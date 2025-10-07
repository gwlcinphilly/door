"""
Information management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models
from ..models import information_tags
from ..schemas import InformationResponse, InformationCreate, InformationUpdate, CommentResponse, CommentCreate
from ..source_detection import detect_source
from ..auth import require_auth

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Information CRUD operations
@router.get("/", response_class=HTMLResponse)
async def information_page(
    request: Request, 
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
    source: Optional[str] = None,
    days: Optional[str] = "1",
    no_tag: Optional[bool] = False,
    check_tag: Optional[bool] = False
):
    """Information management page with filtering"""
    if user is None:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/auth/login", status_code=302)
    
    from datetime import datetime, timedelta
    from sqlalchemy import and_, or_
    
    # Base queryset for information entries
    information_query = db.query(models.Information)
    
    # Apply source filter if selected
    if source:
        information_query = information_query.join(models.InfoSource).filter(models.InfoSource.short == source)
    
    # Apply tag filters (mutually exclusive)
    # If "No Tag" is selected, it takes precedence over specific tag filters
    if no_tag:
        # Filter entries that have no tags in the many-to-many relationship
        information_query = information_query.outerjoin(information_tags).filter(information_tags.c.infotag_id.is_(None))
    elif check_tag:
        # Only apply specific tag filter if "No Tag" is not selected
        # Filter entries that have the "check" tag
        check_tag_obj = db.query(models.InfoTag).filter(models.InfoTag.tag == 'check').first()
        if check_tag_obj:
            information_query = information_query.join(information_tags).filter(information_tags.c.infotag_id == check_tag_obj.id)
    
    # Apply days filter if not "all"
    if days != 'all':
        try:
            days_int = int(days)
            cutoff_date = datetime.now().date() - timedelta(days=days_int)
            information_query = information_query.filter(models.Information.date >= cutoff_date)
        except ValueError:
            # If invalid days value, default to 1 day
            days_int = 1
            cutoff_date = datetime.now().date() - timedelta(days=days_int)
            information_query = information_query.filter(models.Information.date >= cutoff_date)
    
    # Order the results by ID (newest entries first)
    information_query = information_query.order_by(models.Information.id.desc())
    
    # Get all info sources for the filter
    info_sources = db.query(models.InfoSource).order_by(models.InfoSource.name).all()
    
    # Get all info tags
    info_tags = db.query(models.InfoTag).order_by(models.InfoTag.name).all()
    
    # Calculate filter statistics
    total_count = db.query(models.Information).count()
    filtered_count = information_query.count()
    
    # Get date range info
    oldest_entry = db.query(models.Information).order_by(models.Information.date).first()
    newest_entry = db.query(models.Information).order_by(models.Information.date.desc()).first()
    
    return templates.TemplateResponse("information.html", {
        "request": request,
        "information": information_query.all(),
        "info_sources": info_sources,
        "info_tags": info_tags,
        "selected_source": source,
        "selected_days": days,
        "no_tag_filter": no_tag,
        "check_tag_filter": check_tag,
        "total_count": total_count,
        "filtered_count": filtered_count,
        "oldest_entry_date": oldest_entry.date if oldest_entry else None,
        "newest_entry_date": newest_entry.date if newest_entry else None,
    })

@router.get("/api/information", response_model=List[InformationResponse])
async def get_information(
    skip: int = 0, 
    limit: int = 100, 
    source: Optional[str] = None,
    days: Optional[str] = "1",
    no_tag: Optional[bool] = False,
    check_tag: Optional[bool] = False,
    db: Session = Depends(get_db)
):
    """Get information entries with filtering"""
    from datetime import datetime, timedelta
    
    # Base queryset for information entries
    information_query = db.query(models.Information)
    
    # Apply source filter if selected
    if source:
        information_query = information_query.join(models.InfoSource).filter(models.InfoSource.short == source)
    
    # Apply tag filters (mutually exclusive)
    # If "No Tag" is selected, it takes precedence over specific tag filters
    if no_tag:
        # Filter entries that have no tags in the many-to-many relationship
        information_query = information_query.outerjoin(information_tags).filter(information_tags.c.infotag_id.is_(None))
    elif check_tag:
        # Only apply specific tag filter if "No Tag" is not selected
        # Filter entries that have the "check" tag
        check_tag_obj = db.query(models.InfoTag).filter(models.InfoTag.tag == 'check').first()
        if check_tag_obj:
            information_query = information_query.join(information_tags).filter(information_tags.c.infotag_id == check_tag_obj.id)
    
    # Apply days filter if not "all"
    if days != 'all':
        try:
            days_int = int(days)
            cutoff_date = datetime.now().date() - timedelta(days=days_int)
            information_query = information_query.filter(models.Information.date >= cutoff_date)
        except ValueError:
            # If invalid days value, default to 1 day
            days_int = 1
            cutoff_date = datetime.now().date() - timedelta(days=days_int)
            information_query = information_query.filter(models.Information.date >= cutoff_date)
    
    # Order the results by ID (newest entries first)
    information_query = information_query.order_by(models.Information.id.desc())
    
    # Apply pagination with eager loading of tags
    from sqlalchemy.orm import joinedload
    information = information_query.options(joinedload(models.Information.tags)).offset(skip).limit(limit).all()
    return information

@router.get("/api/information/{info_id}", response_model=InformationResponse)
async def get_information_item(info_id: int, db: Session = Depends(get_db)):
    """Get a specific information entry"""
    from sqlalchemy.orm import joinedload
    
    info = db.query(models.Information).options(joinedload(models.Information.tags)).filter(models.Information.id == info_id).first()
    if not info:
        raise HTTPException(status_code=404, detail="Information not found")
    return info

@router.post("/api/information", response_model=InformationResponse)
async def create_information(info: InformationCreate, db: Session = Depends(get_db)):
    """Create a new information entry with automatic source detection"""
    try:
        # Check if URL already exists
        existing_info = db.query(models.Information).filter(models.Information.url == info.url).first()
        if existing_info:
            raise HTTPException(status_code=400, detail="Information with this URL already exists")
        
        # Handle tag updates if provided
        tag_ids = getattr(info, 'tag_ids', None)
        print(f"DEBUG: tag_ids received: {tag_ids}")
        
        # Run source detection to get title, content, and source
        try:
            detection_result = detect_source(info.url)
            print(f"DEBUG: Source detection result: {detection_result}")
        except Exception as e:
            print(f"DEBUG: Source detection failed: {e}")
            detection_result = {'success': False, 'error': str(e)}
        
        # Create the information entry with explicit date and updated_at
        from datetime import datetime, timezone
        info_data = info.dict(exclude={'tag_ids'})
        now = datetime.now(timezone.utc)
        info_data['date'] = now
        info_data['updated_at'] = now
        
        # Use detected data if available, otherwise use provided/default values
        if detection_result.get('success'):
            info_data['title'] = detection_result.get('title', info_data.get('title', f"Entry from {info_data['url']}"))
            info_data['content'] = detection_result.get('content', info_data.get('content', f"Content from {info_data['url']}"))
            # Note: We don't automatically set source_id from detection as it might not be properly mapped
        else:
            # Provide default values for required fields if not provided
            if not info_data.get('title'):
                info_data['title'] = f"Entry from {info_data['url']}"
            if not info_data.get('content'):
                info_data['content'] = f"Content from {info_data['url']}"
        
        if not info_data.get('source_id'):
            info_data['source_id'] = 1  # Default to YouTube
        
        db_info = models.Information(**info_data)
        db.add(db_info)
        db.commit()
        db.refresh(db_info)
        
        # Add tags if provided
        if tag_ids:
            tag_ids_list = [int(tid.strip()) for tid in tag_ids.split(',') if tid.strip()]
            print(f"DEBUG: tag_ids_list: {tag_ids_list}")
            new_tags = db.query(models.InfoTag).filter(models.InfoTag.id.in_(tag_ids_list)).all()
            print(f"DEBUG: new_tags found: {[tag.id for tag in new_tags]}")
            db_info.tags.extend(new_tags)
            db.commit()
        
        # Refresh and eager load tags to avoid relationship issues
        from sqlalchemy.orm import joinedload
        db.refresh(db_info)
        db_info = db.query(models.Information).options(joinedload(models.Information.tags)).filter(models.Information.id == db_info.id).first()
        
        return db_info
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating information: {str(e)}")

@router.put("/api/information/{info_id}", response_model=InformationResponse)
async def update_information(info_id: int, info: InformationUpdate, db: Session = Depends(get_db)):
    """Update an information entry"""
    db_info = db.query(models.Information).filter(models.Information.id == info_id).first()
    if not db_info:
        raise HTTPException(status_code=404, detail="Information not found")
    
    # Handle tag updates if provided
    tag_ids = getattr(info, 'tag_ids', None)
    print(f"DEBUG: tag_ids received: {tag_ids}")
    if tag_ids is not None:
        # Clear existing tags
        db_info.tags.clear()
        
        # Add new tags
        if tag_ids:
            tag_ids_list = [int(tid.strip()) for tid in tag_ids.split(',') if tid.strip()]
            print(f"DEBUG: tag_ids_list: {tag_ids_list}")
            new_tags = db.query(models.InfoTag).filter(models.InfoTag.id.in_(tag_ids_list)).all()
            print(f"DEBUG: new_tags found: {[tag.id for tag in new_tags]}")
            db_info.tags.extend(new_tags)
    
    # Update other fields
    for field, value in info.dict(exclude_unset=True, exclude={'tag_ids'}).items():
        setattr(db_info, field, value)
    
    db.commit()
    
    # Refresh and eager load tags to avoid relationship issues
    from sqlalchemy.orm import joinedload
    db.refresh(db_info)
    db_info = db.query(models.Information).options(joinedload(models.Information.tags)).filter(models.Information.id == db_info.id).first()
    
    return db_info

@router.delete("/api/information/{info_id}")
async def delete_information(info_id: int, db: Session = Depends(get_db)):
    """Delete an information entry"""
    info = db.query(models.Information).filter(models.Information.id == info_id).first()
    if not info:
        raise HTTPException(status_code=404, detail="Information not found")
    
    db.delete(info)
    db.commit()
    return {"message": "Information deleted successfully"}

# InfoSource management endpoints
@router.post("/api/sources")
async def create_or_update_source(source_data: dict, db: Session = Depends(get_db)):
    """Create or update an InfoSource"""
    try:
        source_id = source_data.get('id')
        short = source_data.get('short')
        name = source_data.get('name')
        description = source_data.get('description', '')
        
        if not short or not name:
            raise HTTPException(status_code=400, detail="Short code and name are required")
        
        if source_id:
            # Update existing source
            source = db.query(models.InfoSource).filter(models.InfoSource.id == source_id).first()
            if not source:
                raise HTTPException(status_code=404, detail="Source not found")
            source.short = short
            source.name = name
            source.description = description
        else:
            # Create new source
            source = models.InfoSource(short=short, name=name, description=description)
            db.add(source)
        
        db.commit()
        db.refresh(source)
        return {"message": "Source saved successfully", "source": source}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# InfoTag management endpoints
@router.post("/api/tags")
async def create_or_update_tag(tag_data: dict, db: Session = Depends(get_db)):
    """Create or update an InfoTag"""
    try:
        tag_id = tag_data.get('id')
        tag_code = tag_data.get('tag')
        name = tag_data.get('name')
        description = tag_data.get('description', '')
        
        if not tag_code or not name:
            raise HTTPException(status_code=400, detail="Tag code and name are required")
        
        if tag_id:
            # Update existing tag
            tag = db.query(models.InfoTag).filter(models.InfoTag.id == tag_id).first()
            if not tag:
                raise HTTPException(status_code=404, detail="Tag not found")
            tag.tag = tag_code
            tag.name = name
            tag.description = description
        else:
            # Create new tag
            tag = models.InfoTag(tag=tag_code, name=name, description=description)
            db.add(tag)
        
        db.commit()
        db.refresh(tag)
        return {"message": "Tag saved successfully", "tag": tag}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Update all documents endpoint
@router.post("/api/update-all")
async def update_all_documents(db: Session = Depends(get_db)):
    """Update all information entries from their sources"""
    try:
        # This would implement the same logic as the Django version
        # For now, just return a success message
        return {"message": "Update all documents functionality not yet implemented"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Refresh metadata from URL endpoint
@router.post("/api/information/{info_id}/refresh")
async def refresh_information_metadata(info_id: int, db: Session = Depends(get_db)):
    """Refresh metadata for an existing information entry by re-detecting from URL"""
    try:
        # Get the existing information entry
        info = db.query(models.Information).filter(models.Information.id == info_id).first()
        if not info:
            raise HTTPException(status_code=404, detail="Information entry not found")
        
        # Use standalone source detection to get fresh metadata
        result = detect_source(info.url)
        
        if result['success']:
            # Update the information entry with fresh metadata
            info.title = result['title']
            info.content = result['content']
            
            # Commit the changes
            db.commit()
            db.refresh(info)
            
            return {
                "message": "Metadata refreshed successfully",
                "information": {
                    "id": info.id,
                    "title": info.title,
                    "content": info.content,
                    "url": info.url,
                    "date": info.date
                }
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to refresh metadata: {result.get('error', 'Unknown error')}")
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Metadata detection endpoint (without creating entry)
@router.post("/api/detect-metadata")
async def detect_metadata_endpoint(url: str):
    """Detect source and extract metadata from URL without creating entry"""
    try:
        # Use standalone source detection (no Django dependencies)
        result = detect_source(url)
        
        if result['success']:
            return {
                "success": True,
                "detected_data": result
            }
        else:
            return {
                "success": False,
                "error": result.get('error', 'Unknown error')
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metadata detection failed: {str(e)}")

# Source detection endpoint (creates entry)
@router.post("/api/detect-source")
async def detect_source_endpoint(url: str, db: Session = Depends(get_db)):
    """Detect source and extract metadata from URL and create entry"""
    try:
        # Use standalone source detection (no Django dependencies)
        result = detect_source(url)
        
        if result['success']:
            # Create information entry with detected metadata
            info_data = InformationCreate(
                url=result['url'],
                title=result['title'],
                content=result['content'],
                source_id=1  # Default source, you might want to map this properly
            )
            
            # Create the information entry with explicit date and updated_at
            from datetime import datetime, timezone
            info_dict = info_data.dict()
            now = datetime.now(timezone.utc)
            info_dict['date'] = now
            info_dict['updated_at'] = now
            
            db_info = models.Information(**info_dict)
            db.add(db_info)
            db.commit()
            db.refresh(db_info)
            
            return {
                "success": True,
                "detected_data": result,
                "created_info": db_info
            }
        else:
            return {
                "success": False,
                "error": result.get('error', 'Unknown error')
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Source detection failed: {str(e)}")

# Comments
@router.get("/api/information/{info_id}/comments", response_model=List[CommentResponse])
async def get_comments(info_id: int, db: Session = Depends(get_db)):
    """Get comments for an information entry"""
    comments = db.query(models.Comment).filter(models.Comment.information_id == info_id).all()
    return comments

@router.post("/api/information/{info_id}/comments", response_model=CommentResponse)
async def create_comment(info_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    """Create a comment for an information entry"""
    try:
        # Check if information entry exists
        info = db.query(models.Information).filter(models.Information.id == info_id).first()
        if not info:
            raise HTTPException(status_code=404, detail="Information entry not found")
        
        # Create comment with explicit date and updated_at
        from datetime import datetime, timezone, date
        comment_data = comment.dict()
        comment_data['information_id'] = info_id
        comment_data['date'] = date.today()
        comment_data['updated_at'] = datetime.now(timezone.utc)
        
        db_comment = models.Comment(**comment_data)
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating comment: {str(e)}")
