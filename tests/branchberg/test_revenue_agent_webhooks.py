"""Tests for Revenue Tracking Agent webhook handlers.

These tests:
- mock Stripe/Gumroad webhook verification
- cover failure scenarios (SAFE_MODE, missing secrets, invalid signatures)
- cover retry/idempotency scenarios (same event delivered multiple times)

Note: current implementation returns HTTP 200 with a status payload even on
invalid signatures; tests assert the returned JSON contract.
"""

from __future__ import annotations

import hmac
import hashlib
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from branchberg.app.database import Base, RevenueEvent, get_db
from branchberg.app.main import app
from branchberg.app.revenue_agent.config import AgentSettings


@pytest.fixture()
def db_engine(tmp_path):
    """Create a per-test SQLite database file to avoid global locking issues."""
    db_path = tmp_path / "test_revenue_agent.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    try:
        yield engine
    finally:
        try:
            engine.dispose()
        except Exception:
            pass


@pytest.fixture()
def db_session_factory(db_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


@pytest.fixture()
def client(db_engine, db_session_factory, monkeypatch):
    """Test client with overridden DB dependency."""

    def override_get_db():
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    Base.metadata.create_all(bind=db_engine)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=db_engine)


def _count_events(db_session_factory) -> int:
    db = db_session_factory()
    try:
        return db.query(RevenueEvent).count()
    finally:
        db.close()


def _set_agent_settings(monkeypatch, *, safe_mode: bool, stripe_secret: str | None, gumroad_secret: str | None):
    settings = AgentSettings(
        safe_mode=safe_mode,
        stripe_webhook_secret=stripe_secret,
        gumroad_webhook_secret=gumroad_secret,
        slack_webhook_url=None,
    )
    # main.py holds AGENT_SETTINGS as a module global.
    import branchberg.app.main as main_module

    monkeypatch.setattr(main_module, "AGENT_SETTINGS", settings, raising=True)


def test_stripe_webhook_safe_mode(client, db_session_factory, monkeypatch):
    _set_agent_settings(monkeypatch, safe_mode=True, stripe_secret="whsec_test", gumroad_secret="gsec")

    res = client.post("/webhooks/stripe", content=b"{}", headers={"Stripe-Signature": "t=1,v1=abc"})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "safe_mode"
    assert body["provider"] == "stripe"
    assert _count_events(db_session_factory) == 0


def test_stripe_webhook_missing_secret(client, db_session_factory, monkeypatch):
    _set_agent_settings(monkeypatch, safe_mode=False, stripe_secret=None, gumroad_secret="gsec")

    res = client.post("/webhooks/stripe", content=b"{}", headers={"Stripe-Signature": "t=1,v1=abc"})
    assert res.status_code == 500
    body = res.json()
    assert body["status"] == "not_configured"
    assert body["provider"] == "stripe"
    assert _count_events(db_session_factory) == 0


def test_stripe_webhook_invalid_signature_or_parse(client, db_session_factory, monkeypatch):
    _set_agent_settings(monkeypatch, safe_mode=False, stripe_secret="whsec_test", gumroad_secret="gsec")

    import stripe

    def boom(*args, **kwargs):
        raise ValueError("bad signature")

    monkeypatch.setattr(stripe.Webhook, "construct_event", boom, raising=True)

    res = client.post("/webhooks/stripe", content=b"{}", headers={"Stripe-Signature": "bad"})
    assert res.status_code == 401
    body = res.json()
    assert body["status"] == "invalid"
    assert body["provider"] == "stripe"
    assert body["processed"] is False
    assert _count_events(db_session_factory) == 0


def test_stripe_webhook_success_and_retry_idempotent(client, db_session_factory, monkeypatch):
    _set_agent_settings(monkeypatch, safe_mode=False, stripe_secret="whsec_test", gumroad_secret="gsec")

    import stripe

    event_id = "evt_123"

    def ok_construct_event(payload, sig_header, secret):
        assert secret == "whsec_test"
        # Minimal Stripe-like event.
        return {
            "id": event_id,
            "type": "checkout.session.completed",
            "data": {"object": {"amount_total": 4999, "currency": "usd"}},
        }

    monkeypatch.setattr(stripe.Webhook, "construct_event", ok_construct_event, raising=True)

    res1 = client.post("/webhooks/stripe", content=b"{}", headers={"Stripe-Signature": "t=1,v1=abc"})
    assert res1.status_code == 200
    body1 = res1.json()
    assert body1["status"] == "ok"
    assert body1["created"] is True
    assert body1["event_id"] == event_id
    assert _count_events(db_session_factory) == 1

    # Retry of the same event should not create a second row.
    res2 = client.post("/webhooks/stripe", content=b"{}", headers={"Stripe-Signature": "t=1,v1=abc"})
    assert res2.status_code == 200
    body2 = res2.json()
    assert body2["status"] == "ok"
    assert body2["created"] is False
    assert _count_events(db_session_factory) == 1


def test_gumroad_webhook_safe_mode(client, db_session_factory, monkeypatch):
    _set_agent_settings(monkeypatch, safe_mode=True, stripe_secret="whsec", gumroad_secret="gsec")

    res = client.post("/webhooks/gumroad", data={"order_number": "ORD1", "signature": "abc"})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "safe_mode"
    assert body["provider"] == "gumroad"
    assert _count_events(db_session_factory) == 0


def test_gumroad_webhook_missing_secret(client, db_session_factory, monkeypatch):
    _set_agent_settings(monkeypatch, safe_mode=False, stripe_secret="whsec", gumroad_secret=None)

    res = client.post("/webhooks/gumroad", data={"order_number": "ORD1", "signature": "abc"})
    assert res.status_code == 500
    body = res.json()
    assert body["status"] == "not_configured"
    assert body["provider"] == "gumroad"
    assert _count_events(db_session_factory) == 0


def test_gumroad_webhook_invalid_signature(client, db_session_factory, monkeypatch):
    _set_agent_settings(monkeypatch, safe_mode=False, stripe_secret="whsec", gumroad_secret="gsec")

    res = client.post(
        "/webhooks/gumroad",
        data={
            "order_number": "ORD1",
            "signature": "wrong",
            "price": "1000",
            "currency": "USD",
        },
    )
    assert res.status_code == 401
    body = res.json()
    assert body["status"] == "invalid"
    assert body["provider"] == "gumroad"
    assert _count_events(db_session_factory) == 0


def test_gumroad_webhook_success_and_retry_idempotent(client, db_session_factory, monkeypatch):
    secret = "gsec"
    _set_agent_settings(monkeypatch, safe_mode=False, stripe_secret="whsec", gumroad_secret=secret)

    order_number = "ORD123"
    signature = hmac.new(secret.encode("utf-8"), order_number.encode("utf-8"), hashlib.sha256).hexdigest()

    payload = {
        "seller_id": "seller_1",
        "product_id": "prod_1",
        "email": "buyer@example.com",
        "price": "89700",
        "currency": "USD",
        "order_number": order_number,
        "signature": signature,
    }

    res1 = client.post("/webhooks/gumroad", data=payload)
    assert res1.status_code == 200
    body1 = res1.json()
    assert body1["status"] == "ok"
    assert body1["created"] is True
    assert body1["event_id"] == f"gumroad_{order_number}"
    assert _count_events(db_session_factory) == 1

    # Retry delivery.
    res2 = client.post("/webhooks/gumroad", data=payload)
    assert res2.status_code == 200
    body2 = res2.json()
    assert body2["status"] == "ok"
    assert body2["created"] is False
    assert _count_events(db_session_factory) == 1
