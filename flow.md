# 🔁 ForensiX AI — System Flow

This document describes the end-to-end data flows for the two core systems: **Video Analysis** and **Two-Factor Authentication (2FA)**.

---

## 1. 🎥 Video Analysis Flow

```
User (Browser)                 Frontend (React)              Backend (FastAPI)              Model (PyTorch)          MongoDB
     │                               │                              │                            │                       │
     │  Drag/drop or select video    │                              │                            │                       │
     │──────────────────────────────►│                              │                            │                       │
     │                               │  POST /upload-video          │                            │                       │
     │                               │  + JWT Authorization header  │                            │                       │
     │                               │─────────────────────────────►│                            │                       │
     │                               │                              │  Validate JWT              │                       │
     │                               │                              │  Validate file type/size   │                       │
     │                               │                              │  Save to uploads/{uuid}.mp4│                       │
     │                               │                              │─────────────────────────────────────────────────── │
     │                               │                              │  extract_frames()          │                       │
     │                               │                              │  @ DEFAULT_FPS = 5         │                       │
     │                               │                              │                            │                       │
     │                               │                              │  Per frame: predict_frame()│                       │
     │                               │                              │───────────────────────────►│                       │
     │                               │                              │   BGR→RGB resize 224×224   │                       │
     │                               │                              │   ImageNet normalize       │                       │
     │                               │                              │   Conv→BN→ReLU×3           │                       │
     │                               │                              │   AdaptiveAvgPool → Linear │                       │
     │                               │                              │   Sigmoid → score ∈ [0,1]  │                       │
     │                               │                              │◄───────────────────────────│                       │
     │                               │                              │                            │                       │
     │                               │                              │  aggregate_predictions()   │                       │
     │                               │                              │  score > 0.65 → FAKE       │                       │
     │                               │                              │  score < 0.35 → REAL       │                       │
     │                               │                              │  else → UNCERTAIN          │                       │
     │                               │                              │                            │                       │
     │                               │                              │  Save analysis document    │                       │
     │                               │                              │  (includes saved_video_path│                       │
     │                               │                              │───────────────────────────────────────────────────►│
     │                               │                              │                            │                       │
     │                               │  VideoAnalysisResponse       │                            │                       │
     │                               │◄─────────────────────────────│                            │                       │
     │  Display results, charts      │                              │                            │                       │
     │◄──────────────────────────────│                              │                            │                       │
```

### Frame Scoring Logic

| Score Range | Classification |
|---|---|
| `score > 0.65` | **FAKE** |
| `score < 0.35` | **REAL** |
| `0.35 ≤ score ≤ 0.65` | **UNCERTAIN** |

### Video-Level Decision

The final verdict uses **mean score + majority vote**:
- If `mean_score > 0.65` OR `fake_frames > real_frames` → **DEEPFAKE**
- If `mean_score < 0.35` OR `real_frames > fake_frames` → **REAL**
- Otherwise → **UNCERTAIN**

---

## 2. 🔐 Signup + Biometric Registration Flow (2FA Mandatory)

```
User (Browser)              Frontend (React/Auth.jsx)         Backend (FastAPI)               MongoDB
     │                               │                              │                              │
     │  Enter username + password    │                              │                              │
     │  Click "Create Account"       │                              │                              │
     │──────────────────────────────►│                              │                              │
     │                               │  POST /auth/signup           │                              │
     │                               │  {username, password}        │                              │
     │                               │─────────────────────────────►│                              │
     │                               │                              │  Hash password (bcrypt)      │
     │                               │                              │  Insert user document        │
     │                               │                              │─────────────────────────────►│
     │                               │                              │  POST /auth/login (internal) │
     │                               │                              │  Return JWT access_token     │
     │                               │◄─────────────────────────────│                              │
     │                               │                              │                              │
     │  Show "Link Biometrics" screen│                              │                              │
     │◄──────────────────────────────│                              │                              │
     │                               │                              │                              │
     │  Click "Link Fingerprint/Iris"│                              │                              │
     │──────────────────────────────►│                              │                              │
     │                               │  GET /auth/register/options  │                              │
     │                               │  + JWT Authorization         │                              │
     │                               │─────────────────────────────►│                              │
     │                               │                              │  generate_registration_opts()│
     │                               │                              │  Store challenge hex in DB   │
     │                               │                              │─────────────────────────────►│
     │                               │◄─────────────────────────────│                              │
     │  Windows Hello / Touch ID     │                              │                              │
     │  prompt appears               │                              │                              │
     │──────────────────────────────►│                              │                              │
     │  (user scans fingerprint/face)│                              │                              │
     │                               │  POST /auth/register/verify  │                              │
     │                               │  {username, response}        │                              │
     │                               │─────────────────────────────►│                              │
     │                               │                              │  verify_registration_resp()  │
     │                               │                              │  Store credential_id (hex)   │
     │                               │                              │  public_key, sign_count      │
     │                               │                              │─────────────────────────────►│
     │                               │◄─────────────────────────────│                              │
     │  Redirect to Dashboard        │                              │                              │
     │◄──────────────────────────────│                              │                              │
```

---

## 3. 🔑 Login Flow (Mandatory 2FA: Password → Biometrics)

```
User (Browser)              Frontend (React/Auth.jsx)         Backend (FastAPI)               MongoDB
     │                               │                              │                              │
     │  Enter username + password    │                              │                              │
     │  Click "Authenticate"         │                              │                              │
     │──────────────────────────────►│                              │                              │
     │                               │  [Guard: password empty?]    │                              │
     │                               │  YES → show "Please enter    │                              │
     │                               │          the password" error │                              │
     │                               │  NO → continue               │                              │
     │                               │                              │                              │
     │                               │  POST /auth/login            │                              │
     │                               │  {username, password}        │                              │
     │                               │─────────────────────────────►│                              │
     │                               │                              │  Find user in DB             │
     │                               │                              │─────────────────────────────►│
     │                               │                              │  bcrypt.verify(password)     │
     │                               │                              │  Return JWT (Factor 1 ✓)     │
     │                               │◄─────────────────────────────│                              │
     │                               │                              │                              │
     │  Show "Verify Biometrics"     │                              │                              │
     │  loading screen               │                              │                              │
     │◄──────────────────────────────│                              │                              │
     │                               │                              │                              │
     │                               │  GET /auth/login/biometric/options?username=...             │
     │                               │─────────────────────────────►│                              │
     │                               │                              │  generate_authentication_opts│
     │                               │                              │  Store new challenge in DB   │
     │                               │                              │─────────────────────────────►│
     │                               │◄─────────────────────────────│                              │
     │                               │                              │                              │
     │  Windows Hello / Touch ID     │                              │                              │
     │  prompt appears automatically │                              │                              │
     │──────────────────────────────►│                              │                              │
     │  (user scans fingerprint/face)│                              │                              │
     │                               │  POST /auth/login/biometric/verify                          │
     │                               │  {username, response}        │                              │
     │                               │─────────────────────────────►│                              │
     │                               │                              │  Decode base64url → hex      │
     │                               │                              │  Match credential in DB      │
     │                               │                              │─────────────────────────────►│
     │                               │                              │  verify_authentication_resp()│
     │                               │                              │  Update sign_count           │
     │                               │                              │  Return new JWT (Factor 2 ✓) │
     │                               │◄─────────────────────────────│                              │
     │  Redirect to Dashboard        │                              │                              │
     │◄──────────────────────────────│                              │                              │
```

---

## 4. ⬇️ Video Download Flow

```
User              Frontend                   Backend                    Filesystem
  │                   │                          │                           │
  │ Click ⬇️ button   │                          │                           │
  │──────────────────►│                          │                           │
  │                   │  GET /video/{id}          │                           │
  │                   │  + Authorization header   │                           │
  │                   │─────────────────────────►│                           │
  │                   │                          │  Validate JWT             │
  │                   │                          │  Find analysis in MongoDB │
  │                   │                          │  Read saved_video_path    │
  │                   │                          │─────────────────────────►│
  │                   │                          │  Stream file              │
  │                   │                          │◄──────────────────────────│
  │                   │◄─────────────────────────│                           │
  │                   │  Blob → createObjectURL  │                           │
  │                   │  Trigger <a> download    │                           │
  │◄──────────────────│                          │                           │
  │  File saves to    │                          │                           │
  │  Downloads folder │                          │                           │
```

---

## 5. 🗑️ History Deletion Flow

```
User              Frontend                   Backend                    MongoDB + Filesystem
  │                   │                          │                           │
  │ Click 🗑️ button   │                          │                           │
  │──────────────────►│                          │                           │
  │                   │  window.confirm() dialog │                           │
  │ Confirm "OK"      │                          │                           │
  │──────────────────►│                          │                           │
  │                   │  DELETE /history/{id}     │                           │
  │                   │  + Authorization header   │                           │
  │                   │─────────────────────────►│                           │
  │                   │                          │  Find analysis document   │
  │                   │                          │  Get saved_video_path     │
  │                   │                          │  Unlink video file        │
  │                   │                          │  Delete DB document       │
  │                   │                          │─────────────────────────►│
  │                   │  fetchHistory() refresh  │                           │
  │                   │◄─────────────────────────│                           │
  │ Card disappears   │                          │                           │
  │◄──────────────────│                          │                           │
```
