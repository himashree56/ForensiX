# 📁 Project Structure

Complete file structure of the Deepfake Detection application.

```
vision-mamba-deepfake/
│
├── 📄 README.md                    # Original model documentation
├── 📄 PROJECT_README.md            # Complete project documentation
├── 📄 QUICKSTART.md                # Quick start guide (START HERE!)
├── 📄 ARCHITECTURE.md              # Technical architecture details
├── 📄 DEPLOYMENT.md                # Production deployment guide
├── 📄 .gitignore                   # Git ignore rules
│
├── 🐳 docker-compose.yml           # Docker orchestration
├── 🚀 start.bat                    # Windows quick start script
├── 🚀 start.sh                     # Linux/Mac quick start script
├── 🧪 test_api.py                  # API testing script
│
├── 🤖 Model Files
│   ├── model.safetensors           # Trained model weights (379 KB)
│   ├── inference.py                # Model inference logic
│   └── config.json                 # Model configuration
│
├── 🔧 backend/                     # FastAPI Backend
│   ├── main.py                     # API server (core application)
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Backend container
│   └── README.md                   # Backend documentation
│
└── 🎨 frontend/                    # React Frontend
    ├── src/
    │   ├── App.tsx                 # Main React component
    │   ├── index.css               # Complete design system
    │   ├── App.css                 # Component styles (empty)
    │   └── main.tsx                # Application entry point
    │
    ├── public/                     # Static assets
    │   └── vite.svg                # Vite logo
    │
    ├── node_modules/               # Dependencies (auto-generated)
    │
    ├── 📦 Configuration Files
    │   ├── package.json            # NPM dependencies
    │   ├── package-lock.json       # Dependency lock file
    │   ├── vite.config.ts          # Vite configuration
    │   ├── tsconfig.json           # TypeScript config
    │   ├── tsconfig.app.json       # App TypeScript config
    │   ├── tsconfig.node.json      # Node TypeScript config
    │   └── eslint.config.js        # ESLint configuration
    │
    ├── 🐳 Deployment Files
    │   ├── Dockerfile              # Frontend container
    │   └── nginx.conf              # Nginx configuration
    │
    ├── ⚙️ Environment
    │   ├── .env                    # Environment variables
    │   └── .gitignore              # Frontend git ignore
    │
    ├── index.html                  # HTML entry point
    └── README.md                   # Frontend documentation
```

## 📊 File Statistics

### Backend
- **Total Files**: 4
- **Lines of Code**: ~350
- **Main Language**: Python
- **Framework**: FastAPI

### Frontend
- **Total Files**: 16 (excluding node_modules)
- **Lines of Code**: ~1,200
- **Main Language**: TypeScript
- **Framework**: React + Vite

### Documentation
- **Total Docs**: 7 markdown files
- **Total Words**: ~8,000
- **Coverage**: Setup, Architecture, Deployment, API

## 🎯 Key Files to Know

### For Users
1. **`QUICKSTART.md`** - Start here for setup instructions
2. **`PROJECT_README.md`** - Complete project overview
3. **`start.bat` / `start.sh`** - One-click startup scripts

### For Developers
1. **`backend/main.py`** - Backend API implementation
2. **`frontend/src/App.tsx`** - Frontend React component
3. **`frontend/src/index.css`** - Design system and styles
4. **`ARCHITECTURE.md`** - Technical architecture

### For DevOps
1. **`docker-compose.yml`** - Container orchestration
2. **`backend/Dockerfile`** - Backend container
3. **`frontend/Dockerfile`** - Frontend container
4. **`DEPLOYMENT.md`** - Deployment guide

## 📝 Documentation Hierarchy

```
Start Here
    │
    ├─→ QUICKSTART.md (5 min read)
    │   └─→ Get app running immediately
    │
    ├─→ PROJECT_README.md (15 min read)
    │   ├─→ Features overview
    │   ├─→ API documentation
    │   └─→ Configuration options
    │
    ├─→ ARCHITECTURE.md (20 min read)
    │   ├─→ System design
    │   ├─→ Data flow
    │   └─→ Performance metrics
    │
    └─→ DEPLOYMENT.md (30 min read)
        ├─→ Local deployment
        ├─→ Docker deployment
        └─→ Cloud deployment (AWS, GCP, Heroku)
```

## 🔍 File Purposes

### Root Level

| File | Purpose | Size |
|------|---------|------|
| `README.md` | Original model docs | 416 B |
| `PROJECT_README.md` | Main project docs | ~10 KB |
| `QUICKSTART.md` | Quick start guide | ~8 KB |
| `ARCHITECTURE.md` | Architecture docs | ~14 KB |
| `DEPLOYMENT.md` | Deployment guide | ~11 KB |
| `docker-compose.yml` | Container orchestration | 846 B |
| `test_api.py` | API test script | ~4 KB |
| `model.safetensors` | Model weights | 379 KB |
| `inference.py` | Inference logic | ~2 KB |
| `config.json` | Model config | 551 B |

### Backend Files

| File | Purpose | Lines | Complexity |
|------|---------|-------|------------|
| `main.py` | FastAPI server | ~250 | High |
| `requirements.txt` | Dependencies | ~10 | Low |
| `Dockerfile` | Container image | ~30 | Medium |
| `README.md` | Backend docs | ~80 | Low |

### Frontend Files

| File | Purpose | Lines | Complexity |
|------|---------|-------|------------|
| `App.tsx` | Main component | ~350 | High |
| `index.css` | Design system | ~800 | Medium |
| `vite.config.ts` | Build config | ~20 | Low |
| `Dockerfile` | Container image | ~25 | Medium |
| `nginx.conf` | Web server config | ~40 | Medium |

## 🎨 Design System (index.css)

The design system includes:

- **Colors**: 20+ CSS variables
- **Typography**: 8 font sizes
- **Spacing**: 5 spacing scales
- **Components**: 15+ reusable styles
- **Animations**: 10+ keyframe animations
- **Responsive**: Mobile-first breakpoints

## 🔧 Configuration Files

### Backend Configuration
- `requirements.txt` - Python packages
- `Dockerfile` - Container setup
- `main.py` - Runtime config (ports, thresholds)

### Frontend Configuration
- `package.json` - NPM packages
- `vite.config.ts` - Build settings
- `tsconfig.json` - TypeScript settings
- `.env` - Environment variables
- `nginx.conf` - Production server

## 📦 Dependencies

### Backend (Python)
```
fastapi==0.109.0
uvicorn==0.27.0
python-multipart==0.0.6
opencv-python==4.9.0.80
torch==2.1.2
torchvision==0.16.2
numpy==1.26.3
safetensors==0.4.1
pydantic==2.5.3
```

### Frontend (Node.js)
```
react@18.3.1
react-dom@18.3.1
typescript@5.6.2
vite@7.3.1
@vitejs/plugin-react@5.1.2
```

## 🚀 Startup Scripts

### Windows (`start.bat`)
- Creates Python virtual environment
- Installs backend dependencies
- Starts backend server
- Installs frontend dependencies
- Starts frontend dev server

### Linux/Mac (`start.sh`)
- Same as Windows but for Unix systems
- Uses bash instead of batch
- Compatible with multiple terminal emulators

## 🧪 Testing

### Test Script (`test_api.py`)
- Health check test
- Video upload test
- Result validation
- Error handling

### Manual Testing
- Interactive API docs at `/docs`
- Frontend UI testing
- Integration testing

## 📊 Total Project Size

| Category | Size |
|----------|------|
| Model | 379 KB |
| Backend Code | ~15 KB |
| Frontend Code | ~50 KB |
| Dependencies (installed) | ~500 MB |
| Documentation | ~50 KB |
| **Total (without deps)** | **~500 KB** |
| **Total (with deps)** | **~500 MB** |

## 🎯 Quick Reference

### Start Application
```bash
# Windows
start.bat

# Linux/Mac
./start.sh

# Docker
docker-compose up
```

### Access Points
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### Test API
```bash
python test_api.py [video_path] [fps]
```

### Build for Production
```bash
# Backend
docker build -t deepfake-backend -f backend/Dockerfile .

# Frontend
cd frontend && npm run build
```

---

**Last Updated**: 2026-02-01
