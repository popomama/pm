from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Cookie
import secrets
import hashlib
from database import SessionLocal, User

SESSION_DURATION = timedelta(hours=24)
sessions = {}

def create_session(username: str) -> str:
    session_token = secrets.token_urlsafe(32)
    sessions[session_token] = {
        "username": username,
        "created_at": datetime.now()
    }
    return session_token

def validate_session(session_token: Optional[str]) -> Optional[str]:
    if not session_token or session_token not in sessions:
        return None
    
    session = sessions[session_token]
    if datetime.now() - session["created_at"] > SESSION_DURATION:
        del sessions[session_token]
        return None
    
    return session["username"]

def delete_session(session_token: str):
    if session_token in sessions:
        del sessions[session_token]

def verify_credentials(username: str, password: str) -> bool:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return False
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == user.password_hash
    finally:
        db.close()
