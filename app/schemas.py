"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

# Stock schemas
class StockBase(BaseModel):
    stick: str
    stock_type: str = "stock"
    status: str = "monitor"
    price: Optional[Decimal] = None
    quantity: Optional[Decimal] = None

class StockCreate(StockBase):
    pass

class StockUpdate(BaseModel):
    stick: Optional[str] = None
    stock_type: Optional[str] = None
    status: Optional[str] = None
    price: Optional[Decimal] = None
    quantity: Optional[Decimal] = None

class StockResponse(StockBase):
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Stock Transaction schemas
class StockTransBase(BaseModel):
    operation: str  # 'buy' or 'sell'
    order_date: date
    execute_date: Optional[date] = None
    price: Decimal
    quantity: int
    total_amount: Optional[Decimal] = None
    notes: Optional[str] = None
    account_id: Optional[int] = None

class StockTransCreate(StockTransBase):
    stock_id: int

class StockTransResponse(StockTransBase):
    id: int
    stock_id: int
    
    class Config:
        from_attributes = True

# Information schemas
class InformationBase(BaseModel):
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    source_id: Optional[int] = None

class InformationCreate(InformationBase):
    tag_ids: Optional[str] = None  # Comma-separated list of tag IDs

class InformationUpdate(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    source_id: Optional[int] = None
    tag_ids: Optional[str] = None  # Comma-separated list of tag IDs

# InfoTag schemas
class InfoTagResponse(BaseModel):
    id: int
    tag: str
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class InformationResponse(InformationBase):
    id: int
    date: datetime
    updated_at: datetime
    tags: List[InfoTagResponse] = []
    
    class Config:
        from_attributes = True

# Comment schemas
class CommentBase(BaseModel):
    content: Optional[str] = None

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    information_id: int
    date: date
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Notes schemas
class NotesBase(BaseModel):
    title: str
    content: Optional[str] = None
    category_id: Optional[int] = None
    tag_id: Optional[int] = None

class NotesCreate(NotesBase):
    pass

class NotesUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None
    tag_id: Optional[int] = None

class NotesResponse(NotesBase):
    id: int
    timestamp: datetime
    date: date
    
    class Config:
        from_attributes = True

# Update schemas
class UpdateBase(BaseModel):
    content: Optional[str] = None

class UpdateCreate(UpdateBase):
    pass

class UpdateResponse(UpdateBase):
    id: int
    notes_id: int
    date: date
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Source detection schema
class SourceDetectionRequest(BaseModel):
    url: str

class SourceDetectionResponse(BaseModel):
    success: bool
    source: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None

# Notes Types (Categories) schemas
class NotesTypesResponse(BaseModel):
    id: int
    short: str
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

# Notes Tags schemas
class NotesTagResponse(BaseModel):
    id: int
    tag: str
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True
