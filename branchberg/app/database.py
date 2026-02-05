"""Database configuration and models for BranchOS revenue tracking."""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

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


class PurchaseOrder(Base):
    """Purchase orders table - stores PO lifecycle data."""
    __tablename__ = "purchase_orders"
    __table_args__ = (
        UniqueConstraint(
            "entity",
            "customer_name",
            "po_number",
            name="uq_po_entity_customer_po_number",
        ),
    )

    id = Column(String, primary_key=True)  # UUID as string
    po_number = Column(String, nullable=False)
    customer_id = Column(String, nullable=True)
    customer_name = Column(String, nullable=False)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, nullable=False, default="draft")  # draft, issued, invoiced, paid, cancelled
    entity = Column(String, nullable=False)
    issued_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    record_metadata = Column("metadata", JSON, default={})

    invoices = relationship("Invoice", back_populates="purchase_order")


class Invoice(Base):
    """Invoices table - stores invoices linked to POs."""
    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint(
            "entity",
            "customer_name",
            "invoice_number",
            name="uq_invoice_entity_customer_invoice_number",
        ),
    )

    id = Column(String, primary_key=True)  # UUID as string
    invoice_number = Column(String, nullable=False)
    po_id = Column(String, ForeignKey("purchase_orders.id"), nullable=False, index=True)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, nullable=False, default="draft")  # draft, sent, void, paid
    issued_at = Column(DateTime, nullable=True)
    due_at = Column(DateTime, nullable=True)
    artifact_uri = Column(String, nullable=True)
    entity = Column(String, nullable=False)
    customer_id = Column(String, nullable=True)
    customer_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    record_metadata = Column("metadata", JSON, default={})

    purchase_order = relationship("PurchaseOrder", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice")


class Payment(Base):
    """Payments table - records payment artifacts tied to invoices."""
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint(
            "entity",
            "payment_reference",
            name="uq_payment_entity_reference",
        ),
    )

    id = Column(String, primary_key=True)  # UUID as string
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=False, index=True)
    payment_reference = Column(String, nullable=False)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String, default="USD")
    paid_at = Column(DateTime, nullable=False)
    method = Column(String, nullable=False)
    artifact_uri = Column(String, nullable=False)
    entity = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    record_metadata = Column("metadata", JSON, default={})

    invoice = relationship("Invoice", back_populates="payments")


class AuditLog(Base):
    """Append-only audit log for PO-to-paid lifecycle actions."""
    __tablename__ = "audit_log"

    id = Column(String, primary_key=True)  # UUID as string
    entity = Column(String, nullable=False)
    actor = Column(String, nullable=False)
    action = Column(String, nullable=False)
    po_id = Column(String, nullable=True)
    invoice_id = Column(String, nullable=True)
    payment_id = Column(String, nullable=True)
    from_state = Column(String, nullable=True)
    to_state = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    record_metadata = Column("metadata", JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)


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
