"""Test for /health endpoint to ensure API module loads correctly."""
import pytest
from fastapi.testclient import TestClient

from branchberg.app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_endpoint(client):
    """Test /health endpoint returns OK status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data


def test_health_endpoint_structure(client):
    """Test /health endpoint returns expected structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "status" in data
    assert data["status"] == "ok"
