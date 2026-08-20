from fastapi import FastAPI, HTTPException, Cookie, Depends, BackgroundTasks, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
import os
import asyncio
import uuid
import mimetypes
from auth import create_session, validate_session, delete_session, verify_credentials, cleanup_expired_sessions
from database import init_db, get_db, SessionLocal
from sqlalchemy.orm import Session
from api_models import (
    BoardResponse, CreateCardRequest, UpdateCardRequest, 
    MoveCardRequest, RenameColumnRequest, UpdateBoardRequest,
    CreateChecklistItemRequest, UpdateChecklistItemRequest,
    CreateColumnRequest, UpdateColumnRequest, ReorderColumnsRequest
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

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    display_name: Optional[str] = None

class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None

class AddBoardMemberRequest(BaseModel):
    user_id: int
    role: str  # 'owner', 'editor', 'viewer'

class UpdateMemberRoleRequest(BaseModel):
    role: str

def get_current_user(session_token: str = Cookie(None)) -> str:
    username = validate_session(session_token)
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return username

def check_board_permission(board_id: int, username: str, required_role: str, db: Session) -> bool:
    """
    Check if user has required permission level for a board.
    Roles hierarchy: owner > editor > viewer
    """
    from database import User, Board, BoardMember
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        return False
    
    # Owner has all permissions
    if board.owner_id == user.id:
        return True
    
    # Check membership
    membership = db.query(BoardMember).filter(
        BoardMember.board_id == board_id,
        BoardMember.user_id == user.id
    ).first()
    
    if not membership:
        return False
    
    # Check role hierarchy
    role_hierarchy = {'owner': 3, 'editor': 2, 'viewer': 1}
    user_level = role_hierarchy.get(membership.role, 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    return user_level >= required_level

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

@app.post("/api/auth/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    from database import User, hash_password
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists
    if request.email:
        existing_email = db.query(User).filter(User.email == request.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create new user
    new_user = User(
        username=request.username,
        password_hash=hash_password(request.password),
        email=request.email,
        display_name=request.display_name or request.username
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create session for new user
    session_token = create_session(request.username)
    
    response = JSONResponse(content={
        "success": True,
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "display_name": new_user.display_name
        }
    })
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=86400,
        samesite="lax"
    )
    return response

@app.get("/api/users/me")
async def get_current_user_profile(
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from database import User
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }

@app.put("/api/users/me")
async def update_current_user_profile(
    request: UpdateProfileRequest,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from database import User
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if request.display_name is not None:
        user.display_name = request.display_name
    if request.avatar_url is not None:
        user.avatar_url = request.avatar_url
    
    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "avatar_url": user.avatar_url
        }
    }

@app.get("/api/users/search")
async def search_users(
    q: str,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from database import User
    
    if len(q) < 2:
        return {"users": []}
    
    users = db.query(User).filter(
        (User.username.like(f"%{q}%")) | (User.email.like(f"%{q}%"))
    ).limit(10).all()
    
    return {
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "avatar_url": user.avatar_url
            }
            for user in users
        ]
    }

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
    """Get all boards for the current user (owned or member)."""
    from database import User, Board, BoardMember
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get boards where user is owner or member
    owned_query = db.query(Board).filter(Board.owner_id == user.id)
    if not include_archived:
        owned_query = owned_query.filter(Board.is_archived == False)
    owned_boards = owned_query.all()
    
    member_query = db.query(Board).join(BoardMember).filter(
        BoardMember.user_id == user.id,
        Board.owner_id != user.id  # Don't duplicate owned boards
    )
    if not include_archived:
        member_query = member_query.filter(Board.is_archived == False)
    member_boards = member_query.all()
    
    all_boards = owned_boards + member_boards
    all_boards.sort(key=lambda b: b.updated_at, reverse=True)
    
    return {
        "boards": [
            {
                "id": board.id,
                "title": board.title,
                "is_archived": board.is_archived,
                "template_name": board.template_name,
                "created_at": board.created_at.isoformat(),
                "updated_at": board.updated_at.isoformat(),
                "is_owner": board.owner_id == user.id
            }
            for board in all_boards
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

# Board Sharing Endpoints

@app.get("/api/boards/{board_id}/members")
async def get_board_members(
    board_id: int,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all members of a board."""
    from database import BoardMember
    
    if not check_board_permission(board_id, username, 'viewer', db):
        raise HTTPException(status_code=403, detail="Access denied")
    
    members = db.query(BoardMember).filter(BoardMember.board_id == board_id).all()
    
    return {
        "members": [
            {
                "id": member.id,
                "user_id": member.user_id,
                "username": member.user.username,
                "display_name": member.user.display_name,
                "avatar_url": member.user.avatar_url,
                "role": member.role,
                "created_at": member.created_at.isoformat()
            }
            for member in members
        ]
    }

@app.post("/api/boards/{board_id}/members")
async def add_board_member(
    board_id: int,
    request: AddBoardMemberRequest,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a member to a board (owner only)."""
    from database import Board, BoardMember, User
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    board = db.query(Board).filter(Board.id == board_id, Board.owner_id == user.id).first()
    if not board:
        raise HTTPException(status_code=403, detail="Only board owner can add members")
    
    existing = db.query(BoardMember).filter(
        BoardMember.board_id == board_id,
        BoardMember.user_id == request.user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member")
    
    if request.role not in ['owner', 'editor', 'viewer']:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    new_member = BoardMember(
        board_id=board_id,
        user_id=request.user_id,
        role=request.role
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    
    return {
        "success": True,
        "member": {
            "id": new_member.id,
            "user_id": new_member.user_id,
            "role": new_member.role
        }
    }

@app.put("/api/boards/{board_id}/members/{user_id}")
async def update_member_role(
    board_id: int,
    user_id: int,
    request: UpdateMemberRoleRequest,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a member's role (owner only)."""
    from database import Board, BoardMember, User
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    board = db.query(Board).filter(Board.id == board_id, Board.owner_id == user.id).first()
    if not board:
        raise HTTPException(status_code=403, detail="Only board owner can update member roles")
    
    if request.role not in ['owner', 'editor', 'viewer']:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    member = db.query(BoardMember).filter(
        BoardMember.board_id == board_id,
        BoardMember.user_id == user_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    member.role = request.role
    db.commit()
    
    return {"success": True, "role": member.role}

@app.delete("/api/boards/{board_id}/members/{user_id}")
async def remove_board_member(
    board_id: int,
    user_id: int,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a member from a board (owner only)."""
    from database import Board, BoardMember, User
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    board = db.query(Board).filter(Board.id == board_id, Board.owner_id == user.id).first()
    if not board:
        raise HTTPException(status_code=403, detail="Only board owner can remove members")
    
    member = db.query(BoardMember).filter(
        BoardMember.board_id == board_id,
        BoardMember.user_id == user_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    db.delete(member)
    db.commit()
    
    return {"success": True}

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
    success = update_card_service(
        db, username, card_id, 
        request.title, request.details,
        request.dueDate, request.priority, request.tags
    )
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

# Column management endpoints
@app.post("/api/boards/{board_id}/columns")
async def create_column(
    board_id: int,
    request: CreateColumnRequest,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new column in a board."""
    from database import User, Board, Column
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    board = db.query(Board).filter(Board.id == board_id, Board.user_id == user.id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    # Get next position if not specified
    if request.position is None:
        max_pos = db.query(Column).filter(Column.board_id == board_id).count()
        position = max_pos
    else:
        position = request.position
        # Shift existing columns
        db.query(Column).filter(
            Column.board_id == board_id,
            Column.position >= position
        ).update({Column.position: Column.position + 1})
    
    column = Column(
        board_id=board_id,
        title=request.title,
        position=position,
        wip_limit=request.wipLimit
    )
    db.add(column)
    db.commit()
    db.refresh(column)
    
    return {
        "id": f"col-{column.id}",
        "title": column.title,
        "position": column.position,
        "wipLimit": column.wip_limit
    }

@app.put("/api/columns/{column_id}/update")
async def update_column(
    column_id: str,
    request: UpdateColumnRequest,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update column title and/or WIP limit."""
    from database import User, Column
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    col_id = int(column_id.replace("col-", ""))
    column = db.query(Column).filter(Column.id == col_id).first()
    if not column or column.board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Column not found")
    
    if request.title is not None:
        column.title = request.title
    if request.wipLimit is not None:
        column.wip_limit = request.wipLimit if request.wipLimit > 0 else None
    
    db.commit()
    return {"success": True}

@app.delete("/api/columns/{column_id}")
async def delete_column(
    column_id: str,
    migrate_to_column_id: Optional[str] = None,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a column and optionally migrate cards to another column."""
    from database import User, Column, Card
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    col_id = int(column_id.replace("col-", ""))
    column = db.query(Column).filter(Column.id == col_id).first()
    if not column or column.board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Column not found")
    
    board_id = column.board_id
    position = column.position
    
    # Migrate cards if target column specified
    if migrate_to_column_id:
        target_col_id = int(migrate_to_column_id.replace("col-", ""))
        target_column = db.query(Column).filter(Column.id == target_col_id).first()
        if not target_column or target_column.board_id != board_id:
            raise HTTPException(status_code=400, detail="Invalid target column")
        
        # Move all cards to target column
        cards = db.query(Card).filter(Card.column_id == col_id).all()
        max_pos = db.query(Card).filter(Card.column_id == target_col_id).count()
        for i, card in enumerate(cards):
            card.column_id = target_col_id
            card.position = max_pos + i
    
    # Delete column (cards will cascade delete if not migrated)
    db.delete(column)
    db.flush()
    
    # Shift remaining columns - use two-step to avoid unique constraint violations
    remaining_columns = db.query(Column).filter(
        Column.board_id == board_id,
        Column.position > position
    ).order_by(Column.position).all()
    
    # First set to negative positions
    for col in remaining_columns:
        col.position = -col.id
    db.flush()
    
    # Then set to final positions
    for i, col in enumerate(remaining_columns):
        col.position = position + i
    
    db.commit()
    return {"success": True}

@app.post("/api/boards/{board_id}/columns/reorder")
async def reorder_columns(
    board_id: int,
    request: ReorderColumnsRequest,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reorder columns in a board."""
    from database import User, Board, Column
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    board = db.query(Board).filter(Board.id == board_id, Board.user_id == user.id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    # First, set all positions to negative values to avoid unique constraint violations
    columns = db.query(Column).filter(Column.board_id == board_id).all()
    for col in columns:
        col.position = -col.id  # Use negative ID as temporary position
    db.flush()
    
    # Now update to final positions
    for i, column_id in enumerate(request.columnOrder):
        col_id = int(column_id.replace("col-", ""))
        column = db.query(Column).filter(Column.id == col_id, Column.board_id == board_id).first()
        if column:
            column.position = i
    
    db.commit()
    return {"success": True}

# Checklist endpoints
@app.post("/api/cards/{card_id}/checklist")
async def add_checklist_item(
    card_id: str,
    request: CreateChecklistItemRequest,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from database import User, Card, ChecklistItem
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    c_id = int(card_id.replace("card-", ""))
    card = db.query(Card).filter(Card.id == c_id).first()
    if not card or card.column.board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Get next position
    max_pos = db.query(ChecklistItem).filter(ChecklistItem.card_id == c_id).count()
    
    item = ChecklistItem(
        card_id=c_id,
        text=request.text,
        position=max_pos,
        completed=False
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return {
        "id": item.id,
        "text": item.text,
        "completed": item.completed,
        "position": item.position
    }

@app.put("/api/cards/{card_id}/checklist/{item_id}")
async def update_checklist_item(
    card_id: str,
    item_id: int,
    request: UpdateChecklistItemRequest,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from database import User, Card, ChecklistItem
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    c_id = int(card_id.replace("card-", ""))
    card = db.query(Card).filter(Card.id == c_id).first()
    if not card or card.column.board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Card not found")
    
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id, ChecklistItem.card_id == c_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    
    if request.text is not None:
        item.text = request.text
    if request.completed is not None:
        item.completed = request.completed
    
    db.commit()
    return {"success": True}

@app.delete("/api/cards/{card_id}/checklist/{item_id}")
async def delete_checklist_item(
    card_id: str,
    item_id: int,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from database import User, Card, ChecklistItem
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    c_id = int(card_id.replace("card-", ""))
    card = db.query(Card).filter(Card.id == c_id).first()
    if not card or card.column.board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Card not found")
    
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id, ChecklistItem.card_id == c_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    
    db.delete(item)
    db.commit()
    return {"success": True}

# File attachment endpoints
UPLOAD_DIR = Path(__file__).parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@app.post("/api/cards/{card_id}/attachments")
async def upload_attachment(
    card_id: str,
    file: UploadFile = File(...),
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a file attachment to a card."""
    from database import User, Card, CardAttachment
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    c_id = int(card_id.replace("card-", ""))
    card = db.query(Card).filter(Card.id == c_id).first()
    if not card or card.column.board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Validate file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024}MB")
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Determine MIME type
    mime_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
    
    # Create database record
    attachment = CardAttachment(
        card_id=c_id,
        filename=unique_filename,
        original_filename=file.filename,
        file_size=file_size,
        mime_type=mime_type,
        uploaded_by=user.id
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    
    return {
        "id": attachment.id,
        "filename": attachment.original_filename,
        "size": attachment.file_size,
        "mimeType": attachment.mime_type,
        "uploadedAt": attachment.uploaded_at.isoformat()
    }

@app.get("/api/cards/{card_id}/attachments")
async def list_attachments(
    card_id: str,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all attachments for a card."""
    from database import User, Card, CardAttachment
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    c_id = int(card_id.replace("card-", ""))
    card = db.query(Card).filter(Card.id == c_id).first()
    if not card or card.column.board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Card not found")
    
    attachments = db.query(CardAttachment).filter(CardAttachment.card_id == c_id).all()
    
    return {
        "attachments": [
            {
                "id": att.id,
                "filename": att.original_filename,
                "size": att.file_size,
                "mimeType": att.mime_type,
                "uploadedAt": att.uploaded_at.isoformat()
            }
            for att in attachments
        ]
    }

@app.get("/api/attachments/{attachment_id}/download")
async def download_attachment(
    attachment_id: int,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download an attachment file."""
    from database import User, CardAttachment
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    attachment = db.query(CardAttachment).filter(CardAttachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    # Verify user owns the card
    if attachment.card.column.board.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    file_path = UPLOAD_DIR / attachment.filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=attachment.original_filename,
        media_type=attachment.mime_type
    )

@app.delete("/api/attachments/{attachment_id}")
async def delete_attachment(
    attachment_id: int,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an attachment."""
    from database import User, CardAttachment
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    attachment = db.query(CardAttachment).filter(CardAttachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    # Verify user owns the card
    if attachment.card.column.board.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete physical file
    file_path = UPLOAD_DIR / attachment.filename
    if file_path.exists():
        file_path.unlink()
    
    # Delete database record
    db.delete(attachment)
    db.commit()
    
    return {"success": True}

# Label endpoints
@app.get("/api/boards/{board_id}/labels")
async def get_board_labels(
    board_id: int,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all labels for a board."""
    from database import User, Board, BoardLabel
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    board = db.query(Board).filter(Board.id == board_id, Board.user_id == user.id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    labels = db.query(BoardLabel).filter(BoardLabel.board_id == board_id).all()
    
    return {
        "labels": [
            {
                "id": label.id,
                "name": label.name,
                "color": label.color
            }
            for label in labels
        ]
    }

@app.post("/api/boards/{board_id}/labels")
async def create_label(
    board_id: int,
    label_data: dict,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new label for a board."""
    from database import User, Board, BoardLabel
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    board = db.query(Board).filter(Board.id == board_id, Board.user_id == user.id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    label = BoardLabel(
        board_id=board_id,
        name=label_data["name"],
        color=label_data["color"]
    )
    db.add(label)
    db.commit()
    db.refresh(label)
    
    return {
        "id": label.id,
        "name": label.name,
        "color": label.color
    }

@app.put("/api/labels/{label_id}")
async def update_label(
    label_id: int,
    label_data: dict,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a label."""
    from database import User, BoardLabel
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    label = db.query(BoardLabel).filter(BoardLabel.id == label_id).first()
    if not label or label.board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Label not found")
    
    label.name = label_data["name"]
    label.color = label_data["color"]
    db.commit()
    
    return {
        "id": label.id,
        "name": label.name,
        "color": label.color
    }

@app.delete("/api/labels/{label_id}")
async def delete_label(
    label_id: int,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a label."""
    from database import User, BoardLabel
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    label = db.query(BoardLabel).filter(BoardLabel.id == label_id).first()
    if not label or label.board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Label not found")
    
    db.delete(label)
    db.commit()
    
    return {"success": True}

@app.post("/api/cards/{card_id}/labels/{label_id}")
async def add_label_to_card(
    card_id: str,
    label_id: int,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a label to a card."""
    from database import User, Card, BoardLabel, CardLabel
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    c_id = int(card_id.replace("card-", ""))
    card = db.query(Card).filter(Card.id == c_id).first()
    if not card or card.column.board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Card not found")
    
    label = db.query(BoardLabel).filter(BoardLabel.id == label_id).first()
    if not label or label.board_id != card.column.board_id:
        raise HTTPException(status_code=404, detail="Label not found")
    
    # Check if already exists
    existing = db.query(CardLabel).filter(
        CardLabel.card_id == c_id,
        CardLabel.label_id == label_id
    ).first()
    
    if existing:
        return {"success": True}
    
    card_label = CardLabel(card_id=c_id, label_id=label_id)
    db.add(card_label)
    db.commit()
    
    return {"success": True}

@app.delete("/api/cards/{card_id}/labels/{label_id}")
async def remove_label_from_card(
    card_id: str,
    label_id: int,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a label from a card."""
    from database import User, Card, CardLabel
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    c_id = int(card_id.replace("card-", ""))
    card = db.query(Card).filter(Card.id == c_id).first()
    if not card or card.column.board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Card not found")
    
    card_label = db.query(CardLabel).filter(
        CardLabel.card_id == c_id,
        CardLabel.label_id == label_id
    ).first()
    
    if card_label:
        db.delete(card_label)
        db.commit()
    
    return {"success": True}

# Custom field endpoints
@app.get("/api/boards/{board_id}/fields")
async def get_board_fields(
    board_id: int,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all custom fields for a board."""
    from database import User, Board, CustomField
    import json
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    board = db.query(Board).filter(Board.id == board_id, Board.user_id == user.id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    fields = db.query(CustomField).filter(CustomField.board_id == board_id).order_by(CustomField.position).all()
    
    return {
        "fields": [
            {
                "id": field.id,
                "name": field.name,
                "fieldType": field.field_type,
                "options": json.loads(field.options) if field.options else None,
                "position": field.position
            }
            for field in fields
        ]
    }

@app.post("/api/boards/{board_id}/fields")
async def create_field(
    board_id: int,
    field_data: dict,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new custom field for a board."""
    from database import User, Board, CustomField
    import json
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    board = db.query(Board).filter(Board.id == board_id, Board.user_id == user.id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    # Get next position
    max_pos = db.query(CustomField).filter(CustomField.board_id == board_id).count()
    
    options_json = json.dumps(field_data.get("options")) if field_data.get("options") else None
    
    field = CustomField(
        board_id=board_id,
        name=field_data["name"],
        field_type=field_data["fieldType"],
        options=options_json,
        position=max_pos
    )
    db.add(field)
    db.commit()
    db.refresh(field)
    
    return {
        "id": field.id,
        "name": field.name,
        "fieldType": field.field_type,
        "options": json.loads(field.options) if field.options else None,
        "position": field.position
    }

@app.put("/api/fields/{field_id}")
async def update_field(
    field_id: int,
    field_data: dict,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a custom field."""
    from database import User, CustomField
    import json
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    field = db.query(CustomField).filter(CustomField.id == field_id).first()
    if not field or field.board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Field not found")
    
    field.name = field_data["name"]
    if "options" in field_data:
        field.options = json.dumps(field_data["options"]) if field_data["options"] else None
    db.commit()
    
    return {
        "id": field.id,
        "name": field.name,
        "fieldType": field.field_type,
        "options": json.loads(field.options) if field.options else None,
        "position": field.position
    }

@app.delete("/api/fields/{field_id}")
async def delete_field(
    field_id: int,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a custom field."""
    from database import User, CustomField
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    field = db.query(CustomField).filter(CustomField.id == field_id).first()
    if not field or field.board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Field not found")
    
    db.delete(field)
    db.commit()
    
    return {"success": True}

@app.put("/api/cards/{card_id}/fields/{field_id}")
async def set_field_value(
    card_id: str,
    field_id: int,
    value_data: dict,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set field value for a card."""
    from database import User, Card, CustomField, CardFieldValue
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    c_id = int(card_id.replace("card-", ""))
    card = db.query(Card).filter(Card.id == c_id).first()
    if not card or card.column.board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Card not found")
    
    field = db.query(CustomField).filter(CustomField.id == field_id).first()
    if not field or field.board_id != card.column.board_id:
        raise HTTPException(status_code=404, detail="Field not found")
    
    # Check if value already exists
    field_value = db.query(CardFieldValue).filter(
        CardFieldValue.card_id == c_id,
        CardFieldValue.field_id == field_id
    ).first()
    
    if field_value:
        field_value.value = value_data["value"]
    else:
        field_value = CardFieldValue(
            card_id=c_id,
            field_id=field_id,
            value=value_data["value"]
        )
        db.add(field_value)
    
    db.commit()
    return {"success": True}

@app.delete("/api/cards/{card_id}/fields/{field_id}")
async def clear_field_value(
    card_id: str,
    field_id: int,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear field value for a card."""
    from database import User, Card, CardFieldValue
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    c_id = int(card_id.replace("card-", ""))
    card = db.query(Card).filter(Card.id == c_id).first()
    if not card or card.column.board.user_id != user.id:
        raise HTTPException(status_code=404, detail="Card not found")
    
    field_value = db.query(CardFieldValue).filter(
        CardFieldValue.card_id == c_id,
        CardFieldValue.field_id == field_id
    ).first()
    
    if field_value:
        db.delete(field_value)
        db.commit()
    
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
