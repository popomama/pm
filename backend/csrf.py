"""CSRF protection for state-changing operations."""
import secrets
import hashlib
from typing import Optional
from fastapi import HTTPException, Header, Cookie

def generate_csrf_token(session_token: str) -> str:
    """Generate a CSRF token derived from session token."""
    # Simple HMAC-like approach: hash session token with a secret
    # In production, use proper HMAC with a secret key
    return hashlib.sha256(f"csrf_{session_token}".encode()).hexdigest()

def validate_csrf_token(session_token: Optional[str], csrf_token: Optional[str]) -> bool:
    """Validate CSRF token matches the session."""
    if not session_token or not csrf_token:
        return False
    
    expected_token = generate_csrf_token(session_token)
    return secrets.compare_digest(csrf_token, expected_token)

def get_csrf_token(session_token: str = Cookie(None)) -> str:
    """Dependency to get CSRF token for the current session."""
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return generate_csrf_token(session_token)

def require_csrf(
    session_token: str = Cookie(None),
    x_csrf_token: Optional[str] = Header(None, alias="X-CSRF-Token")
) -> None:
    """Dependency to require CSRF token for state-changing operations."""
    if not validate_csrf_token(session_token, x_csrf_token):
        raise HTTPException(
            status_code=403,
            detail="CSRF token missing or invalid"
        )
