# Backend API

FastAPI backend for Kanban Studio project management application.

## Current Implementation (Part 2)

### Files

**main.py**
- FastAPI application entry point
- Test endpoints for initial scaffolding

### Endpoints

**GET /test**
- Returns HTML "Hello World" page
- Styled with project color scheme
- Confirms server is running

**GET /api/health**
- Returns JSON: `{"status": "ok"}`
- Health check endpoint for monitoring

### Dependencies (requirements.txt)

- fastapi==0.115.6 - Web framework
- uvicorn[standard]==0.34.0 - ASGI server
- python-multipart==0.0.20 - Form data support

### Running the Server

Use the start scripts in the scripts/ directory:
- Windows: `scripts\start.bat`
- Mac/Linux: `./scripts/start.sh`

Server runs on: http://localhost:8000

### Testing

- Visit http://localhost:8000/test for HTML test page
- Visit http://localhost:8000/api/health for JSON health check
- Visit http://localhost:8000/docs for auto-generated API documentation

## Future Implementation

The backend will be extended with:
- Static file serving for Next.js frontend
- User authentication endpoints
- SQLite database integration
- Kanban board CRUD API
- AI chat integration with gpt-oss-120b model