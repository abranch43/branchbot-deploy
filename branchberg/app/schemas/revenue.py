"""Pydantic schemas for revenue endpoints."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .common import normalize_currency


class ManualTransaction(BaseModel):
    amount: float = Field(..., gt=0, description="Transaction amount in dollars")
    currency: str = Field(default="USD", description="Currency code")
    customer_email: Optional[str] = Field(None, description="Customer email")
    customer_id: Optional[str] = Field(None, description="Customer ID")
    entity: Optional[str] = Field(None, description="Business entity")
    description: Optional[str] = Field(None, description="Transaction description")

    @field_validator("currency")
    @classmethod
    def _currency_upper(cls, value: str) -> str:
        return normalize_currency(value)


class RevenueEventResponse(BaseModel):
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

    @classmethod
    def from_record(cls, record):
        return cls(
            id=record.id,
            event_id=record.event_id,
            provider=record.provider,
            event_type=record.event_type,
            amount_cents=record.amount_cents,
            amount_dollars=record.amount_cents / 100.0,
            currency=record.currency,
            customer_email=record.customer_email,
            customer_id=record.customer_id,
            entity=record.entity,
            created_at=record.created_at,
            processed_at=record.processed_at,
            metadata=record.event_metadata or {},
        )


class RevenueSummary(BaseModel):
    total_cents: int
    total_dollars: float
    count: int
    currency: str = "USD"
