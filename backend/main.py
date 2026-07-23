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

# Load .env file before anything else reads environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / ".env")
except ImportError:
    pass  # python-dotenv not installed — rely on env vars set by host

import cv2
import numpy as np
import torch
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
import traceback
from fastapi.responses import JSONResponse, FileResponse
from fastapi import Request
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
    AnalysisDetailResponse,
    UserDB,
    Token,
    UserResponse,
    SignupRequest,
    LoginRequest,
    WebAuthnRegistrationOptions,
    WebAuthnRegistrationVerifyRequest,
    WebAuthnLoginOptionsRequest,
    WebAuthnLoginVerifyRequest,
)
from auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    get_registration_options,
    get_authentication_options,
    RP_ID,
    ORIGIN,
    SECRET_KEY,
    ALGORITHM,
)
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

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
_frontend_url = os.getenv("FRONTEND_URL", "").rstrip("/")
ALLOW_ORIGINS = list(filter(None, [
    "https://forensi-x.vercel.app",       # production frontend (always allowed)
    _frontend_url if _frontend_url else None,  # from env var if set
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
]))
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"GLOBAL ERROR: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
        headers={"Access-Control-Allow-Origin": "*"} # Force CORS header on 500
    )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    db = get_database()
    user = await db.users.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user

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

# --- Auth Endpoints ---

@app.post("/auth/signup", response_model=UserResponse)
async def signup(request: SignupRequest):
    db = get_database()
    # Check if user exists
    existing_user = await db.users.find_one({"username": request.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create user
    user_db = UserDB(
        username=request.username,
        hashed_password=hash_password(request.password)
    )
    user_dict = user_db.model_dump(by_alias=True, exclude={"id"}) if hasattr(user_db, "model_dump") else user_db.dict(by_alias=True, exclude={"id"})
    
    result = await db.users.insert_one(user_dict)
    return {"id": str(result.inserted_id), "username": request.username}

@app.post("/auth/login", response_model=Token)
async def login(request: LoginRequest):
    db = get_database()
    user = await db.users.find_one({"username": request.username})
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/register/options")
async def register_options(current_user: dict = Depends(get_current_user)):
    from webauthn import options_to_json
    from auth_utils import get_registration_options

    try:
        options = get_registration_options(
            username=current_user["username"],
            user_id=str(current_user["_id"]),
            existing_credentials=current_user.get("credentials", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate options: {str(e)}")

    # Store challenge as hex string in DB
    db = get_database()
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"current_challenge": options.challenge.hex()}}
    )

    import json
    return JSONResponse(content=json.loads(options_to_json(options)))

@app.post("/auth/register/verify")
async def register_verify(request: WebAuthnRegistrationVerifyRequest, current_user: dict = Depends(get_current_user)):
    from webauthn import verify_registration_response, options_to_json
    import json

    db = get_database()
    challenge_hex = current_user.get("current_challenge")
    if not challenge_hex:
        raise HTTPException(status_code=400, detail="Challenge not found. Please request options again.")

    try:
        verification = verify_registration_response(
            credential=request.response,
            expected_challenge=bytes.fromhex(challenge_hex),
            expected_origin=ORIGIN,
            expected_rp_id=RP_ID,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Verification failed: {str(e)}")

    # Store credential — credential_id as hex, public_key as bytes stored in list
    new_credential = {
        "credential_id": verification.credential_id.hex(),
        "public_key": list(verification.credential_public_key),
        "sign_count": verification.sign_count,
        "created_at": datetime.utcnow()
    }

    await db.users.update_one(
        {"_id": current_user["_id"]},
        {
            "$push": {"credentials": new_credential},
            "$unset": {"current_challenge": ""}
        }
    )

    return {"status": "ok"}

@app.get("/auth/login/biometric/options")
async def login_biometric_options(username: str):
    from webauthn import options_to_json
    from auth_utils import get_authentication_options

    db = get_database()
    user = await db.users.find_one({"username": username})
    if not user or not user.get("credentials"):
        raise HTTPException(status_code=400, detail="User not found or no biometrics registered")

    try:
        options = get_authentication_options(user["credentials"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate options: {str(e)}")

    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"current_challenge": options.challenge.hex()}}
    )

    import json
    return JSONResponse(content=json.loads(options_to_json(options)))

@app.post("/auth/login/biometric/verify")
async def login_biometric_verify(request: WebAuthnLoginVerifyRequest):
    from webauthn import verify_authentication_response

    db = get_database()
    user = await db.users.find_one({"username": request.username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    challenge_hex = user.get("current_challenge")
    if not challenge_hex:
        raise HTTPException(status_code=400, detail="Challenge not found")

    import base64
    credential_id_b64 = request.response.get("id")
    
    # Convert base64url to hex to match DB storage
    padding = '=' * (4 - (len(credential_id_b64) % 4)) if credential_id_b64 else ''
    try:
        req_id_hex = base64.urlsafe_b64decode(credential_id_b64 + padding).hex()
    except Exception:
        req_id_hex = credential_id_b64

    db_credential = next(
        (c for c in user["credentials"] if c["credential_id"] == req_id_hex),
        None
    )
    if not db_credential:
        raise HTTPException(status_code=400, detail="Credential not found")

    try:
        verification = verify_authentication_response(
            credential=request.response,
            expected_challenge=bytes.fromhex(challenge_hex),
            expected_rp_id=RP_ID,
            expected_origin=ORIGIN,
            credential_public_key=bytes(db_credential["public_key"]),
            credential_current_sign_count=db_credential["sign_count"],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Verification failed: {str(e)}")

    await db.users.update_one(
        {"_id": user["_id"], "credentials.credential_id": req_id_hex},
        {
            "$set": {"credentials.$.sign_count": verification.new_sign_count},
            "$unset": {"current_challenge": ""}
        }
    )

    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

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
async def analyze_video(
    file: UploadFile = File(...), 
    fps: int = DEFAULT_FPS,
    current_user: dict = Depends(get_current_user)
):
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
    
    import uuid
    saved_video_name = f"{uuid.uuid4()}{file_ext}"
    saved_video_path = UPLOAD_DIR / saved_video_name
    
    try:
        # Save uploaded file
        with open(saved_video_path, "wb") as buffer:
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
        frames = extract_frames(str(saved_video_path), fps=fps)
        
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
                    processing_time=processing_time,
                    saved_video_path=str(saved_video_path)
                )
                
                result = await db.analyses.insert_one(analysis_doc.dict(by_alias=True, exclude={'id'}))
                print(f"Saved analysis to database with ID: {result.inserted_id}")
        except Exception as db_error:
            print(f"Warning: Failed to save to database: {db_error}")
            # Continue even if database save fails
        
        return VideoAnalysisResponse(**final_result)
    
    except HTTPException:
        # If error occurs before saving DB, delete the video
        if 'saved_video_path' in locals() and saved_video_path.exists():
            saved_video_path.unlink()
        raise
    except Exception as e:
        print(f"Error processing video: {e}")
        if 'saved_video_path' in locals() and saved_video_path.exists():
            saved_video_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

# History endpoints
@app.get("/history", response_model=List[AnalysisHistoryResponse])
async def get_history(
    limit: int = 50, 
    skip: int = 0,
    current_user: dict = Depends(get_current_user)
):
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
                processing_time=analysis.get('processing_time'),
                saved_video_path=analysis.get('saved_video_path')
            ))
        
        return history
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching history: {e}")

@app.get("/video/{analysis_id}")
async def get_video(analysis_id: str, current_user: dict = Depends(get_current_user)):
    """Download the original uploaded video"""
    from bson.errors import InvalidId
    from bson import ObjectId
    from fastapi.responses import FileResponse
    db = get_database()
    try:
        doc_id = ObjectId(analysis_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")
        
    analysis = await db.analyses.find_one({"_id": doc_id})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    video_path = analysis.get("saved_video_path")
    if not video_path or not Path(video_path).exists():
        raise HTTPException(status_code=404, detail="Video file not found on server")
        
    return FileResponse(
        path=video_path,
        filename=analysis.get("filename", "video.mp4"),
        media_type="video/mp4"
    )

@app.delete("/history/{analysis_id}")
async def delete_history(analysis_id: str, current_user: dict = Depends(get_current_user)):
    """Delete an analysis record and its associated video file"""
    from bson.errors import InvalidId
    from bson import ObjectId
    db = get_database()
    try:
        doc_id = ObjectId(analysis_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")
        
    analysis = await db.analyses.find_one({"_id": doc_id})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    # Delete the video file if it exists
    video_path = analysis.get("saved_video_path")
    if video_path:
        p = Path(video_path)
        if p.exists():
            try:
                p.unlink()
            except Exception as e:
                print(f"Failed to delete video file {video_path}: {e}")
                
    # Delete from DB
    await db.analyses.delete_one({"_id": doc_id})
    return {"status": "success", "message": "History deleted"}

@app.get("/history/{analysis_id}", response_model=AnalysisDetailResponse)
async def get_analysis_detail(
    analysis_id: str,
    current_user: dict = Depends(get_current_user)
):
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
