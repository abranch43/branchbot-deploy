"""Gumroad webhook handler skeleton.

NOTE: Gumroad webhook signature schemes vary depending on integration.
This file provides a placeholder verifier and clear TODOs.
"""

from __future__ import annotations

import hmac
import hashlib
from typing import Any, Optional

from fastapi import Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from branchberg.app.revenue_agent.config import AgentSettings
from branchberg.app.revenue_agent.repository import RevenueEventIngest, insert_revenue_event_idempotent


class GumroadWebhookResponse(BaseModel):
    status: str
    provider: str = "gumroad"
    processed: bool
    reason: Optional[str] = None
    created: Optional[bool] = None
    event_id: Optional[str] = None


def _verify_gumroad_signature(*, secret: str, order_number: str, signature: str) -> bool:
    """Verify Gumroad webhook signature.

    TODO: confirm the exact signature scheme used in your Gumroad webhook settings.
    The demo in README uses HMAC(secret, order_number).
    """

    if not secret or not order_number or not signature:
        return False

    expected = hmac.new(secret.encode("utf-8"), order_number.encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def _to_int_cents(price: Any) -> int:
    """Best-effort conversion from Gumroad price fields.

    Gumroad often provides cents as integer-like strings.
    """

    if price is None:
        return 0
    try:
        return int(str(price).strip())
    except Exception:
        return 0


async def handle_gumroad_webhook(
    request: Request, db: Session, settings: AgentSettings
) -> tuple[GumroadWebhookResponse, int]:
    """Verify + ingest a Gumroad webhook.

    For now this returns 200-style JSON on errors (no exceptions), mirroring the
    early-stage behavior of this repo.

    TODO: enforce strict HTTP status codes after rollout.
    """

    if settings.safe_mode:
        return (
            GumroadWebhookResponse(status="safe_mode", processed=False, reason="SAFE_MODE=true"),
            200,
        )

    if not settings.gumroad_webhook_secret:
        return (
            GumroadWebhookResponse(
                status="not_configured",
                processed=False,
                reason="missing GUMROAD_WEBHOOK_SECRET",
            ),
            500,
        )

    form = await request.form()

    order_number = str(form.get("order_number") or "").strip()
    signature = str(form.get("signature") or "").strip()

    if not _verify_gumroad_signature(
        secret=settings.gumroad_webhook_secret,
        order_number=order_number,
        signature=signature,
    ):
        return (
            GumroadWebhookResponse(
                status="invalid",
                processed=False,
                reason="signature_failed",
            ),
            401,
        )

    email = str(form.get("email") or "").strip() or None
    currency = str(form.get("currency") or "USD").strip().upper() or "USD"

    # Gumroad often posts `price` as cents.
    amount_cents = _to_int_cents(form.get("price"))

    # TODO: decide on canonical event_id. Options:
    # - `sale_id` if present
    # - `order_number` plus a suffix for refunds
    event_id = order_number or None
    if not event_id:
        return (
            GumroadWebhookResponse(
                status="invalid",
                processed=False,
                reason="missing_order_number",
            ),
            401,
        )

    event_type = "sale"  # TODO: detect refunds/chargebacks if Gumroad includes such signals.

    ingest = RevenueEventIngest(
        event_id=f"gumroad_{event_id}",
        provider="gumroad",
        event_type=event_type,
        amount_cents=amount_cents,
        currency=currency,
        customer_email=email,
        # TODO: map entity based on product_id, metadata, or webhook configuration.
        metadata={
            "gumroad": {
                "order_number": order_number,
                "product_id": form.get("product_id"),
                "seller_id": form.get("seller_id"),
            }
        },
    )

    record, created = insert_revenue_event_idempotent(db, ingest)

    return (
        GumroadWebhookResponse(
            status="ok",
            processed=True,
            created=created,
            event_id=record.event_id,
        ),
        200,
    )
