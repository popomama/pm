from fastapi import FastAPI, HTTPException, Cookie, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
import os
import asyncio
from auth import create_session, validate_session, delete_session, verify_credentials, cleanup_expired_sessions
from database import init_db, get_db, SessionLocal
from sqlalchemy.orm import Session
from api_models import (
    BoardResponse, CreateCardRequest, UpdateCardRequest, 
    MoveCardRequest, RenameColumnRequest, UpdateBoardRequest
)
from board_service import (
    get_user_board,
    create_card as create_card_service,
    update_card as update_card_service,
    delete_card as delete_card_service,
    move_card as move_card_service,
    rename_column
)
import ai_service

app = FastAPI(title="Kanban Studio API")

async def periodic_session_cleanup():
    """Background task to clean up expired sessions every hour."""
    while True:
        await asyncio.sleep(3600)  # Run every hour
        try:
            count = cleanup_expired_sessions()
            if count > 0:
                print(f"Cleaned up {count} expired sessions")
        except Exception as e:
            print(f"Error cleaning up sessions: {e}")

@app.on_event("startup")
async def startup_event():
    init_db()
    # Start background task for session cleanup
    asyncio.create_task(periodic_session_cleanup())

frontend_dir = Path(__file__).parent.parent / "frontend" / "out"

class LoginRequest(BaseModel):
    username: str
    password: str

def get_current_user(session_token: str = Cookie(None)) -> str:
    username = validate_session(session_token)
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return username

LOGIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Kanban Studio</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #209dd7 0%, #753991 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 2rem;
        }
        .login-container {
            background: white;
            padding: 3rem;
            border-radius: 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 400px;
        }
        h1 {
            color: #032147;
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            color: #888888;
            font-size: 0.875rem;
            margin-bottom: 2rem;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        label {
            display: block;
            color: #032147;
            font-weight: 600;
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
        }
        input {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 2px solid rgba(3, 33, 71, 0.1);
            border-radius: 0.75rem;
            font-size: 1rem;
            transition: border-color 0.2s;
        }
        input:focus {
            outline: none;
            border-color: #209dd7;
        }
        button {
            width: 100%;
            padding: 0.875rem;
            background: #753991;
            color: white;
            border: none;
            border-radius: 0.75rem;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover {
            background: #5e2d75;
        }
        button:disabled {
            background: #888888;
            cursor: not-allowed;
        }
        .error {
            background: #fee;
            color: #c33;
            padding: 0.75rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            font-size: 0.875rem;
            display: none;
        }
        .hint {
            margin-top: 1rem;
            padding: 0.75rem;
            background: #f7f8fb;
            border-radius: 0.5rem;
            font-size: 0.75rem;
            color: #888888;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>Kanban Studio</h1>
        <p class="subtitle">Sign in to continue</p>
        
        <div id="error" class="error"></div>
        
        <form id="loginForm">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autocomplete="username">
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required autocomplete="current-password">
            </div>
            
            <button type="submit" id="submitBtn">Sign In</button>
        </form>
        
        <div class="hint">
            Demo credentials: username = <strong>user</strong>, password = <strong>password</strong>
        </div>
    </div>
    
    <script>
        const form = document.getElementById('loginForm');
        const errorDiv = document.getElementById('error');
        const submitBtn = document.getElementById('submitBtn');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            errorDiv.style.display = 'none';
            submitBtn.disabled = true;
            submitBtn.textContent = 'Signing in...';
            
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password }),
                });
                
                const data = await response.json();
                
                if (data.success) {
                    window.location.href = '/';
                } else {
                    errorDiv.textContent = data.error || 'Invalid credentials';
                    errorDiv.style.display = 'block';
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Sign In';
                }
            } catch (error) {
                errorDiv.textContent = 'An error occurred. Please try again.';
                errorDiv.style.display = 'block';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Sign In';
            }
        });
    </script>
</body>
</html>
"""

@app.get("/test", response_class=HTMLResponse)
async def test_endpoint():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Kanban Studio - Test</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #209dd7 0%, #753991 100%);
            }
            .container {
                background: white;
                padding: 3rem;
                border-radius: 2rem;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
            }
            h1 {
                color: #032147;
                margin: 0 0 1rem 0;
            }
            p {
                color: #888888;
                margin: 0;
            }
            .status {
                display: inline-block;
                background: #ecad0a;
                color: #032147;
                padding: 0.5rem 1rem;
                border-radius: 1rem;
                font-weight: 600;
                margin-top: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Hello World</h1>
            <p>Kanban Studio Backend is running</p>
            <div class="status">✓ Server Active</div>
        </div>
    </body>
    </html>
    """

@app.get("/api/health")
async def health_check():
    return JSONResponse(content={"status": "ok"})

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    if verify_credentials(request.username, request.password):
        session_token = create_session(request.username)
        response = JSONResponse(content={
            "success": True,
            "username": request.username
        })
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            max_age=86400,
            samesite="lax"
        )
        return response
    else:
        return JSONResponse(
            content={"success": False, "error": "Invalid credentials"},
            status_code=401
        )

@app.post("/api/auth/logout")
async def logout(session_token: str = Cookie(None)):
    if session_token:
        delete_session(session_token)
    response = JSONResponse(content={"success": True})
    response.delete_cookie("session_token")
    return response

@app.get("/api/auth/session")
async def check_session(session_token: str = Cookie(None)):
    username = validate_session(session_token)
    if username:
        return JSONResponse(content={
            "authenticated": True,
            "username": username
        })
    else:
        return JSONResponse(
            content={"authenticated": False},
            status_code=401
        )

@app.get("/api/boards")
async def get_boards(
    include_archived: bool = False,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all boards for the current user."""
    from database import User, Board
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = db.query(Board).filter(Board.user_id == user.id)
    if not include_archived:
        query = query.filter(Board.is_archived == False)
    
    boards = query.order_by(Board.updated_at.desc()).all()
    return {
        "boards": [
            {
                "id": board.id,
                "title": board.title,
                "is_archived": board.is_archived,
                "template_name": board.template_name,
                "created_at": board.created_at.isoformat(),
                "updated_at": board.updated_at.isoformat(),
            }
            for board in boards
        ]
    }

@app.get("/api/board", response_model=BoardResponse)
async def get_board(
    board_id: Optional[int] = None,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific board or the user's most recent board."""
    from database import User, Board
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if board_id:
        board = db.query(Board).filter(Board.id == board_id, Board.user_id == user.id).first()
    else:
        # Get most recent non-archived board
        board = db.query(Board).filter(
            Board.user_id == user.id,
            Board.is_archived == False
        ).order_by(Board.updated_at.desc()).first()
    
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    # Convert to BoardResponse format
    from board_service import get_user_board
    return get_user_board(db, username, board.id)

class CreateBoardRequest(BaseModel):
    title: str
    template_name: Optional[str] = 'default'

@app.post("/api/boards")
async def create_board(
    request: CreateBoardRequest,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new board for the current user."""
    from database import User, Board, Column, get_template_columns
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create board
    board = Board(
        user_id=user.id,
        title=request.title,
        template_name=request.template_name
    )
    db.add(board)
    db.commit()
    db.refresh(board)
    
    # Create columns from template
    columns = get_template_columns(request.template_name or 'default')
    for title, position in columns:
        col = Column(board_id=board.id, title=title, position=position)
        db.add(col)
    db.commit()
    
    return {
        "id": board.id,
        "title": board.title,
        "template_name": board.template_name,
        "created_at": board.created_at.isoformat()
    }

@app.delete("/api/boards/{board_id}")
async def delete_board(
    board_id: int,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a board."""
    from database import User, Board
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    board = db.query(Board).filter(Board.id == board_id, Board.user_id == user.id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    db.delete(board)
    db.commit()
    return {"success": True}

@app.put("/api/boards/{board_id}/archive")
async def archive_board(
    board_id: int,
    archive: bool = True,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Archive or unarchive a board."""
    from database import User, Board
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    board = db.query(Board).filter(Board.id == board_id, Board.user_id == user.id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    board.is_archived = archive
    db.commit()
    return {"success": True, "is_archived": board.is_archived}

@app.post("/api/boards/{board_id}/duplicate")
async def duplicate_board(
    board_id: int,
    include_cards: bool = False,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Duplicate a board."""
    from database import User, Board, Column, Card
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    original_board = db.query(Board).filter(Board.id == board_id, Board.user_id == user.id).first()
    if not original_board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    # Create new board
    new_board = Board(
        user_id=user.id,
        title=f"{original_board.title} (Copy)",
        template_name=original_board.template_name
    )
    db.add(new_board)
    db.commit()
    db.refresh(new_board)
    
    # Copy columns
    original_columns = db.query(Column).filter(Column.board_id == original_board.id).order_by(Column.position).all()
    column_mapping = {}
    
    for orig_col in original_columns:
        new_col = Column(
            board_id=new_board.id,
            title=orig_col.title,
            position=orig_col.position
        )
        db.add(new_col)
        db.commit()
        db.refresh(new_col)
        column_mapping[orig_col.id] = new_col.id
    
    # Copy cards if requested
    if include_cards:
        for orig_col in original_columns:
            cards = db.query(Card).filter(Card.column_id == orig_col.id).order_by(Card.position).all()
            for card in cards:
                new_card = Card(
                    column_id=column_mapping[orig_col.id],
                    title=card.title,
                    details=card.details,
                    position=card.position
                )
                db.add(new_card)
        db.commit()
    
    return {
        "id": new_board.id,
        "title": new_board.title,
        "created_at": new_board.created_at.isoformat()
    }

@app.post("/api/cards")
async def create_new_card(
    request: CreateCardRequest,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    card = create_card_service(db, username, request.columnId, request.title, request.details)
    if not card:
        raise HTTPException(status_code=400, detail="Failed to create card")
    return card

@app.put("/api/cards/{card_id}")
async def update_existing_card(
    card_id: str,
    request: UpdateCardRequest,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = update_card_service(db, username, card_id, request.title, request.details)
    if not success:
        raise HTTPException(status_code=404, detail="Card not found")
    return {"success": True}

@app.delete("/api/cards/{card_id}")
async def delete_existing_card(
    card_id: str,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = delete_card_service(db, username, card_id)
    if not success:
        raise HTTPException(status_code=404, detail="Card not found")
    return {"success": True}

@app.put("/api/cards/{card_id}/move")
async def move_existing_card(
    card_id: str,
    request: MoveCardRequest,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = move_card_service(db, username, card_id, request.columnId, request.position)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to move card")
    return {"success": True}

@app.put("/api/columns/{column_id}")
async def rename_existing_column(
    column_id: str,
    request: RenameColumnRequest,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = rename_column(db, username, column_id, request.title)
    if not success:
        raise HTTPException(status_code=404, detail="Column not found")
    return {"success": True}

@app.post("/api/ai/test")
async def test_ai(username: str = Depends(get_current_user)):
    try:
        import ai_client
        response = ai_client.simple_query("What is 2+2?")
        return {
            "success": True,
            "question": "What is 2+2?",
            "response": response,
            "model": ai_client.MODEL
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI request failed: {str(e)}")

class ChatRequest(BaseModel):
    message: str
    board: Optional[dict] = None

@app.get("/api/ai/chat/history")
async def get_chat_history(
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for the current user."""
    try:
        history = ai_service.get_conversation_history(db, username, limit=50)
        return {"messages": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load chat history: {str(e)}")

@app.post("/api/ai/chat")
async def chat_with_ai_endpoint(
    request: ChatRequest,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        result = ai_service.chat_with_ai(
            db=db,
            username=username,
            user_message=request.message,
            board_data=request.board
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI chat failed: {str(e)}")

if frontend_dir.exists():
    app.mount("/_next", StaticFiles(directory=frontend_dir / "_next"), name="next-static")
    
    @app.get("/")
    async def serve_frontend(session_token: str = Cookie(None)):
        username = validate_session(session_token)
        if not username:
            return RedirectResponse(url="/login", status_code=302)
        
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return JSONResponse(content={"error": "Frontend not built"}, status_code=404)
    
    @app.get("/login")
    async def serve_login():
        return HTMLResponse(content=LOGIN_PAGE_HTML)
    
    @app.get("/{full_path:path}")
    async def serve_static_files(full_path: str):
        file_path = frontend_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return JSONResponse(content={"error": "File not found"}, status_code=404)
