"""Database interface (repository) for the Revenue Tracking Agent.

This wraps SQLAlchemy operations with:
- idempotent insert semantics (dedupe via event_id)
- a narrow interface used by webhook handlers and jobs

TODO: expand with summaries/alerts tables once models exist.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from branchberg.app.database import RevenueEvent


@dataclass(frozen=True)
class RevenueEventIngest:
    event_id: str
    provider: str  # stripe|gumroad|manual
    event_type: str
    amount_cents: int
    currency: str = "USD"
    customer_email: Optional[str] = None
    customer_id: Optional[str] = None
    entity: Optional[str] = None
    metadata: dict[str, Any] | None = None
    occurred_at: Optional[datetime] = None


def insert_revenue_event_idempotent(db: Session, payload: RevenueEventIngest) -> tuple[RevenueEvent, bool]:
    """Insert a revenue event once; return (event, created).

    Dedupe strategy: `RevenueEvent.event_id` is unique.

    TODO: also record dedupe collisions in `revenue_alerts` as `duplicate`.
    """

    now = datetime.utcnow()
    record = RevenueEvent(
        id=str(uuid.uuid4()),
        event_id=payload.event_id,
        provider=payload.provider,
        event_type=payload.event_type,
        amount_cents=int(payload.amount_cents),
        currency=(payload.currency or "USD"),
        customer_email=payload.customer_email,
        customer_id=payload.customer_id,
        entity=payload.entity,
        event_metadata=payload.metadata or {},
        created_at=payload.occurred_at or now,
        processed_at=now,
    )

    db.add(record)
    try:
        db.commit()
        db.refresh(record)
        return record, True
    except IntegrityError:
        db.rollback()
        existing = db.query(RevenueEvent).filter(RevenueEvent.event_id == payload.event_id).first()
        # Existing should be present if the unique constraint triggered.
        if existing is None:
            # Extremely rare edge case; surface as a generic error for now.
            raise
        return existing, False
