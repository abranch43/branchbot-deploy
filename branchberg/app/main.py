"""FastAPI backend with Stripe & Gumroad webhooks and Universal Income Ingest."""
import importlib.util
import uuid
from datetime import datetime
from typing import List, Optional
from io import StringIO
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
import pandas as pd

from .database import (
    init_db,
    get_db,
    RevenueEvent,
    PurchaseOrder,
    Invoice,
    Payment,
    AuditLog,
)

APP_NAME = "BranchOS Revenue API"
DEFAULT_VERSION = "0.0.0"


def _load_toml(path: Path) -> Optional[dict]:
    if importlib.util.find_spec("tomllib"):
        import tomllib

        with path.open("rb") as handle:
            return tomllib.load(handle)
    if importlib.util.find_spec("tomli"):
        import tomli

        with path.open("rb") as handle:
            return tomli.load(handle)
    return None


def _find_pyproject(start: Path) -> Optional[Path]:
    for parent in [start, *start.parents]:
        candidate = parent / "pyproject.toml"
        if candidate.is_file():
            return candidate
    return None


def resolve_version() -> str:
    pyproject_path = _find_pyproject(Path(__file__).resolve())
    if not pyproject_path:
        return DEFAULT_VERSION
    try:
        toml_data = _load_toml(pyproject_path)
    except OSError:
        return DEFAULT_VERSION
    if not toml_data:
        return DEFAULT_VERSION
    project_data = toml_data.get("project", {})
    version = project_data.get("version")
    return version or DEFAULT_VERSION


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    yield


app = FastAPI(title=APP_NAME, lifespan=lifespan)

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
            "metadata": obj.event_metadata or {}
        }
        return cls(**data)


class RevenueSummary(BaseModel):
    """Revenue summary response."""
    total_cents: int
    total_dollars: float
    count: int
    currency: str = "USD"


class PurchaseOrderCreate(BaseModel):
    """Purchase order creation model."""
    po_number: str
    customer_name: str
    customer_id: Optional[str] = None
    amount: float
    currency: str = "USD"
    entity: Optional[str] = None
    status: str = "issued"
    issued_at: Optional[datetime] = None
    actor: Optional[str] = None
    reason: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class PurchaseOrderResponse(BaseModel):
    """Purchase order response model."""
    id: str
    po_number: str
    customer_name: str
    customer_id: Optional[str]
    amount_cents: int
    amount_dollars: float
    currency: str
    status: str
    entity: Optional[str]
    issued_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    metadata: dict


class InvoiceCreate(BaseModel):
    """Invoice creation model."""
    invoice_number: str
    amount: float
    currency: str = "USD"
    status: str = "sent"
    issued_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    artifact_uri: Optional[str] = None
    actor: Optional[str] = None
    reason: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class InvoiceResponse(BaseModel):
    """Invoice response model."""
    id: str
    invoice_number: str
    po_id: str
    amount_cents: int
    amount_dollars: float
    currency: str
    status: str
    issued_at: Optional[datetime]
    due_at: Optional[datetime]
    artifact_uri: Optional[str]
    entity: Optional[str]
    customer_id: Optional[str]
    customer_name: str
    created_at: datetime
    updated_at: datetime
    metadata: dict


class PaymentCreate(BaseModel):
    """Payment creation model."""
    payment_reference: str
    amount: float
    currency: str = "USD"
    paid_at: Optional[datetime] = None
    method: str
    artifact_uri: str
    actor: Optional[str] = None
    reason: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class PaymentResponse(BaseModel):
    """Payment response model."""
    id: str
    invoice_id: str
    payment_reference: str
    amount_cents: int
    amount_dollars: float
    currency: str
    paid_at: datetime
    method: str
    artifact_uri: str
    created_at: datetime
    metadata: dict


def _record_audit_log(
    db: Session,
    *,
    entity: Optional[str],
    actor: str,
    action: str,
    po_id: Optional[str] = None,
    invoice_id: Optional[str] = None,
    payment_id: Optional[str] = None,
    from_state: Optional[str] = None,
    to_state: Optional[str] = None,
    reason: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> None:
    audit_entry = AuditLog(
        id=str(uuid.uuid4()),
        entity=entity,
        actor=actor,
        action=action,
        po_id=po_id,
        invoice_id=invoice_id,
        payment_id=payment_id,
        from_state=from_state,
        to_state=to_state,
        reason=reason,
        record_metadata=metadata or {},
        created_at=datetime.utcnow(),
    )
    db.add(audit_entry)


# Endpoints
@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"status": "ok", "service": "BranchOS Revenue API"}


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/version")
def version():
    """Version information endpoint."""
    return {
        "name": APP_NAME,
        "version": resolve_version(),
    }


@app.post("/ingest/manual", response_model=RevenueEventResponse)
def ingest_manual_transaction(
    transaction: ManualTransaction,
    db: Session = Depends(get_db)
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
        event_metadata={"description": transaction.description} if transaction.description else {},
        created_at=datetime.utcnow(),
        processed_at=datetime.utcnow()
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
    db: Session = Depends(get_db)
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
                detail=f"Amount column '{amount_column}' not found in CSV"
            )

        # Process each row
        created_count = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                # Extract amount (handle both float and string formats)
                amount_str = str(row[amount_column]).replace("$", "").replace(",", "").strip()
                amount = float(amount_str)
                amount_cents = int(amount * 100)

                # Extract other fields if columns are specified
                currency = row[currency_column] if currency_column and currency_column in df.columns else "USD"
                email = row[email_column] if email_column and email_column in df.columns else None
                entity = row[entity_column] if entity_column and entity_column in df.columns else None
                description = row[description_column] if description_column and description_column in df.columns else None

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
                    event_metadata={"description": description, "csv_row": idx + 1} if description else {"csv_row": idx + 1},
                    created_at=datetime.utcnow(),
                    processed_at=datetime.utcnow()
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
            "errors": errors if errors else None
        }

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty") from None
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}") from e
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
        func.count(RevenueEvent.id).label("count")
    ).first()

    total_cents = result.total_cents if result.total_cents else 0
    count = result.count if result.count else 0

    return RevenueSummary(
        total_cents=total_cents,
        total_dollars=total_cents / 100.0,
        count=count
    )


@app.get("/revenue/events", response_model=List[RevenueEventResponse])
def get_revenue_events(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get recent revenue transactions.

    Parameters:
    - limit: Maximum number of events to return (default: 50)
    - offset: Number of events to skip for pagination (default: 0)
    """
    events = db.query(RevenueEvent).order_by(
        RevenueEvent.created_at.desc()
    ).limit(limit).offset(offset).all()

    return [RevenueEventResponse.from_orm(event) for event in events]


@app.post("/po", response_model=PurchaseOrderResponse)
def create_purchase_order(
    payload: PurchaseOrderCreate,
    db: Session = Depends(get_db),
):
    """Create a purchase order."""
    normalized_status = payload.status.lower().strip()
    if normalized_status not in {"draft", "issued"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="PO status must be 'draft' or 'issued' on creation.",
        )

    amount_cents = int(payload.amount * 100)
    actor = payload.actor or "system"
    issued_at = payload.issued_at or (datetime.utcnow() if normalized_status == "issued" else None)
    now = datetime.utcnow()

    purchase_order = PurchaseOrder(
        id=str(uuid.uuid4()),
        po_number=payload.po_number,
        customer_name=payload.customer_name,
        customer_id=payload.customer_id,
        amount_cents=amount_cents,
        currency=payload.currency,
        status=normalized_status,
        entity=payload.entity,
        issued_at=issued_at,
        created_at=now,
        updated_at=now,
        record_metadata=payload.metadata,
    )
    db.add(purchase_order)
    _record_audit_log(
        db,
        entity=payload.entity,
        actor=actor,
        action="po_created",
        po_id=purchase_order.id,
        from_state=None,
        to_state=normalized_status,
        reason=payload.reason,
        metadata={"po_number": payload.po_number},
    )
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Purchase order violates uniqueness constraints.",
        ) from exc
    db.refresh(purchase_order)

    return PurchaseOrderResponse(
        id=purchase_order.id,
        po_number=purchase_order.po_number,
        customer_name=purchase_order.customer_name,
        customer_id=purchase_order.customer_id,
        amount_cents=purchase_order.amount_cents,
        amount_dollars=purchase_order.amount_cents / 100.0,
        currency=purchase_order.currency,
        status=purchase_order.status,
        entity=purchase_order.entity,
        issued_at=purchase_order.issued_at,
        created_at=purchase_order.created_at,
        updated_at=purchase_order.updated_at,
        metadata=purchase_order.record_metadata or {},
    )


@app.post("/po/{po_id}/invoice", response_model=InvoiceResponse)
def create_invoice(
    po_id: str,
    payload: InvoiceCreate,
    db: Session = Depends(get_db),
):
    """Create an invoice linked to a purchase order."""
    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not purchase_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PO not found.")

    if purchase_order.status not in {"issued", "invoiced"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="PO must be in 'issued' or 'invoiced' status to create an invoice.",
        )

    normalized_status = payload.status.lower().strip()
    if normalized_status not in {"draft", "sent", "void"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invoice status must be 'draft', 'sent', or 'void' on creation.",
        )

    amount_cents = int(payload.amount * 100)
    actor = payload.actor or "system"
    now = datetime.utcnow()
    invoice = Invoice(
        id=str(uuid.uuid4()),
        invoice_number=payload.invoice_number,
        po_id=purchase_order.id,
        amount_cents=amount_cents,
        currency=payload.currency,
        status=normalized_status,
        issued_at=payload.issued_at,
        due_at=payload.due_at,
        artifact_uri=payload.artifact_uri,
        entity=purchase_order.entity,
        customer_id=purchase_order.customer_id,
        customer_name=purchase_order.customer_name,
        created_at=now,
        updated_at=now,
        record_metadata=payload.metadata,
    )
    db.add(invoice)

    previous_status = purchase_order.status
    if purchase_order.status == "issued":
        purchase_order.status = "invoiced"
        purchase_order.updated_at = now

    _record_audit_log(
        db,
        entity=purchase_order.entity,
        actor=actor,
        action="invoice_created",
        po_id=purchase_order.id,
        invoice_id=invoice.id,
        from_state=previous_status,
        to_state=purchase_order.status,
        reason=payload.reason,
        metadata={"invoice_number": payload.invoice_number},
    )
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invoice violates uniqueness constraints.",
        ) from exc

    db.refresh(invoice)

    return InvoiceResponse(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        po_id=invoice.po_id,
        amount_cents=invoice.amount_cents,
        amount_dollars=invoice.amount_cents / 100.0,
        currency=invoice.currency,
        status=invoice.status,
        issued_at=invoice.issued_at,
        due_at=invoice.due_at,
        artifact_uri=invoice.artifact_uri,
        entity=invoice.entity,
        customer_id=invoice.customer_id,
        customer_name=invoice.customer_name,
        created_at=invoice.created_at,
        updated_at=invoice.updated_at,
        metadata=invoice.record_metadata or {},
    )


@app.post("/invoice/{invoice_id}/payment", response_model=PaymentResponse)
def record_payment(
    invoice_id: str,
    payload: PaymentCreate,
    db: Session = Depends(get_db),
):
    """Record a payment tied to an invoice and mark PO paid."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found.")

    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == invoice.po_id).first()
    if not purchase_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PO not found for invoice.")

    if invoice.status == "void":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot record payment against a void invoice.",
        )

    if invoice.status == "paid":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invoice is already marked as paid.",
        )

    if not payload.artifact_uri:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Payment artifact is required to mark invoice/PO as paid.",
        )

    amount_cents = int(payload.amount * 100)
    if amount_cents < invoice.amount_cents:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Payment amount must cover the invoice total.",
        )

    actor = payload.actor or "system"
    paid_at = payload.paid_at or datetime.utcnow()
    now = datetime.utcnow()
    payment = Payment(
        id=str(uuid.uuid4()),
        invoice_id=invoice.id,
        payment_reference=payload.payment_reference,
        amount_cents=amount_cents,
        currency=payload.currency,
        paid_at=paid_at,
        method=payload.method,
        artifact_uri=payload.artifact_uri,
        entity=purchase_order.entity,
        created_at=now,
        record_metadata=payload.metadata,
    )
    db.add(payment)

    previous_invoice_status = invoice.status
    invoice.status = "paid"
    invoice.updated_at = now

    previous_po_status = purchase_order.status
    purchase_order.status = "paid"
    purchase_order.updated_at = now

    revenue_event = RevenueEvent(
        id=str(uuid.uuid4()),
        event_id=f"payment_{uuid.uuid4().hex[:16]}",
        provider="manual",
        event_type="po_payment",
        amount_cents=amount_cents,
        currency=payload.currency,
        customer_email=None,
        customer_id=purchase_order.customer_id,
        entity=purchase_order.entity,
        event_metadata={
            "po_id": purchase_order.id,
            "invoice_id": invoice.id,
            "payment_id": payment.id,
            "payment_reference": payload.payment_reference,
        },
        created_at=now,
        processed_at=now,
    )
    db.add(revenue_event)

    _record_audit_log(
        db,
        entity=purchase_order.entity,
        actor=actor,
        action="payment_recorded",
        po_id=purchase_order.id,
        invoice_id=invoice.id,
        payment_id=payment.id,
        from_state=previous_po_status,
        to_state=purchase_order.status,
        reason=payload.reason,
        metadata={"payment_reference": payload.payment_reference},
    )

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment violates uniqueness constraints.",
        ) from exc

    db.refresh(payment)

    return PaymentResponse(
        id=payment.id,
        invoice_id=payment.invoice_id,
        payment_reference=payment.payment_reference,
        amount_cents=payment.amount_cents,
        amount_dollars=payment.amount_cents / 100.0,
        currency=payment.currency,
        paid_at=payment.paid_at,
        method=payment.method,
        artifact_uri=payment.artifact_uri,
        created_at=payment.created_at,
        metadata=payment.record_metadata or {},
    )


# Webhook endpoints (placeholders for future Stripe/Gumroad integration)
@app.post("/webhooks/stripe")
def stripe_webhook():
    """Stripe webhook endpoint (to be implemented)."""
    return {"status": "not_implemented", "message": "Stripe webhook coming soon"}


@app.post("/webhooks/gumroad")
def gumroad_webhook():
    """Gumroad webhook endpoint (to be implemented)."""
    return {"status": "not_implemented", "message": "Gumroad webhook coming soon"}
