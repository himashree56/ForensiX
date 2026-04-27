@echo off
echo ========================================
echo   Deepfake Detector - Startup Script
echo ========================================
echo.

REM Set environment variables for local development
set MONGODB_URL=mongodb://localhost:27017
set DATABASE_NAME=deepfake_detector

echo Starting Backend...
cd backend
start cmd /k ".\\venv\\Scripts\\activate && python main.py"
cd ..

echo.
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo Starting Frontend...
cd frontend
start cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo   Application Starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Note: MongoDB is optional. If not running,
echo       the app will work without history features.
echo.
echo See MONGODB_SETUP.md for MongoDB installation.
echo.
echo Press any key to exit this window...
pause >nul
