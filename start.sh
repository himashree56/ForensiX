#!/bin/bash

echo "========================================"
echo "  Deepfake Detection - Quick Start"
echo "========================================"
echo ""

echo "[1/3] Starting Backend Server..."
echo ""
cd backend
gnome-terminal -- bash -c "python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python main.py; exec bash" 2>/dev/null || \
xterm -e "python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python main.py; bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd \"'$(pwd)'\" && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python main.py"' 2>/dev/null &
cd ..

echo "Waiting for backend to initialize..."
sleep 10

echo ""
echo "[2/3] Starting Frontend Server..."
echo ""
cd frontend
gnome-terminal -- bash -c "npm install && npm run dev; exec bash" 2>/dev/null || \
xterm -e "npm install && npm run dev; bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd \"'$(pwd)'\" && npm install && npm run dev"' 2>/dev/null &
cd ..

echo ""
echo "[3/3] Setup Complete!"
echo ""
echo "========================================"
echo "  Services Starting:"
echo "  - Backend:  http://localhost:8000"
echo "  - Frontend: http://localhost:3000"
echo "  - API Docs: http://localhost:8000/docs"
echo "========================================"
echo ""
