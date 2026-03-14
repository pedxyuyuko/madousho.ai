"""TDD test suite for API authentication (RED phase).

Tests cover token verification via Authorization header (Bearer scheme)
and X-API-Token header. These tests will FAIL until verify_token() is
implemented - this is expected behavior for the RED phase.
"""

import pytest
from types import SimpleNamespace
from fastapi.testclient import TestClient

from madousho.api.main import app
from madousho.config import loader


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TEST_TOKEN = "test-token-123"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class MockConfig:
    """Minimal mock config with api.token for auth testing."""

    def __init__(self, token: str = TEST_TOKEN) -> None:
        self.api = SimpleNamespace(token=token)


@pytest.fixture
def mock_config(monkeypatch: pytest.MonkeyPatch) -> MockConfig:
    """Patch _cached_config so get_config() returns a controlled token."""
    cfg = MockConfig()
    monkeypatch.setattr(loader, "_cached_config", cfg)
    return cfg


@pytest.fixture
def client() -> TestClient:
    """Create TestClient for the FastAPI app."""
    return TestClient(app)


# ---------------------------------------------------------------------------
# Test classes
# ---------------------------------------------------------------------------


class TestAuthMissingToken:
    """Requests without any authentication header must be rejected."""

    def test_no_auth_header_returns_401(
        self, client: TestClient, mock_config: MockConfig
    ) -> None:
        """Request without Authorization or X-API-Token should get 401."""
        response = client.get("/api/v1/protected")
        assert response.status_code == 401

    def test_no_auth_header_error_body(
        self, client: TestClient, mock_config: MockConfig
    ) -> None:
        """401 response should include error detail in JSON body."""
        response = client.get("/api/v1/protected")
        body = response.json()
        assert "detail" in body or "error" in body


class TestAuthBearerToken:
    """Bearer token authentication via Authorization header."""

    def test_valid_bearer_token_passes(
        self, client: TestClient, mock_config: MockConfig
    ) -> None:
        """Correct Bearer token should allow access (200)."""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        response = client.get("/api/v1/protected", headers=headers)
        assert response.status_code == 200

    def test_wrong_bearer_token_returns_401(
        self, client: TestClient, mock_config: MockConfig
    ) -> None:
        """Incorrect Bearer token value should be rejected with 401."""
        headers = {"Authorization": "Bearer wrong-token-value"}
        response = client.get("/api/v1/protected", headers=headers)
        assert response.status_code == 401

    def test_empty_bearer_token_returns_401(
        self, client: TestClient, mock_config: MockConfig
    ) -> None:
        """Bearer scheme with empty token string should be rejected with 401."""
        headers = {"Authorization": "Bearer "}
        response = client.get("/api/v1/protected", headers=headers)
        assert response.status_code == 401

    def test_wrong_auth_scheme_returns_401(
        self, client: TestClient, mock_config: MockConfig
    ) -> None:
        """Non-Bearer scheme (e.g. Basic) should be rejected with 401."""
        headers = {"Authorization": "Basic dXNlcjpwYXNz"}
        response = client.get("/api/v1/protected", headers=headers)
        assert response.status_code == 401


class TestAuthXApiToken:
    """X-API-Token header authentication."""

    def test_valid_x_api_token_passes(
        self, client: TestClient, mock_config: MockConfig
    ) -> None:
        """Correct X-API-Token header should allow access (200)."""
        headers = {"X-API-Token": TEST_TOKEN}
        response = client.get("/api/v1/protected", headers=headers)
        assert response.status_code == 200

    def test_wrong_x_api_token_returns_401(
        self, client: TestClient, mock_config: MockConfig
    ) -> None:
        """Incorrect X-API-Token value should be rejected with 401."""
        headers = {"X-API-Token": "wrong-token-value"}
        response = client.get("/api/v1/protected", headers=headers)
        assert response.status_code == 401


class TestAuthHeaderPriority:
    """Authorization header takes priority over X-API-Token when both present."""

    def test_authorization_takes_priority_over_x_api_token(
        self, client: TestClient, mock_config: MockConfig
    ) -> None:
        """When both headers are present, Authorization is used for validation.

        Sending a valid X-API-Token but invalid Bearer should fail because
        Authorization takes priority.
        """
        headers = {
            "Authorization": "Bearer wrong-token",
            "X-API-Token": TEST_TOKEN,
        }
        response = client.get("/api/v1/protected", headers=headers)
        assert response.status_code == 401


class TestHealthEndpointBypass:
    """Health check endpoint must remain accessible without authentication."""

    def test_health_endpoint_no_auth_returns_200(
        self, client: TestClient, mock_config: MockConfig
    ) -> None:
        """GET /api/v1/health should return 200 even without auth headers."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestOptionsBypass:
    """OPTIONS requests (CORS preflight) must skip authentication."""

    def test_options_request_skips_auth(
        self, client: TestClient, mock_config: MockConfig
    ) -> None:
        """OPTIONS request should be allowed without any auth header."""
        response = client.options("/api/v1/protected")
        # OPTIONS should not return 401 - it should be allowed through
        assert response.status_code != 401


class TestOpenAPISecurityScheme:
    """OpenAPI specification must declare the authentication security scheme."""

    def test_openapi_includes_security_schemes(self, client: TestClient) -> None:
        """GET /openapi.json should contain securitySchemes definition."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        spec = response.json()
        assert "components" in spec
        assert "securitySchemes" in spec["components"]
        schemes = spec["components"]["securitySchemes"]
        # Should have at least one security scheme (e.g. BearerAuth or ApiKeyAuth)
        assert len(schemes) > 0

    def test_openapi_has_bearer_or_apikey_scheme(self, client: TestClient) -> None:
        """Security scheme should define Bearer token or API key authentication."""
        response = client.get("/openapi.json")
        spec = response.json()
        schemes = spec["components"]["securitySchemes"]
        scheme_values = list(schemes.values())
        # At least one scheme should be http/bearer or apiKey type
        has_valid_scheme = any(
            s.get("type") in ("http", "apiKey") for s in scheme_values
        )
        assert has_valid_scheme, f"Expected http or apiKey scheme, got: {schemes}"
