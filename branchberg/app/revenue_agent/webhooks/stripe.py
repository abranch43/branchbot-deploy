"""Stripe webhook handler skeleton.

TODO: expand supported Stripe event types and extract customer/entity fields.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import Request
from sqlalchemy.orm import Session

from branchberg.app.revenue_agent.config import AgentSettings
from branchberg.app.revenue_agent.repository import RevenueEventIngest, insert_revenue_event_idempotent


def _extract_amount_cents(event: dict[str, Any]) -> int:
    obj = (event.get("data") or {}).get("object") or {}

    # Common Stripe fields depending on event type.
    for key in ("amount_total", "amount", "amount_received"):
        value = obj.get(key)
        if isinstance(value, int):
            return value

    # TODO: handle nested line items / payment_intent lookup when needed.
    return 0


def _extract_currency(event: dict[str, Any]) -> str:
    obj = (event.get("data") or {}).get("object") or {}
    currency = obj.get("currency")
    if isinstance(currency, str) and currency.strip():
        return currency.upper()
    return "USD"


async def handle_stripe_webhook(request: Request, db: Session, settings: AgentSettings) -> dict[str, Any]:
    """Verify + ingest a Stripe webhook.

    Returns a JSON payload. For now, this handler intentionally does not raise
    HTTP errors to keep existing tests and simple deployments stable.

    TODO: switch to strict HTTP status codes (400/401) once webhook verification
    is fully deployed.
    """

    raw = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if settings.safe_mode:
        return {
            "status": "safe_mode",
            "provider": "stripe",
            "processed": False,
            "reason": "SAFE_MODE=true",
        }

    if not settings.stripe_webhook_secret:
        return {
            "status": "not_configured",
            "provider": "stripe",
            "processed": False,
            "reason": "missing STRIPE_WEBHOOK_SECRET",
        }

    try:
        import stripe

        event = stripe.Webhook.construct_event(
            payload=raw,
            sig_header=sig_header,
            secret=settings.stripe_webhook_secret,
        )
        # stripe returns StripeObject; cast to dict-like.
        event_dict = dict(event)
    except Exception as exc:
        return {
            "status": "invalid",
            "provider": "stripe",
            "processed": False,
            "reason": "signature_or_parse_failed",
            "error": str(exc),
        }

    event_id = str(event_dict.get("id") or "").strip() or None
    event_type = str(event_dict.get("type") or "").strip() or "unknown"

    if not event_id:
        return {
            "status": "invalid",
            "provider": "stripe",
            "processed": False,
            "reason": "missing_event_id",
        }

    ingest = RevenueEventIngest(
        event_id=event_id,
        provider="stripe",
        event_type=event_type,
        amount_cents=_extract_amount_cents(event_dict),
        currency=_extract_currency(event_dict),
        # TODO: populate customer_email/customer_id/entity based on your Stripe setup.
        metadata={
            # Keep metadata compact; avoid storing full PII-heavy payloads.
            "stripe_event": {
                "id": event_id,
                "type": event_type,
            }
        },
    )

    record, created = insert_revenue_event_idempotent(db, ingest)

    return {
        "status": "ok",
        "provider": "stripe",
        "processed": True,
        "created": created,
        "event_id": record.event_id,
    }
