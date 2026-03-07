from madousho.api.middleware.auth import TokenAuthMiddleware
from madousho.config import get_config
from fastapi import FastAPI
from fastapi.routing import APIRouter
from loguru import logger
import sys

# Import version from madousho module
try:
    from madousho._version import __version__
except ImportError:
    try:
        from madousho import __version__
    except ImportError:
        __version__ = "0.1.0"  # fallback version


def create_app() -> FastAPI:
    """Create and configure FastAPI application instance."""
    
    # Configure loguru
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Initialize FastAPI app
    app = FastAPI(
        title="Madousho AI API",
        version=__version__,
        description="Systematic AI Agent Framework with fixed flow control + AI-executed steps",
    )
    
    # Load configuration and initialize auth middleware
    config = get_config()
    app.add_middleware(TokenAuthMiddleware, token=config.api.token)
    
    # Create API router with v1 prefix
    api_router = APIRouter(prefix="/api/v1")
    
    # Include health check router
    from madousho.api.routes.health import router as health_router
    app.include_router(health_router)
    # app.include_router(api_router)  # Commented out as no routes added yet
    
    logger.info(f"FastAPI application initialized with version {__version__}")
    
    return app
