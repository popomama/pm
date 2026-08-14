@echo off
echo Starting Kanban Studio...
echo.

cd /d "%~dp0.."

if not exist ".venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found at .venv
    echo Please create a virtual environment first
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo Installing/updating backend dependencies...
pip install -q -r backend\requirements.txt

echo.
echo Building frontend...
cd frontend
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)
call npm run build
cd ..

echo.
echo Starting FastAPI server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
