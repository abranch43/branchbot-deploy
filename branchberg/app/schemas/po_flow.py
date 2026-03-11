"""Pydantic schemas for PO -> invoice -> payment flow."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .common import normalize_currency, non_empty_trimmed


class PurchaseOrderCreate(BaseModel):
    po_number: str = Field(..., min_length=1)
    customer_name: str
    customer_id: Optional[str] = None
    amount: float = Field(..., gt=0)
    currency: str = "USD"
    entity: str = Field(..., description="Business entity")
    status: str = "issued"
    issued_at: Optional[datetime] = None
    actor: Optional[str] = None
    reason: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

    @field_validator("currency")
    @classmethod
    def _currency_upper(cls, value: str) -> str:
        return normalize_currency(value)

    @field_validator("po_number")
    @classmethod
    def _po_number_non_empty(cls, value: str) -> str:
        return non_empty_trimmed(value)


class PurchaseOrderResponse(BaseModel):
    id: str
    po_number: str
    customer_name: str
    customer_id: Optional[str]
    amount_cents: int
    amount_dollars: float
    currency: str
    status: str
    entity: str
    issued_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    metadata: dict


class InvoiceCreate(BaseModel):
    invoice_number: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    currency: str = "USD"
    entity: Optional[str] = None
    status: str = "sent"
    issued_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    artifact_uri: Optional[str] = None
    actor: Optional[str] = None
    reason: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

    @field_validator("currency")
    @classmethod
    def _currency_upper(cls, value: str) -> str:
        return normalize_currency(value)

    @field_validator("invoice_number")
    @classmethod
    def _invoice_number_non_empty(cls, value: str) -> str:
        return non_empty_trimmed(value)


class InvoiceResponse(BaseModel):
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
    entity: str
    customer_id: Optional[str]
    customer_name: str
    created_at: datetime
    updated_at: datetime
    metadata: dict


class PaymentCreate(BaseModel):
    payment_reference: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    currency: str = "USD"
    paid_at: Optional[datetime] = None
    method: str
    artifact_uri: str
    actor: Optional[str] = None
    reason: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

    @field_validator("currency")
    @classmethod
    def _currency_upper(cls, value: str) -> str:
        return normalize_currency(value)

    @field_validator("payment_reference")
    @classmethod
    def _payment_reference_non_empty(cls, value: str) -> str:
        return non_empty_trimmed(value)


class PaymentResponse(BaseModel):
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
