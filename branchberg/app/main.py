"""FastAPI backend with Stripe & Gumroad webhooks and Universal Income Ingest."""

import os
import sys
import uuid
from datetime import datetime
from typing import List, Optional
from io import StringIO
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd

from .database import init_db, get_db, RevenueEvent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    yield


app = FastAPI(title="BranchOS Revenue API", lifespan=lifespan)

# CORS middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ManualTransaction(BaseModel):
    """Manual transaction entry."""

    amount: float = Field(..., description="Transaction amount in dollars")
    currency: str = Field(default="USD", description="Currency code")
    customer_email: Optional[str] = Field(None, description="Customer email")
    customer_id: Optional[str] = Field(None, description="Customer ID")
    entity: Optional[str] = Field(None, description="Business entity")
    description: Optional[str] = Field(None, description="Transaction description")


class RevenueEventResponse(BaseModel):
    """Revenue event response model."""

    id: str
    event_id: str
    provider: str
    event_type: str
    amount_cents: int
    amount_dollars: float
    currency: str
    customer_email: Optional[str]
    customer_id: Optional[str]
    entity: Optional[str]
    created_at: datetime
    processed_at: datetime
    metadata: dict

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        data = {
            "id": obj.id,
            "event_id": obj.event_id,
            "provider": obj.provider,
            "event_type": obj.event_type,
            "amount_cents": obj.amount_cents,
            "amount_dollars": obj.amount_cents / 100.0,
            "currency": obj.currency,
            "customer_email": obj.customer_email,
            "customer_id": obj.customer_id,
            "entity": obj.entity,
            "created_at": obj.created_at,
            "processed_at": obj.processed_at,
            "metadata": obj.event_metadata or {},
        }
        return cls(**data)


class RevenueSummary(BaseModel):
    """Revenue summary response."""

    total_cents: int
    total_dollars: float
    count: int
    currency: str = "USD"


# Endpoints
@app.get("/")
def read_root():
    """Root endpoint."""
    return {"status": "ok", "service": "BranchOS Revenue API"}


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "ok",
        "service": "BranchOS Revenue API",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/version")
def version_info():
    """Version information endpoint."""
    return {
        "version": "1.0.0",
        "service": "BranchOS Revenue API",
        "python_version": sys.version.split()[0],
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
    }


@app.post("/ingest/manual", response_model=RevenueEventResponse)
def ingest_manual_transaction(
    transaction: ManualTransaction, db: Session = Depends(get_db)
):
    """
    Add a manual revenue transaction.

    This endpoint allows manual entry of revenue events that don't come
    from automated providers like Stripe or Gumroad.
    """
    # Convert dollars to cents
    amount_cents = int(transaction.amount * 100)

    # Create unique IDs
    event_id = f"manual_{uuid.uuid4().hex[:16]}"
    record_id = str(uuid.uuid4())

    # Create revenue event
    revenue_event = RevenueEvent(
        id=record_id,
        event_id=event_id,
        provider="manual",
        event_type="manual_entry",
        amount_cents=amount_cents,
        currency=transaction.currency,
        customer_email=transaction.customer_email,
        customer_id=transaction.customer_id,
        entity=transaction.entity,
        event_metadata={"description": transaction.description}
        if transaction.description
        else {},
        created_at=datetime.utcnow(),
        processed_at=datetime.utcnow(),
    )

    db.add(revenue_event)
    db.commit()
    db.refresh(revenue_event)

    return RevenueEventResponse.from_orm(revenue_event)


@app.post("/ingest/csv")
def ingest_csv_transactions(
    file: UploadFile = File(...),
    amount_column: str = Form(...),
    currency_column: Optional[str] = Form(None),
    email_column: Optional[str] = Form(None),
    entity_column: Optional[str] = Form(None),
    description_column: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Upload CSV file and ingest transactions with column mapping.

    The CSV file should have headers. You specify which columns contain
    the relevant data.
    """
    try:
        # Read CSV file
        contents = file.file.read().decode("utf-8")
        df = pd.read_csv(StringIO(contents))

        # Validate required column exists
        if amount_column not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Amount column '{amount_column}' not found in CSV",
            )

        # Process each row
        created_count = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                # Extract amount (handle both float and string formats)
                amount_str = (
                    str(row[amount_column]).replace("$", "").replace(",", "").strip()
                )
                amount = float(amount_str)
                amount_cents = int(amount * 100)

                # Extract other fields if columns are specified
                currency = (
                    row[currency_column]
                    if currency_column and currency_column in df.columns
                    else "USD"
                )
                email = (
                    row[email_column]
                    if email_column and email_column in df.columns
                    else None
                )
                entity = (
                    row[entity_column]
                    if entity_column and entity_column in df.columns
                    else None
                )
                description = (
                    row[description_column]
                    if description_column and description_column in df.columns
                    else None
                )

                # Convert to string and handle NaN
                if pd.isna(email):
                    email = None
                if pd.isna(entity):
                    entity = None
                if pd.isna(description):
                    description = None

                # Create unique IDs
                event_id = f"csv_{uuid.uuid4().hex[:16]}"
                record_id = str(uuid.uuid4())

                # Create revenue event
                revenue_event = RevenueEvent(
                    id=record_id,
                    event_id=event_id,
                    provider="manual",
                    event_type="csv_import",
                    amount_cents=amount_cents,
                    currency=currency,
                    customer_email=email,
                    entity=entity,
                    event_metadata={"description": description, "csv_row": idx + 1}
                    if description
                    else {"csv_row": idx + 1},
                    created_at=datetime.utcnow(),
                    processed_at=datetime.utcnow(),
                )

                db.add(revenue_event)
                created_count += 1

            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")

        # Commit all transactions
        db.commit()

        return {
            "success": True,
            "created_count": created_count,
            "total_rows": len(df),
            "errors": errors if errors else None,
        }

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")
    finally:
        file.file.close()


@app.get("/revenue/summary", response_model=RevenueSummary)
def get_revenue_summary(db: Session = Depends(get_db)):
    """
    Get total revenue summary (total amount and transaction count).
    """
    # Query total and count
    result = db.query(
        func.sum(RevenueEvent.amount_cents).label("total_cents"),
        func.count(RevenueEvent.id).label("count"),
    ).first()

    total_cents = result.total_cents if result.total_cents else 0
    count = result.count if result.count else 0

    return RevenueSummary(
        total_cents=total_cents, total_dollars=total_cents / 100.0, count=count
    )


@app.get("/revenue/events", response_model=List[RevenueEventResponse])
def get_revenue_events(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    """
    Get recent revenue transactions.

    Parameters:
    - limit: Maximum number of events to return (default: 50)
    - offset: Number of events to skip for pagination (default: 0)
    """
    events = (
        db.query(RevenueEvent)
        .order_by(RevenueEvent.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    return [RevenueEventResponse.from_orm(event) for event in events]


# Webhook endpoints (placeholders for future Stripe/Gumroad integration)
@app.post("/webhooks/stripe")
def stripe_webhook():
    """Stripe webhook endpoint (to be implemented)."""
    return {"status": "not_implemented", "message": "Stripe webhook coming soon"}


@app.post("/webhooks/gumroad")
def gumroad_webhook():
    """Gumroad webhook endpoint (to be implemented)."""
    return {"status": "not_implemented", "message": "Gumroad webhook coming soon"}
