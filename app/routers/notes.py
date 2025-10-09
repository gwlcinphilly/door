"""
Notes management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models
from ..schemas import NotesResponse, NotesCreate, NotesUpdate, UpdateResponse, UpdateCreate
from ..auth import require_auth

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Notes CRUD operations
@router.get("/", response_class=HTMLResponse)
async def notes_page(request: Request, db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Notes management page"""
    if user is None:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/auth/login", status_code=302)
    
    notes = db.query(models.Notes).all()
    return templates.TemplateResponse("notes.html", {
        "request": request,
        "notes": notes
    })

@router.get("/api/notes", response_model=List[NotesResponse])
async def get_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all notes"""
    notes = db.query(models.Notes).offset(skip).limit(limit).all()
    return notes

@router.get("/api/notes/{note_id}", response_model=NotesResponse)
async def get_note(note_id: int, db: Session = Depends(get_db)):
    """Get a specific note"""
    note = db.query(models.Notes).filter(models.Notes.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.post("/api/notes", response_model=NotesResponse)
async def create_note(note: NotesCreate, db: Session = Depends(get_db)):
    """Create a new note"""
    db_note = models.Notes(**note.dict())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@router.put("/api/notes/{note_id}", response_model=NotesResponse)
async def update_note(note_id: int, note: NotesUpdate, db: Session = Depends(get_db)):
    """Update a note"""
    db_note = db.query(models.Notes).filter(models.Notes.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    for field, value in note.dict(exclude_unset=True).items():
        setattr(db_note, field, value)
    
    db.commit()
    db.refresh(db_note)
    return db_note

@router.delete("/api/notes/{note_id}")
async def delete_note(note_id: int, db: Session = Depends(get_db)):
    """Delete a note"""
    note = db.query(models.Notes).filter(models.Notes.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    return {"message": "Note deleted successfully"}

# Note updates
@router.get("/api/notes/{note_id}/updates", response_model=List[UpdateResponse])
async def get_note_updates(note_id: int, db: Session = Depends(get_db)):
    """Get updates for a note"""
    updates = db.query(models.Update).filter(models.Update.notes_id == note_id).all()
    return updates

@router.post("/api/notes/{note_id}/updates", response_model=UpdateResponse)
async def create_note_update(note_id: int, update: UpdateCreate, db: Session = Depends(get_db)):
    """Create an update for a note"""
    update_data = update.dict()
    update_data['notes_id'] = note_id
    
    db_update = models.Update(**update_data)
    db.add(db_update)
    db.commit()
    db.refresh(db_update)
    return db_update
