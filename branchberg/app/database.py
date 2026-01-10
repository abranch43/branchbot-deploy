"""Database configuration and models for BranchOS revenue tracking."""
import os
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./branchbot.db")

# SQLite compatibility: replace postgresql:// with sqlite://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ProviderEnum(str, enum.Enum):
    """Revenue provider types."""
    stripe = "stripe"
    gumroad = "gumroad"
    manual = "manual"


class RevenueEvent(Base):
    """Revenue events table - stores all income transactions."""
    __tablename__ = "revenue_events"

    id = Column(String, primary_key=True)  # UUID as string
    event_id = Column(String, unique=True, nullable=False, index=True)
    provider = Column(String, nullable=False)  # stripe, gumroad, manual
    event_type = Column(String, nullable=False)  # e.g., charge.succeeded, sale, manual_entry
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String, default="USD")
    customer_email = Column(String, nullable=True)
    customer_id = Column(String, nullable=True)
    event_metadata = Column(JSON, default={})  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, default=datetime.utcnow)
    entity = Column(String, nullable=True)  # A+ Enterprise LLC or Legacy Unchained Inc


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
