import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import time

import cv2
import numpy as np
import torch
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Add parent directory to path to import inference module
sys.path.insert(0, str(Path(__file__).parent.parent))
from inference import load_model, predict_frame

# Import database and models
from database import connect_to_mongo, close_mongo_connection, get_database
from models import (
    AnalysisResultDB, 
    FramePredictionDB, 
    AnalysisHistoryResponse,
    AnalysisDetailResponse
)

# Configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
DEFAULT_FPS = 5  # Extract 5 frames per second
FAKE_THRESHOLD = 0.65
REAL_THRESHOLD = 0.35

# Global model instance
model = None
device = None
executor = ThreadPoolExecutor(max_workers=4)

# FastAPI app
app = FastAPI(
    title="Deepfake Detection API",
    description="API for detecting deepfake videos using Vision-Mamba model",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    device: str

class FramePrediction(BaseModel):
    frame_number: int
    timestamp: float
    score: float
    prediction: str

class VideoAnalysisResponse(BaseModel):
    prediction: str
    confidence: float
    mean_score: float
    total_frames: int
    fake_frames: int
    real_frames: int
    uncertain_frames: int
    frame_predictions: List[FramePrediction]

# Startup event
@app.on_event("startup")
async def startup_event():
    """Load model and connect to database on startup"""
    global model, device
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Determine device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading model on device: {device}")
    
    # Load model (change to parent directory where model.safetensors is located)
    try:
        original_dir = os.getcwd()
        parent_dir = Path(__file__).parent.parent
        os.chdir(parent_dir)
        model = load_model(device=device)
        os.chdir(original_dir)
        print("Model loaded successfully")
    except Exception as e:
        print(f"Error loading model: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await close_mongo_connection()
    executor.shutdown(wait=True)
    # Clean up upload directory
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR, ignore_errors=True)

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health and model status"""
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        device=device if device else "unknown"
    )

# Helper functions
def extract_frames(video_path: str, fps: int = DEFAULT_FPS) -> List[tuple]:
    """
    Extract frames from video at specified FPS
    Returns list of (frame_number, timestamp, frame_array) tuples
    """
    frames = []
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError("Could not open video file")
    
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    if video_fps == 0:
        video_fps = 30  # Default fallback
    
    frame_interval = max(1, int(video_fps / fps))
    frame_count = 0
    extracted_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            timestamp = frame_count / video_fps
            frames.append((extracted_count, timestamp, frame))
            extracted_count += 1
        
        frame_count += 1
    
    cap.release()
    return frames

def analyze_frame(frame_data: tuple) -> Dict:
    """Analyze a single frame"""
    frame_number, timestamp, frame = frame_data
    
    try:
        score = predict_frame(frame, model, device=device)
        
        # Determine prediction
        if score >= FAKE_THRESHOLD:
            prediction = "FAKE"
        elif score <= REAL_THRESHOLD:
            prediction = "REAL"
        else:
            prediction = "UNCERTAIN"
        
        return {
            "frame_number": frame_number,
            "timestamp": round(timestamp, 2),
            "score": round(score, 4),
            "prediction": prediction
        }
    except Exception as e:
        print(f"Error analyzing frame {frame_number}: {e}")
        return {
            "frame_number": frame_number,
            "timestamp": round(timestamp, 2),
            "score": 0.5,
            "prediction": "ERROR"
        }

def aggregate_predictions(frame_results: List[Dict]) -> Dict:
    """Aggregate frame-level predictions into video-level decision"""
    if not frame_results:
        raise ValueError("No frames analyzed")
    
    scores = [r["score"] for r in frame_results]
    mean_score = np.mean(scores)
    
    # Count predictions
    fake_count = sum(1 for r in frame_results if r["prediction"] == "FAKE")
    real_count = sum(1 for r in frame_results if r["prediction"] == "REAL")
    uncertain_count = sum(1 for r in frame_results if r["prediction"] == "UNCERTAIN")
    
    # Video-level decision based on mean score and majority voting
    if mean_score >= FAKE_THRESHOLD or fake_count > real_count:
        final_prediction = "DEEPFAKE"
        confidence = mean_score
    elif mean_score <= REAL_THRESHOLD or real_count > fake_count:
        final_prediction = "REAL"
        confidence = 1 - mean_score
    else:
        final_prediction = "UNCERTAIN"
        confidence = 0.5
    
    return {
        "prediction": final_prediction,
        "confidence": round(confidence, 4),
        "mean_score": round(mean_score, 4),
        "total_frames": len(frame_results),
        "fake_frames": fake_count,
        "real_frames": real_count,
        "uncertain_frames": uncertain_count,
        "frame_predictions": frame_results
    }

# Main upload endpoint
@app.post("/upload-video", response_model=VideoAnalysisResponse)
async def analyze_video(file: UploadFile = File(...), fps: int = DEFAULT_FPS):
    """
    Analyze a video for deepfake detection
    
    Args:
        file: Video file to analyze
        fps: Frames per second to extract (default: 5)
    
    Returns:
        Analysis results with prediction and confidence
    """
    start_time = time.time()
    
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate FPS
    if fps < 1 or fps > 30:
        raise HTTPException(status_code=400, detail="FPS must be between 1 and 30")
    
    # Create temporary file
    temp_video_path = UPLOAD_DIR / f"temp_{file.filename}"
    
    try:
        # Save uploaded file
        with open(temp_video_path, "wb") as buffer:
            content = await file.read()
            
            # Check file size
            file_size = len(content)
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
                )
            
            buffer.write(content)
        
        # Extract frames
        print(f"Extracting frames from {file.filename} at {fps} FPS...")
        frames = extract_frames(str(temp_video_path), fps=fps)
        
        if not frames:
            raise HTTPException(status_code=400, detail="No frames could be extracted from video")
        
        print(f"Extracted {len(frames)} frames")
        
        # Analyze frames in parallel
        print("Analyzing frames...")
        loop = asyncio.get_event_loop()
        frame_results = await loop.run_in_executor(
            executor,
            lambda: [analyze_frame(frame_data) for frame_data in frames]
        )
        
        # Aggregate results
        print("Aggregating results...")
        final_result = aggregate_predictions(frame_results)
        
        processing_time = time.time() - start_time
        print(f"Analysis complete: {final_result['prediction']} ({final_result['confidence']:.2%})")
        
        # Save to MongoDB
        try:
            db = get_database()
            if db is not None:
                analysis_doc = AnalysisResultDB(
                    filename=file.filename,
                    file_size=file_size,
                    upload_timestamp=datetime.utcnow(),
                    prediction=final_result['prediction'],
                    confidence=final_result['confidence'],
                    mean_score=final_result['mean_score'],
                    total_frames=final_result['total_frames'],
                    fake_frames=final_result['fake_frames'],
                    real_frames=final_result['real_frames'],
                    uncertain_frames=final_result['uncertain_frames'],
                    frame_predictions=[
                        FramePredictionDB(**fp) for fp in final_result['frame_predictions']
                    ],
                    processing_time=processing_time
                )
                
                result = await db.analyses.insert_one(analysis_doc.dict(by_alias=True, exclude={'id'}))
                print(f"Saved analysis to database with ID: {result.inserted_id}")
        except Exception as db_error:
            print(f"Warning: Failed to save to database: {db_error}")
            # Continue even if database save fails
        
        return VideoAnalysisResponse(**final_result)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing video: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_video_path.exists():
            temp_video_path.unlink()

# History endpoints
@app.get("/history", response_model=List[AnalysisHistoryResponse])
async def get_history(limit: int = 50, skip: int = 0):
    """
    Get analysis history
    
    Args:
        limit: Maximum number of results to return (default: 50)
        skip: Number of results to skip for pagination (default: 0)
    
    Returns:
        List of analysis summaries
    """
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        # Query database, sorted by most recent first
        cursor = db.analyses.find().sort("upload_timestamp", -1).skip(skip).limit(limit)
        analyses = await cursor.to_list(length=limit)
        
        # Convert to response model
        history = []
        for analysis in analyses:
            history.append(AnalysisHistoryResponse(
                id=str(analysis['_id']),
                filename=analysis['filename'],
                file_size=analysis['file_size'],
                upload_timestamp=analysis['upload_timestamp'],
                prediction=analysis['prediction'],
                confidence=analysis['confidence'],
                mean_score=analysis['mean_score'],
                total_frames=analysis['total_frames'],
                fake_frames=analysis['fake_frames'],
                real_frames=analysis['real_frames'],
                uncertain_frames=analysis['uncertain_frames'],
                processing_time=analysis.get('processing_time')
            ))
        
        return history
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")


@app.get("/history/{analysis_id}", response_model=AnalysisDetailResponse)
async def get_analysis_detail(analysis_id: str):
    """
    Get detailed analysis results including frame predictions
    
    Args:
        analysis_id: MongoDB ObjectId of the analysis
    
    Returns:
        Detailed analysis results with frame predictions
    """
    try:
        from bson import ObjectId
        
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        # Validate ObjectId
        try:
            obj_id = ObjectId(analysis_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid analysis ID format")
        
        # Query database
        analysis = await db.analyses.find_one({"_id": obj_id})
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Convert to response model
        return AnalysisDetailResponse(
            id=str(analysis['_id']),
            filename=analysis['filename'],
            file_size=analysis['file_size'],
            upload_timestamp=analysis['upload_timestamp'],
            prediction=analysis['prediction'],
            confidence=analysis['confidence'],
            mean_score=analysis['mean_score'],
            total_frames=analysis['total_frames'],
            fake_frames=analysis['fake_frames'],
            real_frames=analysis['real_frames'],
            uncertain_frames=analysis['uncertain_frames'],
            processing_time=analysis.get('processing_time'),
            frame_predictions=[
                FramePredictionDB(**fp) for fp in analysis['frame_predictions']
            ]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching analysis detail: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching analysis detail: {str(e)}")


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Deepfake Detection API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload": "/upload-video",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
