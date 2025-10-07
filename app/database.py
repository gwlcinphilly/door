"""
Database configuration and connection management
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
# Auto-detect Render environment or use explicit setting
USE_NEON = os.getenv('USE_NEON', 'False').lower() == 'true' or os.getenv('RENDER') is not None

def get_database_url():
    """Get database URL based on environment configuration"""
    # Debug: Print environment variables (remove in production)
    print(f"DEBUG: USE_NEON = {USE_NEON}")
    print(f"DEBUG: USE_NEON env var = {os.getenv('USE_NEON')}")
    print(f"DEBUG: RENDER env var = {os.getenv('RENDER')}")
    
    if USE_NEON:
        # Neon Database Configuration - ALL VALUES MUST BE SET IN .env FILE
        neon_user = os.getenv('NEON_USER')
        neon_password = os.getenv('NEON_PASSWORD')
        neon_host = os.getenv('NEON_HOST')
        neon_port = os.getenv('NEON_PORT', '5432')
        neon_database = os.getenv('NEON_DATABASE_NAME')

        if not all([neon_user, neon_password, neon_host, neon_database]):
            missing = []
            if not neon_user: missing.append('NEON_USER')
            if not neon_password: missing.append('NEON_PASSWORD')
            if not neon_host: missing.append('NEON_HOST')
            if not neon_database: missing.append('NEON_DATABASE_NAME')
            raise ValueError(f"Missing required Neon database configuration: {', '.join(missing)}. Please set these environment variables in Render dashboard.")

        return f"postgresql://{neon_user}:{neon_password}@{neon_host}:{neon_port}/{neon_database}"
    else:
        # Local PostgreSQL Database Configuration
        db_user = os.getenv('DB_USER', 'bdoor_user')
        db_password = os.getenv('DB_PASSWORD', 'bdoor_password')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'bdoor_postgres')

        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Create database engine
DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db() -> Session:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
