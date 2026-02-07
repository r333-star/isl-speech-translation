#!/bin/bash

echo "=========================================="
echo "ISL AI Communicator - Quick Start"
echo "=========================================="
echo ""

echo "Step 1: Starting Backend Server..."
echo ""
cd backend
python3 app.py &
BACKEND_PID=$!
sleep 3

echo "Step 2: Opening Frontend..."
echo ""
cd ../frontend
python3 -m http.server 8000 &
FRONTEND_PID=$!
sleep 2

# Open browser
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:8000
elif command -v open > /dev/null; then
    open http://localhost:8000
fi

echo ""
echo "=========================================="
echo "System Started!"
echo "=========================================="
echo ""
echo "Backend running at: http://localhost:5000"
echo "Frontend running at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
