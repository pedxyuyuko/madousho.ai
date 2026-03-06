from loguru import logger
import sys

# Track if logger has been configured
_configured = False

def configure_logger(verbose: bool = False, json_output: bool = False):
    """
    Configure logger with specified level and format.
    
    Args:
        verbose: If True, set level to DEBUG; otherwise INFO
        json_output: If True, use JSON format for console output
    """
    global _configured
    
    if _configured:
        # Already configured, remove existing handlers
        logger.remove()
    
    # Set log level
    level = "DEBUG" if verbose else "INFO"
    
    if json_output:
        # JSON format for console
        logger.add(
            sys.stderr,
            format="{message}",
            level=level,
            serialize=True
        )
    else:
        # Colored console format with optional plugin context
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - {extra[plugin]}<level>{message}</level>",
            level=level,
            colorize=True
        )
    
    # JSON file handler (always enabled)
    logger.add(
        "logs/app.log",
        format="{message}",
        level="DEBUG",
        serialize=True,
        rotation="10 MB",
        compression=".gz",
        retention="7 days"
    )
    
    _configured = True

# Auto-configure with default settings on import
configure_logger(verbose=False, json_output=False)

# Set default plugin context
logger = logger.bind(plugin="")

__all__ = ["logger", "configure_logger"]
