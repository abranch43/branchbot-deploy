#!/usr/bin/env python3
"""Manual test script for Income Ingest API."""
import sys
import os
import tempfile
import uuid

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from branchberg.app.main import app
from branchberg.app.database import Base, get_db


def get_test_db_engine():
    """Create a fresh test database engine."""
    test_db_path = os.path.join(tempfile.gettempdir(), f"test_branchbot_{uuid.uuid4().hex[:8]}.db")
    engine = create_engine(f"sqlite:///{test_db_path}", connect_args={"check_same_thread": False})
    return engine, test_db_path


def override_get_db(engine):
    """Create database session override."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    def _override():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    return _override


def setup_test_db(engine):
    """Create test database."""
    Base.metadata.create_all(bind=engine)
    
def teardown_test_db(engine, db_path):
    """Drop test database."""
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    try:
        os.remove(db_path)
    except FileNotFoundError:
        pass


def test_root_endpoint():
    """Test root endpoint returns OK status."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "BranchOS" in data["service"]
    print("✓ test_root_endpoint passed")


def test_manual_transaction_success():
    """Test manual transaction creation."""
    engine, db_path = get_test_db_engine()
    app.dependency_overrides[get_db] = override_get_db(engine)
    setup_test_db(engine)
    client = TestClient(app)
    
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
    
    teardown_test_db(engine, db_path)
    print("✓ test_manual_transaction_success passed")


def test_revenue_summary():
    """Test revenue summary with transactions."""
    engine, db_path = get_test_db_engine()
    app.dependency_overrides[get_db] = override_get_db(engine)
    setup_test_db(engine)
    client = TestClient(app)
    
    # Add two transactions
    client.post("/ingest/manual", json={"amount": 100.00})
    client.post("/ingest/manual", json={"amount": 50.50})
    
    response = client.get("/revenue/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_dollars"] == 150.50
    assert data["count"] == 2
    
    teardown_test_db(engine, db_path)
    print("✓ test_revenue_summary passed")


def test_revenue_events():
    """Test revenue events retrieval."""
    engine, db_path = get_test_db_engine()
    app.dependency_overrides[get_db] = override_get_db(engine)
    setup_test_db(engine)
    client = TestClient(app)
    
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
    
    teardown_test_db(engine, db_path)
    print("✓ test_revenue_events passed")


def test_csv_upload():
    """Test CSV upload endpoint."""
    engine, db_path = get_test_db_engine()
    app.dependency_overrides[get_db] = override_get_db(engine)
    setup_test_db(engine)
    client = TestClient(app)
    
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
    
    teardown_test_db(engine, db_path)
    print("✓ test_csv_upload passed")


if __name__ == "__main__":
    print("Running Income Ingest API tests...\n")
    
    try:
        test_root_endpoint()
        test_manual_transaction_success()
        test_revenue_summary()
        test_revenue_events()
        test_csv_upload()
        
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
