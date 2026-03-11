"""Routes for purchase order lifecycle."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from branchberg.app.database import get_db
from branchberg.app.schemas.po_flow import (
    InvoiceCreate,
    InvoiceResponse,
    PaymentCreate,
    PaymentResponse,
    PurchaseOrderCreate,
    PurchaseOrderResponse,
)
from branchberg.app.services import po_flow as po_flow_service

router = APIRouter(tags=["po-flow"])


@router.post("/po", response_model=PurchaseOrderResponse)
def create_purchase_order(payload: PurchaseOrderCreate, db: Session = Depends(get_db)):
    return po_flow_service.create_purchase_order(db, payload)


@router.post("/po/{po_id}/invoice", response_model=InvoiceResponse)
def create_invoice(po_id: str, payload: InvoiceCreate, db: Session = Depends(get_db)):
    return po_flow_service.create_invoice(db, po_id, payload)


@router.post("/invoice/{invoice_id}/payment", response_model=PaymentResponse)
def record_payment(invoice_id: str, payload: PaymentCreate, db: Session = Depends(get_db)):
    return po_flow_service.record_payment(db, invoice_id, payload)
