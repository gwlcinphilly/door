"""
API endpoints for the Door application
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models

router = APIRouter()

# Health check
@router.get("/health")
async def health_check():
    """API health check"""
    return {"status": "healthy", "message": "API is running"}

# Database status
@router.get("/database/status")
async def database_status(db: Session = Depends(get_db)):
    """Check database connection status"""
    try:
        db.execute("SELECT 1")
        return {"status": "connected", "message": "Database connection successful"}
    except Exception as e:
        return {"status": "error", "message": f"Database connection failed: {str(e)}"}

# Get database statistics
@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get application statistics"""
    try:
        stats = {
            "stocks": db.query(models.Stock).count(),
            "information": db.query(models.Information).count(),
            "notes": db.query(models.Notes).count(),
            "transactions": db.query(models.StockTrans).count(),
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")
