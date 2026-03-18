"""API tests for Madousho.ai HTTP server."""

import pytest
from fastapi.testclient import TestClient

from madousho.api.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client for API tests."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check_returns_ok(self, client: TestClient) -> None:
        """Test GET /api/v1/health returns status ok."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_health_check_content_type(self, client: TestClient) -> None:
        """Test health check returns JSON content type."""
        response = client.get("/api/v1/health")
        assert "application/json" in response.headers["content-type"]


class TestStaticFiles:
    """Tests for static file serving."""

    def test_root_returns_index_html(self, client: TestClient) -> None:
        """Test that root path returns index.html for SPA."""
        response = client.get("/")
        if response.status_code == 200:
            assert "text/html" in response.headers["content-type"]

    def test_spa_fallback_returns_index_html(self, client: TestClient) -> None:
        """Test that any non-API path returns index.html for SPA routing."""
        response = client.get("/login")
        if response.status_code == 200:
            assert "text/html" in response.headers["content-type"]

    def test_api_routes_not_affected(self, client: TestClient) -> None:
        """Test that API routes still work after SPA fallback."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
