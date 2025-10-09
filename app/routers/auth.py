"""
Authentication router for login/logout functionality
"""

from fastapi import APIRouter, Request, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import (
    authenticate_user, 
    create_login_token, 
    is_production_environment,
    get_session_user
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    # If already authenticated, redirect to home
    user = get_session_user(request)
    if user:
        return RedirectResponse(url="/", status_code=302)
    
    return templates.TemplateResponse("login.html", {
        "request": request,
        "is_production": is_production_environment()
    })

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """Process login form"""
    if not is_production_environment():
        # Skip authentication in development
        request.session["access_token"] = "dev_token"
        return RedirectResponse(url="/", status_code=302)
    
    # Authenticate user
    if authenticate_user(username, password):
        # Create token and store in session
        token = create_login_token(username)
        request.session["access_token"] = token
        return RedirectResponse(url="/", status_code=302)
    else:
        # Invalid credentials
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid username or password",
            "is_production": is_production_environment()
        })

@router.get("/logout")
async def logout(request: Request):
    """Logout user"""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)
