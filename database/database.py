"""
Database connection e session management
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
from typing import Generator
import os
from dotenv import load_dotenv

# Import con fallback
try:
    from .models import Base
except ImportError:
    from models import Base

load_dotenv()

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/google_ads_automation")

# Engine
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Crea tutte le tabelle nel database"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")


def get_db() -> Generator[Session, None, None]:
    """Dependency per FastAPI - fornisce una session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager per usare session fuori da FastAPI
    
    Usage:
        with get_db_session() as db:
            campaigns = db.query(CampaignMetric).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Test connection
    print(f"🔍 Testing database connection to: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'local'}")
    try:
        init_db()
        
        with get_db_session() as db:
            result = db.execute(text("SELECT 1"))
            print(f"✅ Database connection successful: {result.scalar()}")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
