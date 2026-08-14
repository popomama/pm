#!/bin/bash

echo "Starting Kanban Studio..."
echo ""

cd "$(dirname "$0")/.."

if [ ! -f ".venv/bin/activate" ]; then
    echo "Error: Virtual environment not found at .venv"
    echo "Please create a virtual environment first"
    exit 1
fi

source .venv/bin/activate

echo "Installing/updating backend dependencies..."
pip install -q -r backend/requirements.txt

echo ""
echo "Building frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi
npm run build
cd ..

echo ""
echo "Starting FastAPI server on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
