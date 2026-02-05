"""Tests for Universal Income Ingest API endpoints."""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from branchberg.app.main import app
from branchberg.app.database import Base, get_db

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_branchbot.db"
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


def test_root_endpoint(client):
    """Test root endpoint returns OK status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "BranchOS" in data["service"]


def test_manual_transaction_success(client, test_db):
    """Test manual transaction creation."""
    transaction_data = {
        "amount": 150.50,
        "currency": "USD",
        "customer_email": "test@example.com",
        "entity": "A+ Enterprise LLC",
        "description": "Test transaction"
    }
    
    response = client.post("/ingest/manual", json=transaction_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["amount_dollars"] == 150.50
    assert data["amount_cents"] == 15050
    assert data["currency"] == "USD"
    assert data["customer_email"] == "test@example.com"
    assert data["provider"] == "manual"
    assert data["event_type"] == "manual_entry"


def test_manual_transaction_minimal(client, test_db):
    """Test manual transaction with minimal data."""
    transaction_data = {
        "amount": 50.00
    }
    
    response = client.post("/ingest/manual", json=transaction_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["amount_dollars"] == 50.00
    assert data["currency"] == "USD"


def test_revenue_summary_empty(client, test_db):
    """Test revenue summary with no transactions."""
    response = client.get("/revenue/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_dollars"] == 0.0
    assert data["count"] == 0


def test_revenue_summary_with_data(client, test_db):
    """Test revenue summary with transactions."""
    # Add two transactions
    client.post("/ingest/manual", json={"amount": 100.00})
    client.post("/ingest/manual", json={"amount": 50.50})
    
    response = client.get("/revenue/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_dollars"] == 150.50
    assert data["count"] == 2


def test_revenue_events_empty(client, test_db):
    """Test revenue events with no data."""
    response = client.get("/revenue/events")
    assert response.status_code == 200
    
    data = response.json()
    assert data == []


def test_revenue_events_with_data(client, test_db):
    """Test revenue events retrieval."""
    # Add transactions
    client.post("/ingest/manual", json={"amount": 100.00, "customer_email": "user1@test.com"})
    client.post("/ingest/manual", json={"amount": 200.00, "customer_email": "user2@test.com"})
    
    response = client.get("/revenue/events")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    
    # Should be ordered by created_at desc (newest first)
    assert data[0]["amount_dollars"] == 200.00
    assert data[1]["amount_dollars"] == 100.00


def test_revenue_events_pagination(client, test_db):
    """Test pagination of revenue events."""
    # Add multiple transactions
    for i in range(5):
        client.post("/ingest/manual", json={"amount": 10.00 * (i + 1)})
    
    # Test limit
    response = client.get("/revenue/events?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # Test offset
    response = client.get("/revenue/events?limit=2&offset=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_csv_upload(client, test_db):
    """Test CSV upload endpoint."""
    csv_content = """amount,email,entity
100.50,user1@test.com,A+ Enterprise LLC
200.75,user2@test.com,Legacy Unchained Inc
50.00,user3@test.com,A+ Enterprise LLC"""
    
    files = {"file": ("test.csv", csv_content, "text/csv")}
    data = {
        "amount_column": "amount",
        "email_column": "email",
        "entity_column": "entity"
    }
    
    response = client.post("/ingest/csv", files=files, data=data)
    assert response.status_code == 200
    
    result = response.json()
    assert result["success"] is True
    assert result["created_count"] == 3
    assert result["total_rows"] == 3
    
    # Verify data was actually saved
    summary_response = client.get("/revenue/summary")
    summary = summary_response.json()
    assert summary["count"] == 3
    assert summary["total_dollars"] == 351.25  # 100.50 + 200.75 + 50.00


def test_csv_upload_missing_column(client, test_db):
    """Test CSV upload with missing required column."""
    csv_content = """email,entity
user1@test.com,A+ Enterprise LLC"""
    
    files = {"file": ("test.csv", csv_content, "text/csv")}
    data = {"amount_column": "amount"}
    
    response = client.post("/ingest/csv", files=files, data=data)
    assert response.status_code == 400
    assert "not found in CSV" in response.json()["detail"]


def test_webhook_endpoints_exist(client):
    """Test that webhook endpoints exist (even if not implemented)."""
    response = client.post("/webhooks/stripe")
    assert response.status_code == 200
    
    response = client.post("/webhooks/gumroad")
    assert response.status_code == 200


# Cleanup test database after all tests
def teardown_module(module):
    """Clean up test database file."""
    import os
    try:
        os.remove("test_branchbot.db")
    except FileNotFoundError:
        pass
