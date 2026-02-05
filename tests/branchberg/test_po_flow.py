"""Tests for PO-to-paid flow invariants."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from branchberg.app.main import app
from branchberg.app.database import Base, get_db, PurchaseOrder

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_branchbot_po.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_db():
    """Create test database for each test."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_cannot_pay_po_without_payment_artifact(client, test_db):
    """Ensure payment artifact is required before PO can be marked as paid."""
    po_payload = {
        "po_number": "PO-123",
        "customer_name": "Acme Corp",
        "customer_id": "ACME-1",
        "amount": 1000.00,
        "currency": "USD",
        "entity": "A+ Enterprise LLC",
    }
    po_response = client.post("/po", json=po_payload)
    assert po_response.status_code == 200
    po_id = po_response.json()["id"]

    invoice_payload = {
        "invoice_number": "INV-123",
        "amount": 1000.00,
        "currency": "USD",
        "status": "sent",
    }
    invoice_response = client.post(f"/po/{po_id}/invoice", json=invoice_payload)
    assert invoice_response.status_code == 200
    invoice_id = invoice_response.json()["id"]

    payment_payload = {
        "payment_reference": "PAY-123",
        "amount": 1000.00,
        "currency": "USD",
        "method": "ach",
    }
    payment_response = client.post(f"/invoice/{invoice_id}/payment", json=payment_payload)
    assert payment_response.status_code == 422
    assert "detail" in payment_response.json()

    db = TestingSessionLocal()
    try:
        po_record = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        assert po_record is not None
        assert po_record.status == "invoiced"
    finally:
        db.close()


def teardown_module(module):
    """Clean up test database file."""
    import os

    try:
        os.remove("test_branchbot_po.db")
    except FileNotFoundError:
        pass
