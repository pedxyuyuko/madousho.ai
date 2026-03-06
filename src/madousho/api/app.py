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
    
    # Create API router with v1 prefix
    api_router = APIRouter(prefix="/api/v1")
    
    # Include API routes here (will be imported in other modules)
    # app.include_router(api_router)  # Commented out as no routes added yet
    
    logger.info(f"FastAPI application initialized with version {__version__}")
    
    return app