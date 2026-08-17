from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Cookie
import secrets
from database import SessionLocal, User, Session, verify_password

SESSION_DURATION = timedelta(hours=24)

def create_session(username: str) -> str:
    """Create a new session in the database."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise ValueError(f"User {username} not found")
        
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + SESSION_DURATION
        
        session = Session(
            token=session_token,
            user_id=user.id,
            expires_at=expires_at
        )
        db.add(session)
        db.commit()
        
        return session_token
    finally:
        db.close()

def validate_session(session_token: Optional[str]) -> Optional[str]:
    """Validate a session token and return the username if valid."""
    if not session_token:
        return None
    
    db = SessionLocal()
    try:
        session = db.query(Session).filter(Session.token == session_token).first()
        if not session:
            return None
        
        # Check if session has expired
        if datetime.utcnow() > session.expires_at:
            db.delete(session)
            db.commit()
            return None
        
        # Get username from user
        user = db.query(User).filter(User.id == session.user_id).first()
        return user.username if user else None
    finally:
        db.close()

def delete_session(session_token: str):
    """Delete a session from the database."""
    if not session_token:
        return
    
    db = SessionLocal()
    try:
        session = db.query(Session).filter(Session.token == session_token).first()
        if session:
            db.delete(session)
            db.commit()
    finally:
        db.close()

def cleanup_expired_sessions():
    """Remove all expired sessions from the database."""
    db = SessionLocal()
    try:
        expired = db.query(Session).filter(Session.expires_at < datetime.utcnow()).all()
        for session in expired:
            db.delete(session)
        db.commit()
        return len(expired)
    finally:
        db.close()

def verify_credentials(username: str, password: str) -> bool:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return False
        
        # Use bcrypt to verify password
        return verify_password(password, user.password_hash)
    finally:
        db.close()
