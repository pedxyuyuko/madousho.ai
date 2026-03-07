"""Unit tests for API routes and endpoints."""

import pytest
from fastapi.testclient import TestClient

from madousho.api.app import create_app


@pytest.fixture
def client():
    """Create test client for API testing."""
    from madousho.config import get_config
    app = create_app()
    token = get_config().api.token
    with TestClient(app, headers={"Authorization": f"Bearer {token}"}) as test_client:
        yield test_client


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check_returns_200(self, client):
        """Test that GET /api/v1/health returns 200 status code."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_check_response_format(self, client):
        """Test that health check response contains required fields."""
        response = client.get("/api/v1/health")
        data = response.json()
        
        assert "status" in data
        assert "version" in data
        assert data["status"] == "ok"

    def test_health_check_version_field(self, client):
        """Test that health check response version is a non-empty string."""
        response = client.get("/api/v1/health")
        data = response.json()
        
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0


class TestNotFoundRoutes:
    """Tests for 404 not found scenarios."""

    def test_nonexistent_route_returns_404(self, client):
        """Test that accessing a non-existent route returns 404."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_nonexistent_root_route_returns_404(self, client):
        """Test that accessing a non-existent root route returns 404."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_nonexistent_api_route_returns_404(self, client):
        """Test that accessing a non-existent API route returns 404."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
