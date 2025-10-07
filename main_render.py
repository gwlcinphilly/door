"""
FastAPI Main Application for Render Deployment
Configured to connect to Neon database for production deployment
"""

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import os
from pathlib import Path

# Import routers
from app.routers import stocks, information, notes, api, settings, auth
from app.database import engine, get_db
from app import models
from app.auth import is_production_environment, require_auth

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Door - Stock & Information Manager",
    description="A modern web application for managing stocks, information, and notes",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware for authentication
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "your-secret-key-here"))

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(api.router, prefix="/api", tags=["api"])
app.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
app.include_router(information.router, prefix="/information", tags=["information"])
app.include_router(notes.router, prefix="/notes", tags=["notes"])
app.include_router(settings.router, prefix="/settings", tags=["settings"])

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user: dict = Depends(require_auth)):
    """Home page with dashboard overview"""
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Door application is running on Render"}

if __name__ == "__main__":
    # Render deployment configuration
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(
        "main_render:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
