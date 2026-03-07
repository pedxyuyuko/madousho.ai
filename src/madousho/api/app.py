from madousho.api.middleware.auth import TokenAuth
from madousho.config import get_config
from fastapi import FastAPI, Depends
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
    
    # Load configuration
    config = get_config()
    
    # Create public router (no authentication required)
    public_router = APIRouter()
    
    # Include health check router (public access)
    from madousho.api.routes.health import router as health_router
    public_router.include_router(health_router)
    
    # Create API router with v1 prefix (authentication required)
    api_router = APIRouter(
        prefix="/api/v1",
        dependencies=[Depends(TokenAuth(token=config.api.token))]
    )
    
    # Include routers
    app.include_router(public_router)
    # app.include_router(api_router)  # Commented out as no routes added yet
    
    logger.info(f"FastAPI application initialized with version {__version__}")
    
    return app
