# 🔍 Vision-Mamba Deepfake Detection - Full Stack Application

A complete end-to-end web application for detecting deepfake videos using a trained Vision-Mamba model. This production-ready application features a FastAPI backend and a modern React frontend with premium UI/UX.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![React](https://img.shields.io/badge/react-18+-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.109+-green.svg)

## 🌟 Features

### Backend
- ✅ **FastAPI** REST API with automatic OpenAPI documentation
- ✅ **Video Processing** - Supports MP4, AVI, MOV, MKV formats
- ✅ **Configurable Frame Extraction** - Adjustable FPS for analysis
- ✅ **Parallel Processing** - Multi-threaded frame analysis
- ✅ **Frame & Video Level Predictions** - Comprehensive analysis
- ✅ **Health Monitoring** - API health check endpoint
- ✅ **CORS Support** - Ready for frontend integration
- ✅ **Docker Support** - Containerized deployment

### Frontend
- ✨ **Modern React + TypeScript** - Type-safe development
- ✨ **Premium Dark Theme** - Beautiful, professional UI
- ✨ **Drag & Drop Upload** - Intuitive file handling
- ✨ **Real-time Progress** - Visual feedback during analysis
- ✨ **Comprehensive Results** - Detailed visualization with charts
- ✨ **Frame Timeline** - Per-frame analysis breakdown
- ✨ **Responsive Design** - Works on all devices
- ✨ **Smooth Animations** - Polished user experience

## 🏗️ Architecture

```
vision-mamba-deepfake/
├── backend/                 # FastAPI backend
│   ├── main.py             # API server
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Backend container
│   └── README.md           # Backend docs
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.tsx        # Main component
│   │   └── index.css      # Design system
│   ├── Dockerfile         # Frontend container
│   ├── nginx.conf         # Nginx config
│   └── README.md          # Frontend docs
├── model.safetensors      # Trained model weights
├── inference.py           # Model inference logic
├── config.json            # Model configuration
└── docker-compose.yml     # Orchestration
```

## 🚀 Quick Start

### Option 1: Local Development (Recommended for Development)

#### Prerequisites
- Python 3.10+
- Node.js 20+
- npm 10+

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

Backend will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Option 2: Docker Deployment (Recommended for Production)

#### Prerequisites
- Docker
- Docker Compose

#### Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## 📖 Model Information

### Vision-Mamba Deepfake Detection Model

This model detects deepfake content from face images or video frames.

**Input:**
- RGB image (224x224)
- Normalized with ImageNet mean/std

**Output:**
- Sigmoid score ∈ [0,1]
- \>0.65 → FAKE
- <0.35 → REAL

**Architecture:**
- Lightweight CNN backbone
- Vision-Mamba–style gated head
- Trained on DFDC face crops

## 🔧 API Documentation

### Endpoints

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda"
}
```

#### Upload Video
```http
POST /upload-video
Content-Type: multipart/form-data
```

**Parameters:**
- `file`: Video file (required)
- `fps`: Frames per second to extract (optional, default: 5)

**Response:**
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

## 🎨 Frontend Features

### Upload Interface
- Drag-and-drop video upload
- File validation (format and size)
- Visual feedback during upload

### Analysis Progress
- Real-time progress bar
- Status messages for each stage
- Smooth animations

### Results Display
- **Prediction Badge**: Clear REAL/DEEPFAKE/UNCERTAIN indicator
- **Confidence Score**: Visual bar with percentage
- **Statistics Grid**: Total frames, fake/real counts, mean score
- **Frame Timeline**: Detailed per-frame analysis with color coding

### Design System
- **Colors**: Modern purple gradient theme
- **Typography**: Inter font family
- **Animations**: Smooth transitions and micro-interactions
- **Responsive**: Mobile-first design

## ⚙️ Configuration

### Backend Configuration

Edit `backend/main.py`:

```python
DEFAULT_FPS = 5              # Frames per second to extract
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
FAKE_THRESHOLD = 0.65        # Score threshold for FAKE
REAL_THRESHOLD = 0.35        # Score threshold for REAL
```

### Frontend Configuration

Edit `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

## 🧪 Testing

### Test Backend

```bash
# Using curl
curl -X POST "http://localhost:8000/upload-video" \
  -F "file=@test_video.mp4" \
  -F "fps=5"

# Using Python
import requests

with open('test_video.mp4', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload-video',
        files={'file': f},
        data={'fps': 5}
    )
    print(response.json())
```

### Test Frontend

1. Open `http://localhost:3000`
2. Upload a test video
3. Wait for analysis
4. Review results

## 📊 Performance Considerations

### Backend Optimization
- Model loaded once at startup (not per request)
- Parallel frame processing with ThreadPoolExecutor
- Efficient video frame extraction with OpenCV
- Automatic cleanup of temporary files

### Frontend Optimization
- Code splitting with Vite
- Lazy loading of components
- Optimized re-renders with React hooks
- CSS animations using transforms (GPU accelerated)

## 🔒 Security

- File type validation
- File size limits
- CORS configuration
- Input sanitization
- Error handling and logging

## 🚢 Deployment

### Production Checklist

#### Backend
- [ ] Set proper CORS origins (not `*`)
- [ ] Configure file size limits
- [ ] Set up logging and monitoring
- [ ] Use production ASGI server (Gunicorn + Uvicorn)
- [ ] Enable HTTPS
- [ ] Set up rate limiting

#### Frontend
- [ ] Build production bundle (`npm run build`)
- [ ] Configure API URL for production
- [ ] Enable HTTPS
- [ ] Set up CDN for static assets
- [ ] Configure caching headers

### Cloud Deployment Options

#### AWS
- **Backend**: ECS/Fargate or EC2
- **Frontend**: S3 + CloudFront
- **Database**: RDS (if needed)

#### Google Cloud
- **Backend**: Cloud Run or GKE
- **Frontend**: Cloud Storage + CDN
- **Database**: Cloud SQL (if needed)

#### Azure
- **Backend**: Container Instances or AKS
- **Frontend**: Static Web Apps
- **Database**: Azure Database (if needed)

#### Heroku
```bash
# Backend
heroku create deepfake-api
heroku container:push web -a deepfake-api
heroku container:release web -a deepfake-api

# Frontend
heroku create deepfake-frontend
# Deploy using buildpack
```

## 🐛 Troubleshooting

### Backend Issues

**Model not loading:**
- Ensure `model.safetensors` is in the correct location
- Check Python version (3.10+)
- Verify all dependencies are installed

**CUDA errors:**
- Install CUDA toolkit if using GPU
- Or set device to "cpu" in code

**Video processing errors:**
- Ensure OpenCV is properly installed
- Check video file is not corrupted
- Verify video codec is supported

### Frontend Issues

**API connection failed:**
- Ensure backend is running on port 8000
- Check CORS configuration
- Verify API URL in `.env`

**Build errors:**
- Clear node_modules and reinstall
- Check Node.js version (20+)
- Update npm to latest version

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.

## 🙏 Acknowledgments

- Vision-Mamba model architecture
- DFDC dataset for training
- FastAPI framework
- React and Vite communities

---

**Built with ❤️ for detecting deepfakes and protecting digital authenticity**
