"""
Stock management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models
from ..schemas import StockResponse, StockCreate, StockUpdate, StockTransResponse, StockTransCreate
from ..auth import require_auth

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Stock CRUD operations
@router.get("/", response_class=HTMLResponse)
async def stocks_page(request: Request, db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Stocks management page"""
    if user is None:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/auth/login", status_code=302)
    
    stocks = db.query(models.Stock).all()
    return templates.TemplateResponse("stocks.html", {
        "request": request,
        "stocks": stocks,
        "user": user
    })

@router.get("/api/stocks", response_model=List[StockResponse])
async def get_stocks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all stocks"""
    stocks = db.query(models.Stock).offset(skip).limit(limit).all()
    return stocks

@router.get("/api/stocks/{stock_id}", response_model=StockResponse)
async def get_stock(stock_id: int, db: Session = Depends(get_db)):
    """Get a specific stock"""
    stock = db.query(models.Stock).filter(models.Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

@router.post("/api/stocks", response_model=StockResponse)
async def create_stock(stock: StockCreate, db: Session = Depends(get_db)):
    """Create a new stock"""
    # Check if stock already exists
    existing_stock = db.query(models.Stock).filter(models.Stock.stick == stock.stick).first()
    if existing_stock:
        raise HTTPException(status_code=400, detail="Stock with this ticker already exists")
    
    db_stock = models.Stock(**stock.dict())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

@router.put("/api/stocks/{stock_id}", response_model=StockResponse)
async def update_stock(stock_id: int, stock: StockUpdate, db: Session = Depends(get_db)):
    """Update a stock"""
    db_stock = db.query(models.Stock).filter(models.Stock.id == stock_id).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    for field, value in stock.dict(exclude_unset=True).items():
        setattr(db_stock, field, value)
    
    db.commit()
    db.refresh(db_stock)
    return db_stock

@router.delete("/api/stocks/{stock_id}")
async def delete_stock(stock_id: int, db: Session = Depends(get_db)):
    """Delete a stock"""
    stock = db.query(models.Stock).filter(models.Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    db.delete(stock)
    db.commit()
    return {"message": "Stock deleted successfully"}

# Stock transactions
@router.get("/api/transactions", response_model=List[StockTransResponse])
async def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all stock transactions"""
    transactions = db.query(models.StockTrans).offset(skip).limit(limit).all()
    return transactions

@router.post("/api/transactions", response_model=StockTransResponse)
async def create_transaction(transaction: StockTransCreate, db: Session = Depends(get_db)):
    """Create a new stock transaction"""
    db_transaction = models.StockTrans(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction
