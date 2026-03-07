"""Integration tests for Madousho API server."""
import pytest
from fastapi.testclient import TestClient
from madousho.api.app import create_app
from madousho.config import get_config


class TestHealthEndpoint:
    """Test health check endpoint functionality."""

    def test_health_check_returns_ok(self):
        """Test that health check endpoint returns status ok."""
        app = create_app()
        client = TestClient(app)

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_health_check_no_auth_required(self):
        """Test that health check endpoint does not require authentication."""
        app = create_app()
        client = TestClient(app)

        # Health check should be accessible without authentication
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_check_version_format(self):
        """Test that version field has valid format."""
        app = create_app()
        client = TestClient(app)

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        version = data["version"]
        assert isinstance(version, str)
        assert len(version) > 0


class TestAppConfiguration:
    """Test app configuration."""

    def test_app_creation_with_title(self):
        """Test that app is created with correct title."""
        app = create_app()
        assert app.title == "Madousho AI API"

    def test_app_creation_with_description(self):
        """Test that app is created with description."""
        app = create_app()
        assert app.description == "Systematic AI Agent Framework with fixed flow control + AI-executed steps"

    def test_app_has_health_router(self):
        """Test that app includes health router."""
        app = create_app()
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
