"""Revenue ingest and read routes."""
import uuid
from datetime import datetime
from io import StringIO
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from branchberg.app.database import RevenueEvent, get_db
from branchberg.app.schemas.revenue import ManualTransaction, RevenueEventResponse, RevenueSummary

router = APIRouter(tags=["revenue"])


@router.post("/ingest/manual", response_model=RevenueEventResponse)
def ingest_manual_transaction(transaction: ManualTransaction, db: Session = Depends(get_db)):
    revenue_event = RevenueEvent(
        id=str(uuid.uuid4()),
        event_id=f"manual_{uuid.uuid4().hex[:16]}",
        provider="manual",
        event_type="manual_entry",
        amount_cents=int(transaction.amount * 100),
        currency=transaction.currency,
        customer_email=transaction.customer_email,
        customer_id=transaction.customer_id,
        entity=transaction.entity,
        event_metadata={"description": transaction.description} if transaction.description else {},
        created_at=datetime.utcnow(),
        processed_at=datetime.utcnow(),
    )
    db.add(revenue_event)
    db.commit()
    db.refresh(revenue_event)
    return RevenueEventResponse.from_record(revenue_event)


@router.post("/ingest/csv")
def ingest_csv_transactions(
    file: UploadFile = File(...),
    amount_column: str = Form(...),
    currency_column: Optional[str] = Form(None),
    email_column: Optional[str] = Form(None),
    entity_column: Optional[str] = Form(None),
    description_column: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    try:
        contents = file.file.read().decode("utf-8")
        df = pd.read_csv(StringIO(contents))
        if amount_column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Amount column '{amount_column}' not found in CSV")

        created_count = 0
        errors = []
        for idx, row in df.iterrows():
            try:
                amount = float(str(row[amount_column]).replace("$", "").replace(",", "").strip())
                revenue_event = RevenueEvent(
                    id=str(uuid.uuid4()),
                    event_id=f"csv_{uuid.uuid4().hex[:16]}",
                    provider="manual",
                    event_type="csv_import",
                    amount_cents=int(amount * 100),
                    currency=row[currency_column] if currency_column and currency_column in df.columns else "USD",
                    customer_email=None if email_column is None or email_column not in df.columns or pd.isna(row[email_column]) else row[email_column],
                    entity=None if entity_column is None or entity_column not in df.columns or pd.isna(row[entity_column]) else row[entity_column],
                    event_metadata={"description": None if description_column is None or description_column not in df.columns or pd.isna(row[description_column]) else row[description_column], "csv_row": idx + 1},
                    created_at=datetime.utcnow(),
                    processed_at=datetime.utcnow(),
                )
                db.add(revenue_event)
                created_count += 1
            except Exception as exc:  # pylint: disable=broad-except
                errors.append(f"Row {idx + 1}: {exc}")

        db.commit()
        return {"success": True, "created_count": created_count, "total_rows": len(df), "errors": errors or None}
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty") from None
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {exc}") from exc
    finally:
        file.file.close()


@router.get("/revenue/summary", response_model=RevenueSummary)
def get_revenue_summary(db: Session = Depends(get_db)):
    result = db.query(func.sum(RevenueEvent.amount_cents).label("total_cents"), func.count(RevenueEvent.id).label("count")).first()
    total_cents = result.total_cents if result.total_cents else 0
    count = result.count if result.count else 0
    return RevenueSummary(total_cents=total_cents, total_dollars=total_cents / 100.0, count=count)


@router.get("/revenue/events", response_model=List[RevenueEventResponse])
def get_revenue_events(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    events = db.query(RevenueEvent).order_by(RevenueEvent.created_at.desc()).limit(limit).offset(offset).all()
    return [RevenueEventResponse.from_record(event) for event in events]
