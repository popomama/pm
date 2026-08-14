# Server Scripts

This folder contains start and stop scripts for running the Kanban Studio server.

## Start Scripts

**start.bat (Windows)**
- Activates .venv virtual environment
- Installs/updates backend dependencies from requirements.txt
- Starts FastAPI server with uvicorn on port 8000
- Enables auto-reload for development

**start.sh (Mac/Linux)**
- Same functionality as start.bat
- Requires execute permissions: `chmod +x start.sh`

## Stop Scripts

**stop.bat (Windows)**
- Finds process listening on port 8000
- Terminates the server process

**stop.sh (Mac/Linux)**
- Uses lsof to find process on port 8000
- Kills the server process

## Usage

**Windows:**
```
scripts\start.bat
scripts\stop.bat
```

**Mac/Linux:**
```
./scripts/start.sh
./scripts/stop.sh
```

## Requirements

- Python virtual environment at .venv
- Backend dependencies will be installed automatically