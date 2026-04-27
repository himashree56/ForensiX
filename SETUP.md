# ⚙️ ForensiX AI — Setup Guide

This guide walks you through setting up and running the ForensiX AI deepfake detection platform from scratch on a local development machine.

---

## Prerequisites

| Tool | Minimum Version | Notes |
|---|---|---|
| **Python** | 3.10+ | 3.11 recommended |
| **Node.js** | 20.19+ or 22.12+ | Required by Vite 7 |
| **npm** | 10+ | Bundled with Node.js |
| **MongoDB** | 6.0+ | Community Edition |
| **Git** | Any | For cloning |

> **GPU (Optional)**: PyTorch defaults to CPU. A CUDA GPU significantly speeds up frame analysis on long videos.

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/himashree56/deepfake-detection.git
cd deepfake-detection
```

---

## Step 2: Set Up MongoDB

MongoDB is required for user authentication and analysis history.

### Windows (Service)
```powershell
# Download and install MongoDB Community from:
# https://www.mongodb.com/try/download/community

# Start as a service
net start MongoDB

# Verify it's running
mongosh --eval "db.adminCommand('ping')"
```

### Windows (Manual)
```powershell
# Create data directory
mkdir C:\data\db

# Start MongoDB
mongod --dbpath C:\data\db
```

### macOS (Homebrew)
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

### Linux
```bash
sudo systemctl start mongod
sudo systemctl enable mongod  # start on boot
```

MongoDB must be accessible at `mongodb://localhost:27017`. This is the default — no configuration needed.

---

## Step 3: Set Up the Backend (Python)

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Backend Dependencies

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | 0.109.0 | REST API framework |
| `uvicorn[standard]` | 0.27.0 | ASGI server |
| `torch` | 2.2.0 | PyTorch inference |
| `torchvision` | 0.17.0 | Image transforms |
| `opencv-python` | 4.9.0.80 | Video frame extraction |
| `safetensors` | 0.4.5 | Load model weights |
| `motor` | 3.3.2 | Async MongoDB driver |
| `pymongo` | 4.6.1 | MongoDB driver |
| `webauthn` | 2.1.0 | FIDO2 / WebAuthn server |
| `bcrypt` | 4.2.1 | Password hashing |
| `python-jose[cryptography]` | 3.3.0 | JWT tokens |
| `pydantic` | 2.5.3 | Data validation |

---

## Step 4: Set Up the Frontend (Node.js)

```bash
cd frontend
npm install
```

---

## Step 5: Run the Application

### Option A — One-Click (Windows only)

From the project root, double-click or run:
```bat
start.bat
```

This opens two terminal windows automatically:
- **Backend**: activates venv and runs `python main.py`
- **Frontend**: runs `npm run dev`

Then wait ~10 seconds for the model to load before opening the browser.

### Option B — Manual (All platforms)

**Terminal 1 — Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

Wait until you see:
```
[SUCCESS] Connected to MongoDB at mongodb://localhost:27017/
Loading model from model.safetensors...
Model loaded successfully on cpu
Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Wait until you see:
```
  VITE v7.x.x  ready in NNN ms
  ➜  Local:   http://localhost:3000/
```

---

## Step 6: Access the Application

| Service | URL |
|---|---|
| **Frontend (App)** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **API Documentation** | http://localhost:8000/docs |

---

## Step 7: Create Your Account

1. Go to `http://localhost:3000`
2. Click **"New Agent? Create Profile →"**
3. Enter a username and password → click **Create Account**
4. You will be automatically prompted to **Link Your Biometrics** — click **"👆 Link Fingerprint / Iris"**
5. Complete the **Windows Hello / Touch ID** prompt
6. You are now logged in to the dashboard

> **Biometric linking is mandatory** — there is no skip option. Login requires both password AND biometrics.

---

## Environment Variables

You can override defaults by setting environment variables before starting the backend:

| Variable | Default | Description |
|---|---|---|
| `MONGODB_URL` | `mongodb://localhost:27017` | MongoDB connection string |
| `DATABASE_NAME` | `deepfake_detector` | MongoDB database name |
| `SECRET_KEY` | `your-secret-key-...` | JWT signing secret — **change in production** |

### Setting on Windows
```powershell
$env:MONGODB_URL = "mongodb://localhost:27017"
$env:SECRET_KEY = "my-super-secret-key"
python main.py
```

### Setting on macOS / Linux
```bash
export MONGODB_URL="mongodb://localhost:27017"
export SECRET_KEY="my-super-secret-key"
python main.py
```

---

## Changing for Production

Before deploying to a public server, update these values in `backend/auth_utils.py`:

```python
RP_ID = "yourdomain.com"          # Your actual domain
ORIGIN = "https://yourdomain.com" # Your frontend URL
```

And set a strong `SECRET_KEY` environment variable.

---

## Docker Setup (Alternative)

If you have Docker installed, you can run the entire stack with:

```bash
docker-compose up --build
```

This starts MongoDB, the FastAPI backend, and the Vite frontend in containers.

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for full Docker and production deployment details.

---

## Troubleshooting

### "Database unavailable" / 503 error
- MongoDB is not running. Start it with `net start MongoDB` (Windows) or `brew services start mongodb-community` (macOS).

### "Model not loaded" / 503 error
- `model.safetensors` is missing from the project root. Ensure it was not excluded from git.

### Biometric prompt not appearing
- WebAuthn requires HTTPS or `localhost`. Ensure you are accessing the app at `http://localhost:3000` (not an IP address or external hostname).
- Windows Hello must be configured in Windows Settings → Accounts → Sign-in options.

### `npm run dev` fails
- Ensure Node.js v20.19+ or v22.12+ is installed: `node --version`
- Delete `node_modules` and run `npm install` again.

### Port already in use
- Backend (8000): `netstat -ano | findstr :8000` → `taskkill /PID <pid> /F`
- Frontend (3000): `netstat -ano | findstr :3000` → `taskkill /PID <pid> /F`

### Old history items have no download button
- Videos analyzed before the download feature was added were automatically deleted. The ⬇️ button only appears for videos saved after this version.
