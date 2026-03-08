from pathlib import Path
from loguru import logger
import sys
import os

# 项目根目录（向上三级：config.py -> logging/ -> madousho/ -> src/ -> 项目根目录）
# 使用绝对路径确保正确
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"

# 标准格式（彩色友好）
STANDARD_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# JSON 格式（结构化日志）
JSON_FORMAT = "{message}"


def configure_logging(
    level: str | None = None,
    is_json: bool = False,
    colorize: bool | None = None
) -> None:
    """
    配置日志 sinks（一次性初始化）
    
    Args:
        level: 日志级别（控制台 + 文件相同），默认从 LOGURU_LEVEL 环境变量读取
               可选："DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
        is_json: 是否使用 JSON 格式，默认 False
        colorize: 是否彩色输出，默认自动检测（JSON 时禁用）
    """
    # 1. 创建 logs 目录
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        pass  # 优雅降级
    
    # 2. 确定日志级别（参数 > 环境变量 > 默认）
    if level is None:
        level = os.getenv("LOGURU_LEVEL", "INFO").upper()
    
    # 3. 确定是否彩色（JSON 格式强制禁用）
    if colorize is None:
        colorize = not is_json and sys.stderr.isatty()
    else:
        colorize = colorize and not is_json
    
    # 4. 选择格式
    log_format = JSON_FORMAT if is_json else STANDARD_FORMAT
    
    # 5. 移除默认 handler
    logger.remove()
    
    # 6. 添加控制台输出
    logger.add(
        sink=sys.stderr,
        format=log_format,
        level=level,
        colorize=colorize,
        backtrace=True,
        diagnose=True,
        serialize=is_json
    )
    
    # 7. 添加文件输出（与控制台相同级别）
    logger.add(
        sink=LOGS_DIR / "madousho.log",
        format=log_format,
        level=level,
        rotation="100 MB",
        retention="7 days",
        enqueue=True,
        compression="zip",
        colorize=False
    )
