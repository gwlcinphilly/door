"""
FastAPI Main Application
A modern Python web application for managing stocks, information, and notes.

Supports three deployment environments:
- LOCAL: Development machine (auto-detected)
- MIRROR: Internal production server (hostname contains "mirror")
- RENDER: Cloud production (detected via RENDER env var)
"""

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import os
import sys
import subprocess
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Import routers
from app.routers import stocks, information, notes, api, settings, auth, environment
from app.database import engine, get_db
from app import models
from app.config import (
    system_config, is_local, is_mirror, is_render, 
    requires_auth, get_environment_info, get_config
)
from app.auth import require_auth

# Configure logging
def setup_logging():
    """Setup logging to both file and console"""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Also configure uvicorn logger
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    
    # Access log file handler
    access_handler = RotatingFileHandler(
        log_dir / "access.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(file_formatter)
    uvicorn_access_logger.addHandler(access_handler)
    
    return logger

# Setup logging
logger = setup_logging()

# Print environment information
logger.info("="*80)
logger.info("🚀 Starting Door Application")
logger.info("="*80)
logger.info(f"Environment: {system_config.config.get('name')}")
logger.info(f"Description: {system_config.config.get('description')}")
logger.info(f"Database: {system_config.config.get('database')}")
logger.info(f"Authentication: {'Required' if requires_auth() else 'Disabled'}")
logger.info(f"Access: {system_config.config.get('access')}")
logger.info(f"Debug Mode: {system_config.config.get('debug')}")
logger.info("="*80)

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
    allow_origins=["*"] if not is_render() else ["https://*.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware if authentication is required
if requires_auth():
    app.add_middleware(
        SessionMiddleware, 
        secret_key=os.getenv("SECRET_KEY", "change-this-secret-key")
    )

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(api.router, prefix="/api", tags=["api"])
app.include_router(environment.router, prefix="/environment", tags=["environment"])
app.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
app.include_router(information.router, prefix="/information", tags=["information"])
app.include_router(notes.router, prefix="/notes", tags=["notes"])
app.include_router(settings.router, prefix="/settings", tags=["settings"])

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user: dict = Depends(require_auth) if requires_auth() else None):
    """Home page with dashboard overview"""
    # If authentication is required and user is not authenticated, redirect to login
    if requires_auth() and user is None:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    context = {"request": request}
    if user:
        context["user"] = user
    
    return templates.TemplateResponse("index.html", context)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    config = get_config()
    return {
        "status": "healthy",
        "message": f"Door application is running",
        "environment": config.get('name'),
        "database": config.get('database')
    }

def run_database_sync():
    """Run database sync before starting the application (local only)"""
    if not is_local():
        logger.info("⏭️  Skipping database sync (not running on local dev machine)")
        return
    
    logger.info("="*60)
    logger.info("🔄 Running database sync before startup...")
    logger.info("="*60)
    
    try:
        # Get the path to the database sync script
        sync_script = Path(__file__).parent / "tools" / "database_sync.py"
        
        if not sync_script.exists():
            logger.warning("⚠️  Database sync script not found, skipping...")
            return
        
        # Run the sync script with smart-sync mode
        result = subprocess.run(
            [sys.executable, str(sync_script), "--direction", "smart-sync"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            logger.info("✅ Database sync completed successfully")
            if result.stdout:
                logger.info(result.stdout)
        else:
            logger.warning("⚠️  Database sync failed, but continuing with startup...")
            if result.stderr:
                logger.error(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logger.warning("⚠️  Database sync timed out, continuing with startup...")
    except Exception as e:
        logger.error(f"⚠️  Error running database sync: {e}")
        logger.info("Continuing with application startup...")
    
    logger.info("="*60)

if __name__ == "__main__":
    # Run database sync before starting the server (local only)
    run_database_sync()
    
    # Get configuration
    config = get_config()
    port = config.get('port', 8080)
    host = config.get('host', '0.0.0.0')
    auto_reload = config.get('auto_reload', False)
    
    logger.info(f"Starting uvicorn server on {host}:{port}")
    logger.info(f"Auto-reload: {auto_reload}")
    logger.info("="*80)
    
    # Start server with environment-specific configuration
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=auto_reload,
        log_level="info"
    )
