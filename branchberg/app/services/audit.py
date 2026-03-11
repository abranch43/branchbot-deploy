"""Audit logging helpers."""
import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from branchberg.app.database import AuditLog


def record_audit_log(
    db: Session,
    *,
    entity: str,
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
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Audit log entries require an entity.",
        )

    db.add(
        AuditLog(
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
    )
