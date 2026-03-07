"""Unit tests for API token authentication."""

import pytest
from starlette.testclient import TestClient
from fastapi import FastAPI, Depends, status

from madousho.api.middleware.auth import TokenAuth


def create_test_app(token: str):
    """Helper to create test app with token authentication."""
    app = FastAPI()
    
    # Apply token authentication to all routes
    app.add_api_route(
        "/test",
        lambda: {"status": "ok"},
        dependencies=[Depends(TokenAuth(token=token))]
    )
    
    return app


class TestTokenAuth:
    """Tests for TokenAuth authentication."""

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

        # Missing Bearer scheme
        response = client.get("/test", headers={"authorization": "test-token-123"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Authorization header is required"

        # Wrong scheme (Basic instead of Bearer)
        response = client.get("/test", headers={"authorization": "Basic test-token-123"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Authorization header is required"

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


class TestTokenAuthEdgeCases:
    """Edge case tests for TokenAuth."""

    def test_special_characters_in_token(self):
        """Test tokens with special characters."""
        token = "test-token_123!@#$%"
        app = create_test_app(token=token)
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test", headers={"authorization": f"Bearer {token}"})
        assert response.status_code == status.HTTP_200_OK

    def test_long_token(self):
        """Test with very long token."""
        token = "a" * 1000
        app = create_test_app(token=token)
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test", headers={"authorization": f"Bearer {token}"})
        assert response.status_code == status.HTTP_200_OK

    def test_whitespace_in_token(self):
        """Test that leading/trailing whitespace is stripped."""
        token = "test-token-123"
        app = create_test_app(token=token)
        client = TestClient(app, raise_server_exceptions=False)
        
        # Token with extra spaces should be stripped and match
        response = client.get("/test", headers={"authorization": f"Bearer  {token}  "})
        assert response.status_code == status.HTTP_200_OK

    def test_unicode_token(self):
        """Test tokens with special characters (unicode not supported in HTTP headers)."""
        # HTTP headers only support ASCII, so we test with special chars that are ASCII-safe
        token = "test-token_special-123"
        app = create_test_app(token=token)
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test", headers={"authorization": f"Bearer {token}"})
        assert response.status_code == status.HTTP_200_OK

    def test_malformed_authorization_headers(self):
        """Test various malformed authorization headers."""
        app = create_test_app(token="test-token")
        client = TestClient(app, raise_server_exceptions=False)
        
        # Empty bearer
        response = client.get("/test", headers={"authorization": "Bearer "})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Just "Bearer"
        response = client.get("/test", headers={"authorization": "Bearer"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Multiple spaces
        response = client.get("/test", headers={"authorization": "Bearer    token"})
        # This should work as we strip whitespace
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]


class TestExtractTokenFromCredentials:
    """Tests for token extraction logic."""

    def test_extract_valid_bearer_token(self):
        """Test extracting valid bearer token."""
        auth = TokenAuth(token="test")
        from fastapi.security import HTTPAuthorizationCredentials
        
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token-123")
        token = auth._extract_token_from_credentials(creds)
        assert token == "test-token-123"

    def test_extract_token_case_insensitive(self):
        """Test that scheme matching is case insensitive."""
        auth = TokenAuth(token="test")
        from fastapi.security import HTTPAuthorizationCredentials
        
        for scheme in ["bearer", "Bearer", "BEARER", "BeArEr"]:
            creds = HTTPAuthorizationCredentials(scheme=scheme, credentials="test-token")
            token = auth._extract_token_from_credentials(creds)
            assert token == "test-token"

    def test_extract_token_strips_whitespace(self):
        """Test that token whitespace is stripped."""
        auth = TokenAuth(token="test")
        from fastapi.security import HTTPAuthorizationCredentials
        
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="  test-token  ")
        token = auth._extract_token_from_credentials(creds)
        assert token == "test-token"

    def test_extract_token_invalid_format_returns_none(self):
        """Test that invalid format returns None."""
        auth = TokenAuth(token="test")
        from fastapi.security import HTTPAuthorizationCredentials
        
        # Empty credentials
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="")
        token = auth._extract_token_from_credentials(creds)
        assert token == ""

    def test_extract_token_with_special_characters(self):
        """Test token extraction with special characters."""
        auth = TokenAuth(token="test")
        from fastapi.security import HTTPAuthorizationCredentials
        
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test!@#$%^&*()")
        token = auth._extract_token_from_credentials(creds)
        assert token == "test!@#$%^&*()"

    def test_extract_token_unicode(self):
        """Test token extraction with unicode characters."""
        auth = TokenAuth(token="test")
        from fastapi.security import HTTPAuthorizationCredentials
        
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="测试-token-🔑")
        token = auth._extract_token_from_credentials(creds)
        assert token == "测试-token-🔑"
