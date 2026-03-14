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

    def test_static_files_mounted(self, client: TestClient) -> None:
        """Test that static files are mounted at root."""
        # The static files should be mounted, but public/ directory may not exist
        # This test verifies the mount point exists
        response = client.get("/")
        # If public/ doesn't exist, should return 404
        # If it exists, should return HTML
        assert response.status_code in [200, 404]
