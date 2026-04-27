# 🏛️ ForensiX AI — Architecture

This document describes the system architecture, component responsibilities, and design decisions of the ForensiX AI deepfake detection platform.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Browser (Client)                            │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    React 19 + Vite 7                         │    │
│  │                                                               │    │
│  │  ┌───────────────┐  ┌────────────────┐  ┌────────────────┐  │    │
│  │  │   Auth.jsx    │  │    App.jsx     │  │ webauthn_client│  │    │
│  │  │ Split-screen  │  │ Dashboard /    │  │    .js         │  │    │
│  │  │ login/signup  │  │ History / Upload│  │ Passkey helpers│  │    │
│  │  │ Mandatory 2FA │  │ Video analysis │  │                │  │    │
│  │  └───────────────┘  └────────────────┘  └────────────────┘  │    │
│  │              │               │                  │             │    │
│  │              └───────────────┴──────────────────┘             │    │
│  │                       HTTP / Fetch API                         │    │
│  └─────────────────────────────────────────────────────────────┘    │
└────────────────────────────────┬────────────────────────────────────┘
                                  │ HTTP (JSON + Multipart)
                                  │ JWT Bearer Auth
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI / Python)                        │
│                                                                       │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  ┌───────────┐  │
│  │   main.py   │  │  auth_utils  │  │ database.py│  │ models.py │  │
│  │             │  │  .py         │  │            │  │           │  │
│  │ All routes  │  │ bcrypt / JWT │  │ Motor async│  │ Pydantic  │  │
│  │ CORS config │  │ WebAuthn     │  │ auto-recon │  │ schemas   │  │
│  │ Global err  │  │ options/     │  │ nect logic │  │           │  │
│  │ handler     │  │ verify       │  │            │  │           │  │
│  └──────┬──────┘  └──────────────┘  └─────┬──────┘  └───────────┘  │
│         │                                   │                        │
│         ▼                                   ▼                        │
│  ┌─────────────┐                    ┌──────────────┐                 │
│  │ inference.py│                    │   MongoDB    │                 │
│  │             │                    │   (Motor)    │                 │
│  │ VisionMamba │                    │              │                 │
│  │ Lite model  │                    │ users coll.  │                 │
│  │ PyTorch     │                    │ analyses coll│                 │
│  └─────────────┘                    └──────────────┘                 │
│         │                                                            │
│         ▼                                                            │
│  ┌─────────────┐                                                     │
│  │model.safe   │                                                     │
│  │tensors      │                                                     │
│  │(378 KB)     │                                                     │
│  └─────────────┘                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Frontend — `frontend/src/`

#### `App.jsx` — Main Application Shell
- Manages global application state: `token`, `result`, `history`, `viewMode`, `file`
- **Navigation**: toggle between Upload and History views
- **Video Upload**: drag-and-drop + file picker, sends `POST /upload-video` with JWT
- **Results Display**: confidence gauge, stats grid, frame-level timeline chart, prediction badge
- **History Dashboard**: paginated card grid; each card shows filename, prediction badge, confidence, frame stats
- **History Actions**:
  - ⬇️ Download: `GET /video/{id}` → `fetch()` → `Blob` → `createObjectURL` → programmatic `<a>` click
  - 🗑️ Delete: `DELETE /history/{id}` → `window.confirm()` guard → refresh history list
- **Download guard**: download button only renders if `item.saved_video_path` is truthy (hides for pre-feature records)

#### `components/Auth.jsx` — Authentication Flow
- **States**: `isLogin`, `justSignedUp`, `awaiting2FA`, `loading`, `error`
- **Signup flow**:
  1. POST `/auth/signup` → auto POST `/auth/login` → store temp JWT
  2. `justSignedUp = true` → renders forced biometric registration screen (no skip)
  3. `GET /auth/register/options` + `startRegistration()` + `POST /auth/register/verify` → `onLogin()`
- **Login flow (strict 2FA)**:
  1. Password empty guard: shows `"Please enter the password"` error, does not proceed
  2. POST `/auth/login` → password verified
  3. `awaiting2FA = true` → renders "Verify Biometrics" loading screen
  4. Automatically calls `loginWithBiometrics(username)` — GET options + `startAuthentication()` + POST verify
  5. Only if biometric succeeds: `localStorage.setItem('token', ...)` → `onLogin()`
- **Split-screen layout**: brand banner (left panel) + glass form card (right panel), responsive stacks on mobile

#### `utils/webauthn_client.js` — Browser Passkey Helpers
- `registerBiometrics()`: fetches registration options, calls `@simplewebauthn/browser`'s `startRegistration()`, posts result for server verification
- `loginWithBiometrics(username)`: fetches challenge, calls `startAuthentication()`, posts for verification, returns JWT data

---

### 2. Backend — `backend/`

#### `main.py` — FastAPI Application
- All HTTP routes defined here
- **Startup lifecycle**: `connect_to_mongo()` → `load_model()` (loads `model.safetensors` into PyTorch)
- **ThreadPoolExecutor(max_workers=4)**: frame analysis runs off the async event loop to avoid blocking
- **Global exception handler**: catches unhandled 500s, prints stack trace, injects CORS headers into error responses
- **Key route logic**:
  - `POST /upload-video`: saves file as `uploads/{uuid4}{ext}`, extracts frames at 5 FPS, runs parallel frame analysis, aggregates, saves analysis document with `saved_video_path`
  - `GET /video/{id}`: finds document, checks `saved_video_path` exists on filesystem, returns `FileResponse`
  - `DELETE /history/{id}`: finds document, `Path.unlink()` the video file, `delete_one()` from MongoDB
  - WebAuthn endpoints: challenges stored as hex strings in MongoDB; credential IDs stored as hex; login verify converts incoming base64url to hex for matching

#### `auth_utils.py` — Auth Helpers
- `hash_password()` / `verify_password()`: bcrypt with UTF-8 encoding
- `create_access_token()`: HS256 JWT, 24-hour expiry, timezone-aware datetime
- `get_registration_options()`: PLATFORM authenticator, user verification REQUIRED, excludes already-registered credentials to prevent duplicate registration
- `get_authentication_options()`: builds allow-list from stored hex credential IDs
- `RP_ID = "localhost"`, `ORIGIN = "http://localhost:3000"` — change for production deployment

#### `database.py` — MongoDB Connection
- Async Motor client with `serverSelectionTimeoutMS=5000`
- `ensure_connected()`: ping-based health check with auto-reconnect fallback
- `get_database()`: raises `HTTP 503` if database is unreachable — prevents silent failures that caused the original 500 errors

#### `models.py` — Pydantic Schemas
- `AnalysisResultDB`: full document schema including `saved_video_path: Optional[str]`
- `AnalysisHistoryResponse`: API response shape, includes `saved_video_path` so frontend can decide whether to show the download button
- `UserDB`: user document including `credentials: List[dict]` for WebAuthn passkeys
- `WebAuthnLoginVerifyRequest`: `{username: str, response: dict}`

---

### 3. AI Model — `inference.py` + `model.safetensors`

#### VisionMambaLite Architecture
```
Input: RGB frame (224×224×3)
  ↓
Conv2d(3→32, 3×3, stride=2) + BatchNorm2d + ReLU     → 112×112×32
  ↓
Conv2d(32→64, 3×3, stride=2) + BatchNorm2d + ReLU    → 56×56×64
  ↓
Conv2d(64→128, 3×3, stride=2) + BatchNorm2d + ReLU   → 28×28×128
  ↓
AdaptiveAvgPool2d(1)                                  → 1×1×128
  ↓
Linear(128→1) + Sigmoid                               → score ∈ [0, 1]
```

- Model weights: `model.safetensors` (≈ 379 KB)
- Preprocessing: BGR → RGB, resize to 224×224, ImageNet normalization
- Inference: `@torch.no_grad()` for efficiency
- Output: single float — higher = more likely fake

---

### 4. Database Schema — MongoDB

**Collection: `users`**
```json
{
  "_id": ObjectId,
  "username": "string",
  "hashed_password": "bcrypt hash",
  "created_at": ISODate,
  "credentials": [
    {
      "credential_id": "hex string",
      "public_key": [/* byte array */],
      "sign_count": 42,
      "created_at": ISODate
    }
  ],
  "current_challenge": "hex string (temporary, cleared after verify)"
}
```

**Collection: `analyses`**
```json
{
  "_id": ObjectId,
  "filename": "video.mp4",
  "file_size": 10485760,
  "upload_timestamp": ISODate,
  "prediction": "DEEPFAKE | REAL | UNCERTAIN",
  "confidence": 0.87,
  "mean_score": 0.82,
  "total_frames": 150,
  "fake_frames": 130,
  "real_frames": 10,
  "uncertain_frames": 10,
  "frame_predictions": [
    { "frame_number": 0, "timestamp": 0.0, "score": 0.91, "prediction": "FAKE" }
  ],
  "processing_time": 12.4,
  "saved_video_path": "uploads/3f2a1b4c-....mp4"
}
```

---

## Security Architecture

| Layer | Mechanism | Notes |
|---|---|---|
| **Transport** | HTTPS (production) | HTTP in local dev |
| **Authentication Factor 1** | bcrypt password | 24-hour JWT issued after success |
| **Authentication Factor 2** | WebAuthn FIDO2 | Platform authenticator, UV=REQUIRED |
| **Session Token** | HS256 JWT | Stored in `localStorage`, sent as Bearer token |
| **CORS** | Permissive (`*`) in dev | Restrict to frontend origin in production |
| **Error Responses** | CORS headers injected | Ensures browser can read error details |
| **DB Errors** | HTTP 503 returned | Never silently swallowed |

---

## Thresholds & Configuration

| Variable | Value | Description |
|---|---|---|
| `DEFAULT_FPS` | 5 | Frames extracted per second |
| `FAKE_THRESHOLD` | 0.65 | Score above this = FAKE |
| `REAL_THRESHOLD` | 0.35 | Score below this = REAL |
| `MAX_FILE_SIZE` | 500 MB | Maximum upload size |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 1440 (24h) | JWT lifetime |
| `MONGODB_URL` | `mongodb://localhost:27017` | Override via env var |
| `DATABASE_NAME` | `deepfake_detector` | Override via env var |
| `RP_ID` | `localhost` | WebAuthn Relying Party ID |
| `ORIGIN` | `http://localhost:3000` | WebAuthn expected origin |
