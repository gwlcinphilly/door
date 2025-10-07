"""
Settings management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..database import get_db
from .. import models
from ..schemas import NotesTypesResponse, NotesTagResponse

# Request schemas for API endpoints
class CategoryCreate(BaseModel):
    short: str
    name: str
    description: str = ""

class TagCreate(BaseModel):
    tag: str
    name: str
    description: str = ""

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Settings page
@router.get("/", response_class=HTMLResponse)
async def settings_page(request: Request, db: Session = Depends(get_db)):
    """Settings management page"""
    # Get all categories and tags for management
    categories = db.query(models.NotesTypes).all()
    tags = db.query(models.NotesTag).all()
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "categories": categories,
        "tags": tags
    })

# Categories CRUD operations
@router.get("/api/categories", response_model=List[NotesTypesResponse])
async def get_categories(db: Session = Depends(get_db)):
    """Get all note categories"""
    categories = db.query(models.NotesTypes).all()
    return categories

@router.post("/api/categories")
async def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category"""
    # Check if short code already exists
    existing = db.query(models.NotesTypes).filter(models.NotesTypes.short == category_data.short).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this short code already exists")
    
    category = models.NotesTypes(
        short=category_data.short,
        name=category_data.name,
        description=category_data.description
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return {"message": "Category created successfully", "category_id": category.id}

@router.put("/api/categories/{category_id}")
async def update_category(category_id: int, short: str, name: str, description: str = "", db: Session = Depends(get_db)):
    """Update a category"""
    category = db.query(models.NotesTypes).filter(models.NotesTypes.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if short code already exists (excluding current category)
    existing = db.query(models.NotesTypes).filter(
        models.NotesTypes.short == short,
        models.NotesTypes.id != category_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this short code already exists")
    
    category.short = short
    category.name = name
    category.description = description
    db.commit()
    return {"message": "Category updated successfully"}

@router.delete("/api/categories/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category"""
    category = db.query(models.NotesTypes).filter(models.NotesTypes.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category is in use
    notes_count = db.query(models.Notes).filter(models.Notes.category_id == category_id).count()
    if notes_count > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete category. It is used by {notes_count} note(s)")
    
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}

# Tags CRUD operations
@router.get("/api/tags", response_model=List[NotesTagResponse])
async def get_tags(db: Session = Depends(get_db)):
    """Get all note tags"""
    tags = db.query(models.NotesTag).all()
    return tags

@router.post("/api/tags")
async def create_tag(tag_data: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag"""
    # Check if tag code already exists
    existing = db.query(models.NotesTag).filter(models.NotesTag.tag == tag_data.tag).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag with this code already exists")
    
    new_tag = models.NotesTag(
        tag=tag_data.tag,
        name=tag_data.name,
        description=tag_data.description
    )
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return {"message": "Tag created successfully", "tag_id": new_tag.id}

@router.put("/api/tags/{tag_id}")
async def update_tag(tag_id: int, tag: str, name: str, description: str = "", db: Session = Depends(get_db)):
    """Update a tag"""
    tag_obj = db.query(models.NotesTag).filter(models.NotesTag.id == tag_id).first()
    if not tag_obj:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Check if tag code already exists (excluding current tag)
    existing = db.query(models.NotesTag).filter(
        models.NotesTag.tag == tag,
        models.NotesTag.id != tag_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag with this code already exists")
    
    tag_obj.tag = tag
    tag_obj.name = name
    tag_obj.description = description
    db.commit()
    return {"message": "Tag updated successfully"}

@router.delete("/api/tags/{tag_id}")
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """Delete a tag"""
    tag_obj = db.query(models.NotesTag).filter(models.NotesTag.id == tag_id).first()
    if not tag_obj:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Check if tag is in use
    notes_count = db.query(models.Notes).filter(models.Notes.tag_id == tag_id).count()
    if notes_count > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete tag. It is used by {notes_count} note(s)")
    
    db.delete(tag_obj)
    db.commit()
    return {"message": "Tag deleted successfully"}
