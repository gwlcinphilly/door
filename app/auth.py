"""
Authentication system for Door application
Only applies when running on Render (production environment)
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .database import get_db
from . import models
from .config import is_render

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token scheme
security = HTTPBearer()

def is_production_environment() -> bool:
    """Check if running in production (Render) environment"""
    return is_render()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return payload
    except JWTError:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    if not is_production_environment():
        # Skip authentication in development
        return {"username": "dev_user", "is_authenticated": True}
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # For now, we'll use a simple hardcoded user
    # In a real application, you'd check against a users table
    if username != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"username": username, "is_authenticated": True}

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate a user with username and password"""
    if not is_production_environment():
        # Skip authentication in development
        return True
    
    # Hardcoded credentials for production
    # In a real application, you'd check against a users table
    correct_username = "admin"
    correct_password = os.getenv("ADMIN_PASSWORD")
    
    # Security: Require AUTH_PASSWORD to be set in environment
    if not correct_username or not correct_password:
        return False
    
    # Verify password
    if username == correct_username and password == correct_password:
        return True
    return False

def create_login_token(username: str) -> str:
    """Create a login token for a user"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return access_token

# Optional: Session-based authentication for HTML pages
def get_session_user(request: Request) -> Optional[dict]:
    """Get current user from session (for HTML pages)"""
    if not is_production_environment():
        # Skip authentication in development
        return {"username": "dev_user", "is_authenticated": True}
    
    # Check for session token
    session_token = request.session.get("access_token")
    if not session_token:
        return None
    
    payload = verify_token(session_token)
    if payload is None:
        return None
    
    username: str = payload.get("sub")
    if username is None:
        return None
    
    return {"username": username, "is_authenticated": True}

def require_auth(request: Request):
    """Require authentication for HTML pages"""
    if not is_production_environment():
        # Skip authentication in development
        return {"username": "dev_user", "is_authenticated": True}
    
    user = get_session_user(request)
    if user is None:
        # For HTML requests, we need to handle redirect in the route handler
        # Return None to indicate authentication failed
        return None
    return user
