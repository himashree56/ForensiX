# Deepfake Detection Backend

FastAPI backend for video deepfake detection using Vision-Mamba model.

## Features

- ✅ Video upload support (.mp4, .avi, .mov, .mkv)
- ✅ Configurable frame extraction (FPS)
- ✅ Parallel frame processing
- ✅ Frame-level and video-level predictions
- ✅ CORS enabled for frontend integration
- ✅ Health check endpoint
- ✅ Automatic cleanup

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Server

```bash
# From the backend directory
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda"
}
```

### Upload Video
```
POST /upload-video
```

Parameters:
- `file`: Video file (multipart/form-data)
- `fps`: Optional, frames per second to extract (default: 5)

Response:
```json
{
  "prediction": "DEEPFAKE",
  "confidence": 0.8234,
  "mean_score": 0.8234,
  "total_frames": 150,
  "fake_frames": 120,
  "real_frames": 25,
  "uncertain_frames": 5,
  "frame_predictions": [
    {
      "frame_number": 0,
      "timestamp": 0.0,
      "score": 0.8456,
      "prediction": "FAKE"
    }
  ]
}
```

## Configuration

Edit these constants in `main.py`:

- `DEFAULT_FPS`: Default frames per second (5)
- `MAX_FILE_SIZE`: Maximum upload size in bytes (500MB)
- `FAKE_THRESHOLD`: Score threshold for FAKE classification (0.65)
- `REAL_THRESHOLD`: Score threshold for REAL classification (0.35)

## API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
