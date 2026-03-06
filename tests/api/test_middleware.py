"""Unit tests for API middleware authentication."""

import pytest
from starlette.testclient import TestClient
from fastapi import FastAPI, status

from madousho.api.middleware.auth import TokenAuthMiddleware


def create_test_app(token=None):
    """Helper to create test app with middleware."""
    app = FastAPI()
    app.add_middleware(TokenAuthMiddleware, token=token)
    
    @app.get("/test")
    def test_endpoint():
        return {"status": "ok"}
    
    return app


class TestTokenAuthMiddleware:
    """Tests for TokenAuthMiddleware authentication."""

    def test_valid_token_allowed(self):
        """Test that requests with valid token are allowed through."""
        app = create_test_app(token="test-token-123")
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test", headers={"authorization": "Bearer test-token-123"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}

    def test_invalid_token_rejected(self):
        """Test that requests with invalid token are rejected."""
        app = create_test_app(token="test-token-123")
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test", headers={"authorization": "Bearer wrong-token"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid token"

    def test_empty_token_config_allows_no_auth(self):
        """Test that None token config allows requests without authentication."""
        app = create_test_app(token=None)
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}

    def test_missing_authorization_header_rejected(self):
        """Test that missing Authorization header is rejected when token is configured."""
        app = create_test_app(token="test-token-123")
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Authorization header is required"

    def test_invalid_authorization_header_format_rejected(self):
        """Test that invalid Authorization header format is rejected."""
        app = create_test_app(token="test-token-123")
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/test", headers={"authorization": "test-token-123"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid authorization header format"

        response = client.get("/test", headers={"authorization": "Basic test-token-123"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid authorization header format"

    def test_bearer_case_insensitive(self):
        """Test that Bearer prefix is case insensitive."""
        app = create_test_app(token="test-token-123")
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/test", headers={"authorization": "bearer test-token-123"})
        assert response.status_code == status.HTTP_200_OK

        response = client.get("/test", headers={"authorization": "BeArEr test-token-123"})
        assert response.status_code == status.HTTP_200_OK

        response = client.get("/test", headers={"authorization": "BEARER test-token-123"})
        assert response.status_code == status.HTTP_200_OK


class TestTokenAuthMiddlewareEdgeCases:
    """Edge case tests for TokenAuthMiddleware."""

    def test_special_characters_in_token(self):
        """Test tokens with special characters are handled correctly."""
        special_token = "test-token_with.special!chars@#123"
        app = create_test_app(token=special_token)
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/test", headers={"authorization": f"Bearer {special_token}"})
        assert response.status_code == status.HTTP_200_OK

        response = client.get("/test", headers={"authorization": "Bearer test-token_with.special!chars@#124"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid token"

    def test_long_token(self):
        """Test very long tokens are handled correctly."""
        long_token = "a" * 1000
        app = create_test_app(token=long_token)
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/test", headers={"authorization": f"Bearer {long_token}"})
        assert response.status_code == status.HTTP_200_OK

        wrong_long_token = "a" * 999 + "b"
        response = client.get("/test", headers={"authorization": f"Bearer {wrong_long_token}"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid token"

    def test_empty_string_token(self):
        """Test empty string token is treated as no authentication (falsy value)."""
        app = create_test_app(token="")
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/test", headers={"authorization": "Bearer anything"})
        assert response.status_code == status.HTTP_200_OK

    def test_whitespace_in_token(self):
        """Test tokens with leading/trailing whitespace are handled correctly."""
        token_with_spaces = "  test-token  "
        app = create_test_app(token=token_with_spaces)
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/test", headers={"authorization": "Bearer test-token"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid token"

        response = client.get("/test", headers={"authorization": f"Bearer {token_with_spaces}"})
        assert response.status_code == status.HTTP_200_OK

    def test_unicode_token(self):
        """Test tokens with unicode characters are handled correctly."""
        unicode_token = "test-token-🔐-secret"
        app = create_test_app(token=unicode_token)
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/test", headers={"authorization": f"Bearer {unicode_token}"})
        assert response.status_code == status.HTTP_200_OK

        response = client.get("/test", headers={"authorization": "Bearer test-token-🔑-secret"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid token"

    def test_token_with_spaces_between_bearer_and_token(self):
        """Test multiple spaces between Bearer and token are handled."""
        app = create_test_app(token="test-token-123")
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/test", headers={"authorization": "Bearer    test-token-123"})
        assert response.status_code == status.HTTP_200_OK

    def test_malformed_authorization_headers(self):
        """Test various malformed Authorization headers are rejected."""
        app = create_test_app(token="test-token-123")
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/test", headers={"authorization": ""})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid authorization header format"

        response = client.get("/test", headers={"authorization": "Bearer"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid authorization header format"

        response = client.get("/test", headers={"authorization": "Bearer "})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid token"


class TestExtractTokenFromHeader:
    """Tests for the _extract_token_from_auth_header helper method."""

    def test_extract_valid_bearer_token(self):
        """Test extracting token from valid Bearer header."""
        middleware = TokenAuthMiddleware(app=None, token="test")
        token = middleware._extract_token_from_auth_header("Bearer test-token-123")
        assert token == "test-token-123"

    def test_extract_token_case_insensitive(self):
        """Test token extraction is case insensitive for Bearer prefix."""
        middleware = TokenAuthMiddleware(app=None, token="test")

        assert middleware._extract_token_from_auth_header("bearer test-token") == "test-token"
        assert middleware._extract_token_from_auth_header("BEARER test-token") == "test-token"
        assert middleware._extract_token_from_auth_header("BeArEr test-token") == "test-token"

    def test_extract_token_strips_whitespace(self):
        """Test that extracted token has whitespace stripped."""
        middleware = TokenAuthMiddleware(app=None, token="test")
        token = middleware._extract_token_from_auth_header("Bearer   test-token   ")
        assert token == "test-token"

    def test_extract_token_invalid_format_returns_none(self):
        """Test that invalid formats return None."""
        middleware = TokenAuthMiddleware(app=None, token="test")

        assert middleware._extract_token_from_auth_header("test-token") is None
        assert middleware._extract_token_from_auth_header("Basic test-token") is None
        assert middleware._extract_token_from_auth_header("") is None
        assert middleware._extract_token_from_auth_header("Bearer") is None

    def test_extract_token_with_special_characters(self):
        """Test extracting tokens with special characters."""
        middleware = TokenAuthMiddleware(app=None, token="test")
        special_token = "test-token_with.special!chars@#123"
        token = middleware._extract_token_from_auth_header(f"Bearer {special_token}")
        assert token == special_token

    def test_extract_token_unicode(self):
        """Test extracting tokens with unicode characters."""
        middleware = TokenAuthMiddleware(app=None, token="test")
        unicode_token = "test-token-🔐-secret"
        token = middleware._extract_token_from_auth_header(f"Bearer {unicode_token}")
        assert token == unicode_token
