"""
FastAPI Main Application for Render Deployment
Configured to connect to Neon database for production deployment
"""

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path

# Import routers
from app.routers import stocks, information, notes, api
from app.database import engine, get_db
from app import models

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

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(api.router, prefix="/api", tags=["api"])
app.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
app.include_router(information.router, prefix="/information", tags=["information"])
app.include_router(notes.router, prefix="/notes", tags=["notes"])

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with dashboard overview"""
    return templates.TemplateResponse("index.html", {"request": request})

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
