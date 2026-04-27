# 🔬 ForensiX AI — Vision-Mamba Deepfake Detector

> *"Your lens into forensic truth, frame by frame"*

ForensiX AI is a full-stack, AI-powered deepfake detection platform. It analyzes uploaded videos frame-by-frame using a custom **Vision-Mamba Lite** deep learning model and presents forensic-grade results through a premium dark-mode web interface.

The platform is secured by a **mandatory Two-Factor Authentication** system combining traditional password login with **WebAuthn biometrics** (Windows Hello, Touch ID, Face ID).

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎥 **Deepfake Detection** | Analyzes MP4, AVI, MOV, MKV files up to 500 MB |
| 📊 **Frame-Level Forensics** | Per-frame confidence scores with FAKE / REAL / UNCERTAIN classification |
| 📈 **Visual Analytics** | Confidence charts, frame breakdown bars, and summary statistics |
| 📜 **Analysis History** | Persistent per-user history stored in MongoDB |
| ⬇️ **Video Download** | Download originally uploaded videos directly from the history |
| 🗑️ **History Deletion** | Delete individual analysis records and their associated video files |
| 🔐 **Mandatory 2FA Auth** | Password + WebAuthn biometric verification required for every login |
| 👆 **Passkey / Biometrics** | Windows Hello, Touch ID, and FIDO2 hardware keys supported |
| 🌐 **Split-Screen UI** | Premium glassmorphism login page with ForensiX AI branding |

---

## 🏗️ Tech Stack

### Backend
- **FastAPI** (Python) — REST API framework
- **PyTorch** — Inference engine for the Vision-Mamba Lite model
- **OpenCV** — Video frame extraction
- **Motor + MongoDB** — Async database for users and analysis history
- **py-webauthn** — FIDO2 / WebAuthn server-side implementation
- **bcrypt + python-jose** — Password hashing and JWT token management

### Frontend
- **React 19** with **Vite 7** — UI framework and dev server
- **@simplewebauthn/browser** — WebAuthn client for passkey prompts
- **Chart.js** — Confidence and frame analysis charts
- **Vanilla CSS** — Custom dark-mode design system with glassmorphism

### Infrastructure
- **MongoDB** — Primary datastore (local or Atlas)
- **Docker / docker-compose** — Optional containerized deployment

---

## 🚀 Quick Start

> **Full instructions**: see [`SETUP.md`](SETUP.md)

### Prerequisites
- Python 3.10+
- Node.js 20.19+ or 22.12+
- MongoDB running on `localhost:27017`

### 1. Clone the repo
```bash
git clone https://github.com/himashree56/deepfake-detection.git
cd deepfake-detection
```

### 2. Start the application (Windows)
```bat
start.bat
```

This opens two terminal windows:
- **Backend** → `http://localhost:8000`
- **Frontend** → `http://localhost:3000`

### 3. Start MongoDB (required for auth & history)
```powershell
net start MongoDB
# or
mongod --dbpath C:\data\db
```

---

## 🔐 Authentication Flow

ForensiX AI enforces **mandatory Two-Factor Authentication** for all users.

### Signup
1. Enter username and password → click **Create Account**
2. The system auto-logs you in temporarily
3. You are **required** to link your biometric (Windows Hello / Touch ID) — no skip option
4. Access is granted only after successful biometric registration

### Login
1. Enter username and password → click **Authenticate**
2. If password is correct, the system **immediately** triggers your biometric prompt
3. Access is granted only if **both** factors succeed

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | API health and model status |
| `POST` | `/auth/signup` | Register a new user |
| `POST` | `/auth/login` | Password login → returns JWT |
| `GET` | `/auth/register/options` | Get WebAuthn registration challenge |
| `POST` | `/auth/register/verify` | Verify and store biometric credential |
| `GET` | `/auth/login/biometric/options` | Get WebAuthn authentication challenge |
| `POST` | `/auth/login/biometric/verify` | Verify biometric → returns JWT |
| `POST` | `/upload-video` | Upload and analyze a video |
| `GET` | `/history` | List user's analysis history |
| `GET` | `/history/{id}` | Get detailed analysis by ID |
| `DELETE` | `/history/{id}` | Delete analysis record and video file |
| `GET` | `/video/{id}` | Download the original uploaded video |

Interactive docs: `http://localhost:8000/docs`

---

## 📁 Project Structure

```
deepfake-detection/
├── backend/
│   ├── main.py          # FastAPI application, all routes
│   ├── auth_utils.py    # Password, JWT, and WebAuthn helpers
│   ├── database.py      # MongoDB connection with auto-reconnect
│   ├── models.py        # Pydantic DB and response models
│   ├── requirements.txt
│   └── uploads/         # Permanently saved video files
├── frontend/
│   └── src/
│       ├── App.jsx       # Main application, dashboard, history
│       ├── index.css     # Design system (dark mode + glassmorphism)
│       ├── components/
│       │   └── Auth.jsx  # Login, signup, 2FA biometric flow
│       └── utils/
│           └── webauthn_client.js  # Browser-side passkey helpers
├── inference.py          # VisionMambaLite model + frame prediction
├── model.safetensors     # Pretrained model weights
├── start.bat             # Windows one-click launcher
├── docker-compose.yml    # Docker deployment
└── SETUP.md              # Detailed installation guide
```

---

## 🐳 Docker Deployment

```bash
docker-compose up --build
```

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for full production deployment instructions.

---

## 📄 Documentation

| File | Description |
|---|---|
| [`SETUP.md`](SETUP.md) | Full installation and configuration guide |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | System design and component overview |
| [`flow.md`](flow.md) | Data flow diagrams for auth and analysis |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Docker and production deployment |

---

## 📜 License

MIT License — see `LICENSE` for details.
