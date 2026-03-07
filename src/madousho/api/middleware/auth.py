"""Token authentication for API routes."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import re
from typing import Optional


security = HTTPBearer(auto_error=False)


class TokenAuth:
    """Token authentication dependency for FastAPI routes."""
    
    def __init__(self, token: str):
        """
        Initialize with the expected token.
        
        Args:
            token: The token to validate against
        """
        self.token = token
    
    async def __call__(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> None:
        """
        Validate the token from Authorization header.
        
        Args:
            credentials: HTTP Bearer credentials from the request
            
        Raises:
            HTTPException: If authentication fails
        """
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header is required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract token from "Bearer <token>\" format
        token_from_header = self._extract_token_from_credentials(credentials)
        if not token_from_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Validate token
        if token_from_header != self.token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def _extract_token_from_credentials(
        self,
        credentials: HTTPAuthorizationCredentials
    ) -> Optional[str]:
        """
        Extract token from credentials.
        
        Args:
            credentials: HTTP Bearer credentials
            
        Returns:
            The extracted token or None if format is invalid
        """
        # Match "Bearer <token>" format (case insensitive for "Bearer")
        if re.match(r"^bearer\s+$", credentials.scheme, re.IGNORECASE):
            return None
        return credentials.credentials.strip()
