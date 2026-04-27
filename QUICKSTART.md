# ⚡ Quick Start Guide

Get the Deepfake Detection application running in **5 minutes**!

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.10+** - [Download](https://www.python.org/downloads/)
- ✅ **Node.js 20+** - [Download](https://nodejs.org/)
- ✅ **npm 10+** (comes with Node.js)

**Optional (for Docker deployment):**
- 🐳 **Docker** - [Download](https://www.docker.com/get-started)
- 🐳 **Docker Compose** - Usually included with Docker Desktop

---

## 🚀 Option 1: Quick Start (Recommended)

### Windows

1. **Double-click** `start.bat` in the project root
2. Wait for both servers to start
3. Open your browser to `http://localhost:3000`

### Linux/Mac

1. **Make the script executable:**
   ```bash
   chmod +x start.sh
   ```

2. **Run the script:**
   ```bash
   ./start.sh
   ```

3. Open your browser to `http://localhost:3000`

---

## 🛠️ Option 2: Manual Setup

### Step 1: Start the Backend

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
# Windows:
python -m venv venv
venv\Scripts\activate

# Linux/Mac:
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

✅ Backend running at: `http://localhost:8000`

### Step 2: Start the Frontend

**Open a new terminal window:**

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

✅ Frontend running at: `http://localhost:3000`

---

## 🐳 Option 3: Docker (Production-like)

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

✅ Services:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

**To stop:**
```bash
docker-compose down
```

---

## 🎯 Using the Application

### 1. Upload a Video

- **Drag and drop** a video file onto the upload zone, or
- **Click** "Choose File" to browse for a video

**Supported formats:** MP4, AVI, MOV, MKV (max 500MB)

### 2. Analyze

- Click the **"🚀 Analyze Video"** button
- Wait while the AI processes your video
- Progress bar shows real-time status

### 3. View Results

The analysis will show:
- ✅ **Prediction**: REAL, DEEPFAKE, or UNCERTAIN
- 📊 **Confidence Score**: How confident the model is
- 📈 **Statistics**: Frame counts and scores
- 🎞️ **Frame Timeline**: Per-frame analysis

### 4. Analyze Another Video

Click **"🔄 Analyze Another Video"** to start over

---

## 🧪 Testing the API

### Using the Web Interface

1. Open `http://localhost:8000/docs`
2. Click on **POST /upload-video**
3. Click **"Try it out"**
4. Upload a video file
5. Click **"Execute"**

### Using the Test Script

```bash
# Test health endpoint only
python test_api.py

# Test with a video file
python test_api.py path/to/video.mp4

# Test with custom FPS
python test_api.py path/to/video.mp4 10
```

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Upload video
curl -X POST "http://localhost:8000/upload-video" \
  -F "file=@test_video.mp4" \
  -F "fps=5"
```

---

## 📊 Understanding Results

### Prediction Types

| Prediction | Score Range | Meaning |
|------------|-------------|---------|
| **REAL** | 0.00 - 0.35 | Authentic video |
| **UNCERTAIN** | 0.35 - 0.65 | Unclear/borderline |
| **DEEPFAKE** | 0.65 - 1.00 | Likely manipulated |

### Confidence Score

- **High (80-100%)**: Very confident prediction
- **Medium (50-80%)**: Moderately confident
- **Low (0-50%)**: Low confidence, review manually

### Frame Analysis

Each frame is analyzed individually:
- **Green bars**: Frames classified as REAL
- **Red bars**: Frames classified as FAKE
- **Yellow bars**: Uncertain frames

---

## ⚙️ Configuration

### Adjust Frame Extraction Rate

**Backend** (`backend/main.py`):
```python
DEFAULT_FPS = 5  # Change to extract more/fewer frames
```

Higher FPS = More accurate but slower
Lower FPS = Faster but less detailed

### Change Thresholds

**Backend** (`backend/main.py`):
```python
FAKE_THRESHOLD = 0.65  # Adjust sensitivity
REAL_THRESHOLD = 0.35
```

### Change API URL

**Frontend** (`frontend/.env`):
```env
VITE_API_URL=http://localhost:8000
```

---

## 🔍 Troubleshooting

### Backend won't start

**Problem:** `ModuleNotFoundError` or import errors

**Solution:**
```bash
cd backend
pip install -r requirements.txt --force-reinstall
```

---

**Problem:** `model.safetensors not found`

**Solution:** Ensure `model.safetensors` is in the project root directory

---

### Frontend won't start

**Problem:** `npm install` fails

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

**Problem:** Port 3000 already in use

**Solution:** Edit `frontend/vite.config.ts`:
```typescript
server: {
  port: 3001,  // Change to different port
  ...
}
```

---

### API connection errors

**Problem:** Frontend can't connect to backend

**Solution:**
1. Ensure backend is running on port 8000
2. Check `http://localhost:8000/health` in browser
3. Verify CORS settings in `backend/main.py`

---

**Problem:** CORS errors in browser console

**Solution:** Update `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specific origin
    ...
)
```

---

### Video processing errors

**Problem:** "Could not open video file"

**Solution:**
- Ensure video is not corrupted
- Try converting to MP4 format
- Check file size (must be < 500MB)

---

**Problem:** Analysis is very slow

**Solution:**
- Reduce FPS (default is 5)
- Use shorter videos for testing
- Consider using GPU if available

---

## 📚 Next Steps

Once you have the application running:

1. **Read the full documentation:**
   - [`PROJECT_README.md`](PROJECT_README.md) - Complete project overview
   - [`ARCHITECTURE.md`](ARCHITECTURE.md) - Technical architecture
   - [`DEPLOYMENT.md`](DEPLOYMENT.md) - Production deployment

2. **Explore the API:**
   - Visit `http://localhost:8000/docs` for interactive API docs
   - Try different videos and FPS settings
   - Review the frame-by-frame analysis

3. **Customize the application:**
   - Modify the UI theme in `frontend/src/index.css`
   - Adjust model thresholds in `backend/main.py`
   - Add new features or endpoints

4. **Deploy to production:**
   - Follow the [`DEPLOYMENT.md`](DEPLOYMENT.md) guide
   - Choose your cloud provider (AWS, GCP, Heroku, etc.)
   - Set up monitoring and logging

---

## 💡 Tips & Best Practices

### For Best Results

1. **Use high-quality videos** - Better input = better analysis
2. **Test with known videos** - Verify accuracy with labeled data
3. **Adjust FPS based on video length** - Longer videos need lower FPS
4. **Review uncertain predictions** - Manual review for borderline cases

### Performance Optimization

1. **Use GPU if available** - 10x faster inference
2. **Batch process videos** - Process multiple videos overnight
3. **Cache results** - Store analysis results for future reference
4. **Optimize video encoding** - Use H.264 codec for best compatibility

### Security Considerations

1. **Validate all uploads** - Check file types and sizes
2. **Sanitize filenames** - Prevent directory traversal attacks
3. **Rate limit API** - Prevent abuse and overload
4. **Use HTTPS in production** - Encrypt data in transit

---

## 🆘 Getting Help

### Resources

- 📖 **Documentation**: See `PROJECT_README.md`
- 🏗️ **Architecture**: See `ARCHITECTURE.md`
- 🚀 **Deployment**: See `DEPLOYMENT.md`
- 🐛 **Issues**: Open a GitHub issue

### Common Questions

**Q: Can I use this commercially?**
A: Check the license file for usage terms.

**Q: How accurate is the model?**
A: Accuracy depends on the training data and video quality. Test with your specific use case.

**Q: Can I retrain the model?**
A: This application uses a pre-trained model. Retraining requires the original training pipeline.

**Q: Does it work with images?**
A: Currently designed for videos, but can be adapted for single images.

**Q: Can I process multiple videos at once?**
A: Not in the current version. This is a planned feature for future releases.

---

## ✅ Success Checklist

Before you start analyzing videos, verify:

- [ ] Backend server is running (`http://localhost:8000/health` returns OK)
- [ ] Frontend is accessible (`http://localhost:3000` loads)
- [ ] API docs are available (`http://localhost:8000/docs`)
- [ ] Test video uploads successfully
- [ ] Results display correctly
- [ ] No console errors in browser

---

**🎉 You're all set! Start detecting deepfakes!**

For detailed information, see [`PROJECT_README.md`](PROJECT_README.md)
