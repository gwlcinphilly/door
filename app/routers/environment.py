"""
Environment and system information endpoints
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database import get_db
from ..config import get_environment_info, is_local, is_render, get_feature_status
from ..auth import require_auth

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def environment_page(request: Request, db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Environment and system information page"""
    if user is None:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/auth/login", status_code=302)
    
    # Get comprehensive environment information
    env_info = get_environment_info()
    
    return templates.TemplateResponse("environment.html", {
        "request": request,
        "user": user,
        "env_info": env_info,
        "is_local": is_local(),
        "is_render": is_render()
    })

@router.get("/api/environment")
async def get_environment_api():
    """Get environment information as JSON"""
    return get_environment_info()

@router.get("/api/features")
async def get_features_api():
    """Get available features based on environment"""
    env_info = get_environment_info()
    return {
        "environment": env_info["environment"],
        "features": env_info["config"]["features"],
        "restrictions": env_info["config"]["restrictions"]
    }
