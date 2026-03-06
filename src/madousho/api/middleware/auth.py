"""Token authentication middleware."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import re
from typing import Optional


class TokenAuthMiddleware(BaseHTTPMiddleware):
    """Token authentication middleware that validates Bearer tokens."""

    def __init__(self, app, token: Optional[str] = None):
        """
        Initialize the middleware with the expected token.
        
        Args:
            app: The FastAPI app instance (provided by FastAPI)
            token: The token to validate against. If None, authentication is disabled.
        """
        super().__init__(app)
        self.token = token

    async def dispatch(self, request: Request, call_next):
        """
        Process incoming requests and validate token if configured.
        
        Args:
            request: The incoming request
            call_next: The next middleware/function to call
            
        Returns:
            Response from the next middleware/function
        """
        # If no token is configured, allow all requests
        if not self.token:
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authorization header is required"}
            )
        
        # Extract token from "Bearer <token>" format
        token_from_header = self._extract_token_from_auth_header(auth_header)
        if not token_from_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authorization header format"}
            )
        
        # Validate token
        if token_from_header != self.token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )
        
        # Token is valid, proceed with the request
        return await call_next(request)

    def _extract_token_from_auth_header(self, auth_header: str) -> Optional[str]:
        """
        Extract token from Authorization header in "Bearer <token>" format.
        
        Args:
            auth_header: The Authorization header value
            
        Returns:
            The extracted token or None if format is invalid
        """
        # Match "Bearer <token>" format (case insensitive for "Bearer")
        match = re.match(r"^bearer\s+(.+)$", auth_header, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
