"""
Database Models for Analysis History
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class FramePredictionDB(BaseModel):
    """Frame prediction model for database"""
    frame_number: int
    timestamp: float
    score: float
    prediction: str


class AnalysisResultDB(BaseModel):
    """Analysis result model for database"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    filename: str
    file_size: int
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    prediction: str
    confidence: float
    mean_score: float
    total_frames: int
    fake_frames: int
    real_frames: int
    uncertain_frames: int
    frame_predictions: List[FramePredictionDB]
    processing_time: Optional[float] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "filename": "video.mp4",
                "file_size": 1024000,
                "prediction": "FAKE",
                "confidence": 0.85,
                "mean_score": 0.75,
                "total_frames": 100,
                "fake_frames": 70,
                "real_frames": 25,
                "uncertain_frames": 5
            }
        }


class AnalysisHistoryResponse(BaseModel):
    """Response model for history list"""
    id: str
    filename: str
    file_size: int
    upload_timestamp: datetime
    prediction: str
    confidence: float
    mean_score: float
    total_frames: int
    fake_frames: int
    real_frames: int
    uncertain_frames: int
    processing_time: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "filename": "video.mp4",
                "file_size": 1024000,
                "upload_timestamp": "2024-01-01T12:00:00",
                "prediction": "FAKE",
                "confidence": 0.85,
                "mean_score": 0.75,
                "total_frames": 100,
                "fake_frames": 70,
                "real_frames": 25,
                "uncertain_frames": 5,
                "processing_time": 15.5
            }
        }


class AnalysisDetailResponse(AnalysisHistoryResponse):
    """Detailed response including frame predictions"""
    frame_predictions: List[FramePredictionDB]
