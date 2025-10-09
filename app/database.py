"""
Database configuration and connection management
Supports three deployment environments with automatic detection
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from app.config import get_environment_type, EnvironmentType

# Load environment variables
load_dotenv()

def get_database_url():
    """
    Get database URL based on environment configuration
    AUTO-DETECTS environment and returns appropriate connection string
    
    LOCAL:  PostgreSQL on localhost (development)
    MIRROR: PostgreSQL in Docker container (internal production)
    RENDER: Neon PostgreSQL (cloud production)
    """
    
    env = get_environment_type()
    
    if env == EnvironmentType.RENDER:
        # RENDER: Neon Cloud Database
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
            raise ValueError(
                f"Missing Neon database configuration: {', '.join(missing)}. "
                f"Please set these environment variables in Render dashboard."
            )

        db_url = f"postgresql://{neon_user}:{neon_password}@{neon_host}:{neon_port}/{neon_database}"
        print(f"🔵 Using RENDER database: Neon PostgreSQL at {neon_host}")
        return db_url
        
    elif env == EnvironmentType.MIRROR:
        # MIRROR: Docker PostgreSQL Container
        # Connection from host application to Docker database container
        db_user = os.getenv('MIRROR_DB_USER', os.getenv('DB_USER', 'bdoor_user'))
        db_password = os.getenv('MIRROR_DB_PASSWORD', os.getenv('DB_PASSWORD', 'bdoor_password'))
        db_host = os.getenv('MIRROR_DB_HOST', os.getenv('DB_HOST', 'localhost'))
        db_port = os.getenv('MIRROR_DB_PORT', os.getenv('DB_PORT', '5432'))
        db_name = os.getenv('MIRROR_DB_NAME', os.getenv('DB_NAME', 'bdoor_postgres'))

        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        print(f"🟢 Using MIRROR database: PostgreSQL (Docker) at {db_host}:{db_port}")
        return db_url
        
    else:  # LOCAL
        # LOCAL: Local PostgreSQL Database
        db_user = os.getenv('DB_USER', 'bdoor_user')
        db_password = os.getenv('DB_PASSWORD', 'bdoor_password')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'bdoor_postgres')

        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        print(f"🟡 Using LOCAL database: PostgreSQL at {db_host}:{db_port}/{db_name}")
        return db_url

# Create database engine
DATABASE_URL = get_database_url()
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
)

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
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
