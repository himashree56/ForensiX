# 🏗️ Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                    (React + TypeScript)                          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Upload     │  │   Progress   │  │   Results    │          │
│  │  Component   │  │   Tracker    │  │   Display    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API LAYER                                │
│                        (FastAPI)                                 │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   /health    │  │ /upload-video│  │     CORS     │          │
│  │   Endpoint   │  │   Endpoint   │  │  Middleware  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                              │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │    Video     │  │    Frame     │  │  Parallel    │          │
│  │  Extraction  │  │  Processing  │  │  Execution   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MODEL LAYER                                 │
│                  (Vision-Mamba Model)                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────┐           │
│  │              PyTorch Model                        │           │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐ │           │
│  │  │    CNN     │→ │   Pooling  │→ │   Linear   │ │           │
│  │  │  Backbone  │  │            │  │    Head    │ │           │
│  │  └────────────┘  └────────────┘  └────────────┘ │           │
│  └──────────────────────────────────────────────────┘           │
│                                                                   │
│  Input: 224x224 RGB → Output: Sigmoid Score [0,1]               │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Video Upload Flow

```
User → Frontend → API → Validation → Temporary Storage
                                            │
                                            ▼
                                    Frame Extraction
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │ Frame Queue  │
                                    └──────────────┘
                                            │
                        ┌───────────────────┼───────────────────┐
                        ▼                   ▼                   ▼
                   Worker 1            Worker 2            Worker 3
                        │                   │                   │
                        └───────────────────┼───────────────────┘
                                            ▼
                                    Aggregate Results
                                            │
                                            ▼
                                    Return to Frontend
```

### 2. Frame Processing Pipeline

```
Video File
    │
    ▼
Extract Frames (OpenCV)
    │
    ├─→ Frame 0 (t=0.0s)
    ├─→ Frame 1 (t=0.2s)
    ├─→ Frame 2 (t=0.4s)
    └─→ ...
         │
         ▼
Preprocess Each Frame
    │
    ├─→ Resize to 224x224
    ├─→ Convert BGR → RGB
    ├─→ Normalize (ImageNet)
    └─→ Convert to Tensor
         │
         ▼
Model Inference
    │
    ├─→ Forward Pass
    ├─→ Apply Sigmoid
    └─→ Get Score [0,1]
         │
         ▼
Classify Frame
    │
    ├─→ score ≥ 0.65 → FAKE
    ├─→ score ≤ 0.35 → REAL
    └─→ else → UNCERTAIN
         │
         ▼
Aggregate All Frames
    │
    ├─→ Mean Score
    ├─→ Count Predictions
    └─→ Final Decision
         │
         ▼
Return Results
```

## Component Details

### Frontend Components

#### 1. Upload Component
- **Purpose**: Handle video file selection
- **Features**:
  - Drag-and-drop support
  - File validation
  - Visual feedback
- **State**: `file`, `isDragging`, `error`

#### 2. Progress Tracker
- **Purpose**: Show analysis progress
- **Features**:
  - Animated progress bar
  - Status messages
  - Percentage display
- **State**: `progress`, `isAnalyzing`

#### 3. Results Display
- **Purpose**: Visualize analysis results
- **Features**:
  - Prediction badge
  - Confidence score
  - Statistics grid
  - Frame timeline
- **State**: `result`

### Backend Components

#### 1. API Server (main.py)
- **Framework**: FastAPI
- **Port**: 8000
- **Features**:
  - Auto-generated OpenAPI docs
  - CORS middleware
  - Request validation
  - Error handling

#### 2. Video Processor
- **Library**: OpenCV (cv2)
- **Functions**:
  - `extract_frames()`: Extract frames at specified FPS
  - `analyze_frame()`: Process single frame
  - `aggregate_predictions()`: Combine results

#### 3. Model Inference (inference.py)
- **Framework**: PyTorch
- **Model**: VisionMambaLite
- **Functions**:
  - `load_model()`: Load model at startup
  - `predict_frame()`: Inference on single frame

## Technology Stack

### Frontend
```
React 18.3.1
├── TypeScript 5.6.2
├── Vite 7.3.1
└── CSS Variables (Design System)
```

### Backend
```
Python 3.10+
├── FastAPI 0.109.0
├── Uvicorn 0.27.0
├── PyTorch 2.1.2
├── OpenCV 4.9.0
└── Safetensors 0.4.1
```

### DevOps
```
Docker 20.10+
├── Docker Compose 2.0+
├── Nginx (Frontend)
└── Multi-stage builds
```

## Performance Characteristics

### Backend Performance

| Metric | Value | Notes |
|--------|-------|-------|
| Model Load Time | ~2-5s | One-time at startup |
| Frame Extraction | ~0.1s/frame | Depends on video codec |
| Inference Time | ~10-50ms/frame | CPU: 50ms, GPU: 10ms |
| Total Processing | ~5-30s | For 30s video at 5 FPS |

### Frontend Performance

| Metric | Value | Notes |
|--------|-------|-------|
| Initial Load | <1s | With code splitting |
| Bundle Size | ~200KB | Minified + gzipped |
| Time to Interactive | <2s | On 3G connection |
| Lighthouse Score | 90+ | Performance metric |

## Scalability Considerations

### Horizontal Scaling

```
                    ┌─────────────┐
                    │Load Balancer│
                    └─────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌─────────┐        ┌─────────┐        ┌─────────┐
   │Backend 1│        │Backend 2│        │Backend 3│
   └─────────┘        └─────────┘        └─────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                    ┌─────────────┐
                    │Shared Model │
                    │   Storage   │
                    └─────────────┘
```

### Vertical Scaling

- **CPU**: 2-4 cores minimum
- **RAM**: 2-4 GB minimum
- **GPU**: Optional (10x speedup)
- **Storage**: 1 GB for model + temp files

## Security Architecture

### Frontend Security
- Input validation
- File type checking
- Size limits
- XSS prevention
- HTTPS enforcement

### Backend Security
- CORS configuration
- Request validation (Pydantic)
- File sanitization
- Rate limiting
- Error message sanitization

### Network Security
```
Internet
    │
    ▼
┌─────────────┐
│   Firewall  │
└─────────────┘
    │
    ▼
┌─────────────┐
│     WAF     │
└─────────────┘
    │
    ▼
┌─────────────┐
│Load Balancer│
└─────────────┘
    │
    ▼
Application Servers
```

## Monitoring & Logging

### Metrics to Track

1. **API Metrics**
   - Request count
   - Response time
   - Error rate
   - Success rate

2. **Model Metrics**
   - Inference time
   - Prediction distribution
   - Confidence scores

3. **System Metrics**
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network traffic

### Logging Strategy

```python
# Application Logs
INFO: Video uploaded - size: 50MB
INFO: Extracted 150 frames
INFO: Analysis complete - prediction: FAKE (85%)

# Error Logs
ERROR: Failed to extract frames - corrupted video
ERROR: Model inference failed - out of memory

# Performance Logs
PERF: Frame extraction: 2.3s
PERF: Model inference: 15.2s
PERF: Total processing: 18.1s
```

## Deployment Architecture

### Development
```
localhost:3000 (Frontend)
    │
    └─→ localhost:8000 (Backend)
```

### Production
```
CDN (Static Assets)
    │
    ▼
users.example.com (Frontend)
    │
    └─→ api.example.com (Backend)
            │
            └─→ Model Storage (S3/GCS)
```

## Future Enhancements

1. **Batch Processing**
   - Process multiple videos
   - Queue management
   - Background jobs

2. **Advanced Analytics**
   - Temporal analysis
   - Face detection
   - Audio analysis

3. **User Management**
   - Authentication
   - Usage tracking
   - API keys

4. **Model Improvements**
   - Ensemble models
   - Real-time processing
   - Edge deployment

---

**Last Updated**: 2026-02-01
