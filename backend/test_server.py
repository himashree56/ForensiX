"""
Quick Test Server - MongoDB History Only
This bypasses the slow model loading to test the history feature
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
from datetime import datetime
import uvicorn

app = FastAPI(title="Deepfake Detector - Quick Test")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "deepfake_detector"
client = None
database = None

@app.on_event("startup")
async def startup():
    global client, database
    try:
        client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        database = client[DATABASE_NAME]
        await client.admin.command('ping')
        print(f"✓ Connected to MongoDB at {MONGODB_URL}")
    except Exception as e:
        print(f"⚠ MongoDB connection failed: {e}")

@app.on_event("shutdown")
async def shutdown():
    if client:
        client.close()

@app.get("/health")
async def health():
    return {"status": "ok", "mongodb": database is not None}

@app.get("/history")
async def get_history(limit: int = 50, skip: int = 0):
    """Get analysis history"""
    try:
        if database is None:
            return []
        
        cursor = database.analyses.find().sort("upload_timestamp", -1).skip(skip).limit(limit)
        analyses = await cursor.to_list(length=limit)
        
        history = []
        for analysis in analyses:
            history.append({
                "id": str(analysis['_id']),
                "filename": analysis['filename'],
                "file_size": analysis['file_size'],
                "upload_timestamp": analysis['upload_timestamp'].isoformat(),
                "prediction": analysis['prediction'],
                "confidence": analysis['confidence'],
                "mean_score": analysis['mean_score'],
                "total_frames": analysis['total_frames'],
                "fake_frames": analysis['fake_frames'],
                "real_frames": analysis['real_frames'],
                "uncertain_frames": analysis['uncertain_frames'],
                "processing_time": analysis.get('processing_time')
            })
        
        return history
    except Exception as e:
        print(f"Error: {e}")
        return []

@app.get("/history/{analysis_id}")
async def get_analysis_detail(analysis_id: str):
    """Get detailed analysis"""
    try:
        from bson import ObjectId
        
        if database is None:
            return {"error": "Database not connected"}
        
        obj_id = ObjectId(analysis_id)
        analysis = await database.analyses.find_one({"_id": obj_id})
        
        if not analysis:
            return {"error": "Not found"}
        
        return {
            "id": str(analysis['_id']),
            "filename": analysis['filename'],
            "file_size": analysis['file_size'],
            "upload_timestamp": analysis['upload_timestamp'].isoformat(),
            "prediction": analysis['prediction'],
            "confidence": analysis['confidence'],
            "mean_score": analysis['mean_score'],
            "total_frames": analysis['total_frames'],
            "fake_frames": analysis['fake_frames'],
            "real_frames": analysis['real_frames'],
            "uncertain_frames": analysis['uncertain_frames'],
            "processing_time": analysis.get('processing_time'),
            "frame_predictions": analysis['frame_predictions']
        }
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    print("=" * 50)
    print("  Quick Test Server - History Feature Only")
    print("=" * 50)
    print("\nThis server tests MongoDB history without loading the model")
    print("Backend will be available at: http://localhost:8000")
    print("\nPress Ctrl+C to stop\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
