"""Smoke tests for prove-it endpoints."""
import pytest
from fastapi.testclient import TestClient

from branchberg.app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_endpoint_returns_200_and_ok(client):
    """Test health endpoint returns 200 with status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_version_endpoint_returns_200_and_has_fields(client):
    """Test version endpoint returns 200 with required fields."""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "git_sha" in data
    assert isinstance(data["version"], str)
    assert isinstance(data["git_sha"], str)
