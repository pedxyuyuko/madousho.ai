from loguru import logger
import sys

# Remove default handler
logger.remove()

# Console handler (colored)
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True
)

# JSON file handler
logger.add(
    "logs/app.log",
    format="{message}",
    level="INFO",
    serialize=True,
    rotation="10 MB",
    compression=".gz",
    retention="7 days"
)

__all__ = ["logger"]
