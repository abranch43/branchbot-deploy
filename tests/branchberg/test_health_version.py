"""Tests for health and version endpoints."""
import pytest
from fastapi.testclient import TestClient

from branchberg.app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_includes_status(client):
    """Health endpoint returns 200 and status field."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_version_includes_version_field(client):
    """Version endpoint returns 200 and version field."""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
