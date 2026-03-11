"""Service layer for PO -> invoice -> payment lifecycle."""
import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from branchberg.app.database import Invoice, Payment, PurchaseOrder, RevenueEvent
from branchberg.app.schemas.po_flow import (
    InvoiceCreate,
    InvoiceResponse,
    PaymentCreate,
    PaymentResponse,
    PurchaseOrderCreate,
    PurchaseOrderResponse,
)
from branchberg.app.services.audit import record_audit_log


def create_purchase_order(db: Session, payload: PurchaseOrderCreate) -> PurchaseOrderResponse:
    if not payload.entity or not payload.entity.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Entity is required to create a purchase order.",
        )

    normalized_status = payload.status.lower().strip()
    if normalized_status not in {"draft", "issued"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="PO status must be 'draft' or 'issued' on creation.",
        )

    now = datetime.utcnow()
    purchase_order = PurchaseOrder(
        id=str(uuid.uuid4()),
        po_number=payload.po_number,
        customer_name=payload.customer_name,
        customer_id=payload.customer_id,
        amount_cents=int(payload.amount * 100),
        currency=payload.currency.strip().upper(),
        status=normalized_status,
        entity=payload.entity.strip(),
        issued_at=payload.issued_at or (now if normalized_status == "issued" else None),
        created_at=now,
        updated_at=now,
        record_metadata=payload.metadata,
    )
    db.add(purchase_order)
    record_audit_log(
        db,
        entity=purchase_order.entity,
        actor=payload.actor or "system",
        action="po_created",
        po_id=purchase_order.id,
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


def create_invoice(db: Session, po_id: str, payload: InvoiceCreate) -> InvoiceResponse:
    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not purchase_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PO not found.")

    if purchase_order.status not in {"issued", "invoiced"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="PO must be in 'issued' or 'invoiced' status to create an invoice.",
        )

    status_value = payload.status.lower().strip()
    if status_value not in {"draft", "sent", "void"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invoice status must be 'draft', 'sent', or 'void' on creation.",
        )

    invoice_currency = payload.currency.strip().upper()
    if invoice_currency != purchase_order.currency:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invoice currency must match purchase order currency.",
        )

    if payload.entity is not None and purchase_order.entity != payload.entity:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invoice entity must match purchase order entity.",
        )

    amount_cents = int(payload.amount * 100)
    existing_non_void_total = (
        db.query(func.coalesce(func.sum(Invoice.amount_cents), 0))
        .filter(Invoice.po_id == purchase_order.id, Invoice.status != "void")
        .scalar()
    )
    projected_total = existing_non_void_total + (0 if status_value == "void" else amount_cents)
    if projected_total > purchase_order.amount_cents:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Total non-void invoices cannot exceed the purchase order amount.",
        )

    now = datetime.utcnow()
    invoice = Invoice(
        id=str(uuid.uuid4()),
        invoice_number=payload.invoice_number,
        po_id=purchase_order.id,
        amount_cents=amount_cents,
        currency=invoice_currency,
        status=status_value,
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

    record_audit_log(
        db,
        entity=purchase_order.entity,
        actor=payload.actor or "system",
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


def record_payment(db: Session, invoice_id: str, payload: PaymentCreate) -> PaymentResponse:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found.")

    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == invoice.po_id).first()
    if not purchase_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PO not found for invoice.")

    if not invoice.entity or not purchase_order.entity or invoice.entity != purchase_order.entity:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invoice and purchase order must include a matching entity before recording payment.",
        )

    if invoice.status in {"void", "paid"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot record payment for invoice in current state.",
        )

    if db.query(Payment).filter(Payment.invoice_id == invoice.id).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A payment has already been recorded for this invoice.",
        )

    if not payload.artifact_uri:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Payment artifact is required to mark invoice/PO as paid.",
        )

    amount_cents = int(payload.amount * 100)
    if amount_cents != invoice.amount_cents:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Payment amount must equal the invoice total.",
        )

    payment_currency = payload.currency.strip().upper()
    invoice_currency = (invoice.currency or "").strip().upper()
    if payment_currency != invoice_currency:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Payment currency must match invoice currency.",
        )

    now = datetime.utcnow()
    payment = Payment(
        id=str(uuid.uuid4()),
        invoice_id=invoice.id,
        payment_reference=payload.payment_reference,
        amount_cents=amount_cents,
        currency=invoice_currency,
        paid_at=payload.paid_at or now,
        method=payload.method,
        artifact_uri=payload.artifact_uri,
        entity=invoice.entity,
        created_at=now,
        record_metadata=payload.metadata,
    )
    db.add(payment)

    invoice.status = "paid"
    invoice.updated_at = now
    previous_po_status = purchase_order.status
    purchase_order.status = "paid"
    purchase_order.updated_at = now

    db.add(
        RevenueEvent(
            id=str(uuid.uuid4()),
            event_id=f"payment_{uuid.uuid4().hex[:16]}",
            provider="manual",
            event_type="po_payment",
            amount_cents=amount_cents,
            currency=invoice_currency,
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
    )

    record_audit_log(
        db,
        entity=purchase_order.entity,
        actor=payload.actor or "system",
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
