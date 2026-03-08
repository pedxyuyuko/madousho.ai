"""Serve command for Madousho.ai API server."""

from madousho.config.loader import init_config, get_config_file
from madousho.logging.config import configure_logging
from loguru import logger


def serve():
    """Madousho.ai API server."""
    # Get the actual config file path that will be used
    config_path = get_config_file(None)

    # Load configuration
    _ = init_config()

    # Initialize logging
    configure_logging()

    # Output startup information
    logger.info("Server starting...")
    logger.info(f"Configuration loaded from: {config_path}")
    logger.info("Madousho serve is ready (API server not yet implemented)")
