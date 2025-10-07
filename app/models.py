"""
SQLAlchemy models for the Door application
Based on the original Django models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Boolean, Table, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date
from .database import Base

# Association tables for many-to-many relationships
information_tags = Table(
    'information_information_tags',
    Base.metadata,
    Column('information_id', Integer, ForeignKey('information_information.id'), primary_key=True),
    Column('infotag_id', Integer, ForeignKey('information_infotag.id'), primary_key=True)
)

# Stock Models
class StockTypes(Base):
    __tablename__ = "stocktypes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, index=True)
    fullname = Column(String(100))
    description = Column(Text)
    
    def __repr__(self):
        return f"<StockTypes(name='{self.name}', fullname='{self.fullname}')>"

class StockStatus(Base):
    __tablename__ = "stockstatus"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(20), unique=True, index=True)
    name = Column(String(100))
    description = Column(Text)
    
    def __repr__(self):
        return f"<StockStatus(status='{self.status}', name='{self.name}')>"

class StockTags(Base):
    __tablename__ = "stocktags"
    
    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String(20), unique=True, index=True)
    name = Column(String(100))
    description = Column(Text)
    
    def __repr__(self):
        return f"<StockTags(tag='{self.tag}', name='{self.name}')>"

class Stock(Base):
    __tablename__ = "stocks_stock"
    
    id = Column(Integer, primary_key=True, index=True)
    stick = Column(String(20), unique=True, index=True)  # ticker symbol
    stock_type = Column(String(10), default='stock')
    status = Column(String(10), default='monitor')
    price = Column(Numeric(10, 2), nullable=True)
    quantity = Column(Numeric(10, 2), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    transactions = relationship("StockTrans", back_populates="stock")
    info_stocks = relationship("InfoStocks", back_populates="stock")
    
    def __repr__(self):
        return f"<Stock(stick='{self.stick}', type='{self.stock_type}', status='{self.status}')>"

class StockAccount(Base):
    __tablename__ = "stocks_stockaccount"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    account_number = Column(String(50), unique=True)
    company = Column(String(100))
    balance = Column(Numeric(12, 2), nullable=True)
    
    # Relationships
    transactions = relationship("StockTrans", back_populates="account")
    
    def __repr__(self):
        return f"<StockAccount(name='{self.name}', company='{self.company}')>"

class StockTrans(Base):
    __tablename__ = "stocks_stocktrans"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks_stock.id"))
    operation = Column(String(4))  # 'buy' or 'sell'
    order_date = Column(Date)
    execute_date = Column(Date, nullable=True)
    price = Column(Numeric(10, 2))
    quantity = Column(Integer)
    total_amount = Column(Numeric(12, 2), nullable=True)
    notes = Column(Text)
    account_id = Column(Integer, ForeignKey("stocks_stockaccount.id"), nullable=True)
    
    # Relationships
    stock = relationship("Stock", back_populates="transactions")
    account = relationship("StockAccount", back_populates="transactions")
    
    def __repr__(self):
        return f"<StockTrans(operation='{self.operation}', quantity={self.quantity}, price={self.price})>"

# Information Models
class InfoSource(Base):
    __tablename__ = "information_infosource"
    
    id = Column(Integer, primary_key=True, index=True)
    short = Column(String(20), unique=True, index=True)
    name = Column(String(100))
    description = Column(Text)
    
    # Relationships
    informations = relationship("Information", back_populates="source")
    source_maps = relationship("InfoSourceMap", back_populates="source")
    
    def __repr__(self):
        return f"<InfoSource(short='{self.short}', name='{self.name}')>"

class InfoTag(Base):
    __tablename__ = "information_infotag"
    
    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String(20), unique=True, index=True)
    name = Column(String(100))
    description = Column(Text)
    
    # Relationships
    informations = relationship("Information", secondary=information_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<InfoTag(tag='{self.tag}', name='{self.name}')>"

class InfoSourceMap(Base):
    __tablename__ = "information_infosourcemap"
    
    id = Column(Integer, primary_key=True, index=True)
    website = Column(String(255), unique=True, index=True)
    source_id = Column(Integer, ForeignKey("information_infosource.id"))
    description = Column(Text)
    
    # Relationships
    source = relationship("InfoSource", back_populates="source_maps")
    
    def __repr__(self):
        return f"<InfoSourceMap(website='{self.website}')>"

class Information(Base):
    __tablename__ = "information_information"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), unique=True, index=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    source_id = Column(Integer, ForeignKey("information_infosource.id"), nullable=True)
    title = Column(String(255))
    content = Column(Text)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    source = relationship("InfoSource", back_populates="informations")
    tags = relationship("InfoTag", secondary=information_tags, back_populates="informations")
    comments = relationship("Comment", back_populates="information")
    info_stocks = relationship("InfoStocks", back_populates="link")
    
    def __repr__(self):
        return f"<Information(url='{self.url}', title='{self.title}')>"

class Comment(Base):
    __tablename__ = "information_comment"
    
    id = Column(Integer, primary_key=True, index=True)
    information_id = Column(Integer, ForeignKey("information_information.id"))
    date = Column(Date, server_default=func.current_date())
    content = Column(Text)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    information = relationship("Information", back_populates="comments")
    
    def __repr__(self):
        return f"<Comment(information_id={self.information_id})>"

class InfoStocksType(Base):
    __tablename__ = "information_infostockstype"
    
    id = Column(Integer, primary_key=True, index=True)
    typename = Column(String(20), unique=True, index=True)
    name = Column(String(100))
    description = Column(Text)
    
    # Relationships
    info_stocks = relationship("InfoStocks", back_populates="key_type")
    
    def __repr__(self):
        return f"<InfoStocksType(typename='{self.typename}', name='{self.name}')>"

class InfoStocks(Base):
    __tablename__ = "information_infostocks"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks_stock.id"))
    link_id = Column(Integer, ForeignKey("information_information.id"))
    date = Column(Date, server_default=func.current_date())
    title = Column(String(255))
    key_date = Column(Date, nullable=True)
    key_type_id = Column(Integer, ForeignKey("information_infostockstype.id"))
    key_value = Column(String(255))
    content = Column(Text)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    stock = relationship("Stock", back_populates="info_stocks")
    link = relationship("Information", back_populates="info_stocks")
    key_type = relationship("InfoStocksType", back_populates="info_stocks")
    
    def __repr__(self):
        return f"<InfoStocks(stock_id={self.stock_id}, title='{self.title}')>"

# Notes Models
class NotesTypes(Base):
    __tablename__ = "notes_notestypes"
    
    id = Column(Integer, primary_key=True, index=True)
    short = Column(String(20), unique=True, index=True)
    name = Column(String(100))
    description = Column(Text)
    
    # Relationships
    notes = relationship("Notes", back_populates="category")
    
    def __repr__(self):
        return f"<NotesTypes(short='{self.short}', name='{self.name}')>"

class NotesTag(Base):
    __tablename__ = "notes_notestag"
    
    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String(20), unique=True, index=True)
    name = Column(String(100))
    description = Column(Text)
    
    # Relationships
    notes = relationship("Notes", back_populates="tag")
    
    def __repr__(self):
        return f"<NotesTag(tag='{self.tag}', name='{self.name}')>"

class Notes(Base):
    __tablename__ = "notes_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    timestamp = Column(DateTime(timezone=True), nullable=False)
    date = Column(Date, nullable=False)
    category_id = Column(Integer, ForeignKey("notes_notestypes.id"), nullable=True)
    tag_id = Column(Integer, ForeignKey("notes_notestag.id"), nullable=True)
    content = Column(Text, nullable=False, default="")
    
    # Relationships
    category = relationship("NotesTypes", back_populates="notes")
    tag = relationship("NotesTag", back_populates="notes")
    updates = relationship("Update", back_populates="notes")
    
    def __init__(self, **kwargs):
        # Set default values for timestamp and date if not provided
        if 'timestamp' not in kwargs:
            kwargs['timestamp'] = datetime.now()
        if 'date' not in kwargs:
            kwargs['date'] = date.today()
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f"<Notes(title='{self.title}', category_id={self.category_id})>"

class Update(Base):
    __tablename__ = "notes_update"
    
    id = Column(Integer, primary_key=True, index=True)
    notes_id = Column(Integer, ForeignKey("notes_notes.id"))
    date = Column(Date, server_default=func.current_date())
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    content = Column(Text)
    
    # Relationships
    notes = relationship("Notes", back_populates="updates")
    
    def __repr__(self):
        return f"<Update(notes_id={self.notes_id}, date='{self.date}')>"
