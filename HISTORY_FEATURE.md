# 📜 History Feature - Quick Start Guide

## Overview

The deepfake detector now includes a **complete history tracking system** that saves all analysis results to MongoDB and allows you to view and reload previous analyses.

## Features

✅ **Automatic Saving**: Every video analysis is automatically saved  
✅ **History View**: Browse all previous analyses in a beautiful card layout  
✅ **One-Click Load**: Click any history card to view its full analysis  
✅ **Visual Breakdown**: See Real/Uncertain/Fake distribution at a glance  
✅ **Detailed Stats**: Confidence, frame count, file size, processing time  
✅ **Works Offline**: App functions without MongoDB (history disabled)  

## Quick Start

### 1. Install MongoDB (Optional but Recommended)

**Easiest Method - Using Docker:**
```bash
docker run -d --name deepfake-mongodb -p 27017:27017 mongo:7.0
```

**Alternative Methods:**
- See `MONGODB_SETUP.md` for detailed installation instructions
- Download from: https://www.mongodb.com/try/download/community

### 2. Start the Application

**Option A: Using the startup script**
```bash
start.bat
```

**Option B: Manual start**
```bash
# Terminal 1 - Backend
cd backend
.\\venv\\Scripts\\activate
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 3. Use History Features

1. **Upload and analyze a video** (this saves it to history)
2. **Click "📜 View History"** button
3. **Click any history card** to reload that analysis
4. **View all forensic visualizations** for historical data

## What Gets Saved?

Each analysis saves:
- Video filename and file size
- Upload timestamp
- Overall prediction (REAL/FAKE/UNCERTAIN)
- Confidence score
- Mean score across all frames
- Frame counts (total, fake, real, uncertain)
- Processing time
- **All frame-by-frame predictions** (for full forensic analysis)

## History Card Information

Each card displays:
- 🎬 **Filename**: Original video name
- **Prediction Badge**: Color-coded REAL/FAKE/UNCERTAIN
- **Confidence**: Percentage confidence in prediction
- **Frames**: Total number of frames analyzed
- **Size**: File size in MB
- **Date**: When the analysis was performed
- **Processing Time**: How long the analysis took
- **Breakdown Bar**: Visual distribution of Real/Uncertain/Fake frames

## API Endpoints

### Get History List
```bash
GET /history?limit=20&skip=0
```

### Get Specific Analysis
```bash
GET /history/{analysis_id}
```

## Without MongoDB

If MongoDB is not installed or not running:
- ✅ Video analysis works normally
- ✅ Results displayed immediately
- ⚠️ History button shows empty state
- ⚠️ Data not persisted between sessions
- ⚠️ Console shows warning message

## Troubleshooting

### "No Analysis History" message
- **Cause**: No videos have been analyzed yet, or MongoDB is not connected
- **Solution**: Upload and analyze a video, or check MongoDB connection

### "Failed to connect to MongoDB" in console
- **Cause**: MongoDB is not running
- **Solution**: Start MongoDB (see MONGODB_SETUP.md)
- **Note**: App will still work without history features

### History cards not loading
- **Cause**: MongoDB connection issue
- **Solution**: Check MongoDB is running on port 27017
- **Test**: Run `mongosh` in terminal to verify connection

## Viewing Data in MongoDB

### Using MongoDB Compass (GUI)
1. Download: https://www.mongodb.com/try/download/compass
2. Connect to: `mongodb://localhost:27017`
3. Database: `deepfake_detector`
4. Collection: `analyses`

### Using mongosh (CLI)
```bash
mongosh
use deepfake_detector
db.analyses.find().pretty()
```

## Technical Details

- **Database**: MongoDB 7.0
- **Driver**: Motor 3.3.2 (async Python driver)
- **Collection**: `analyses`
- **Connection**: `mongodb://localhost:27017`
- **Database Name**: `deepfake_detector`

## Files Modified

### Backend:
- `backend/database.py` - MongoDB connection
- `backend/models.py` - Data models
- `backend/main.py` - History endpoints
- `backend/requirements.txt` - Added motor, pymongo

### Frontend:
- `frontend/src/App.tsx` - History UI and logic
- `frontend/src/index.css` - History styles

### Configuration:
- `docker-compose.yml` - MongoDB service
- `start.bat` - Startup script with MongoDB env vars

## Next Steps

1. **Try it out**: Analyze a few videos and view the history
2. **Explore MongoDB**: Use Compass to see the saved data
3. **Read docs**: Check `MONGODB_INTEGRATION.md` for full details
4. **Optional enhancements**: See "Next Steps" in MONGODB_INTEGRATION.md

## Support

- **MongoDB Setup**: See `MONGODB_SETUP.md`
- **Full Documentation**: See `MONGODB_INTEGRATION.md`
- **Docker Setup**: See `docker-compose.yml`

---

**🎉 Enjoy your new history tracking feature!**
