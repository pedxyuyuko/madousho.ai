from loguru import logger
from .config import configure_logging

# 注意：不在模块导入时自动初始化
# 调用方需要显式调用 configure_logging()


def get_logger(name: str | None = None):
    """
    获取 logger 实例
    
    Args:
        name: 可选的 logger 名称
              None → 返回主 logger
              str → 返回绑定 name 的子 logger
    
    Returns:
        Loguru Logger instance
    
    Examples:
        >>> logger = get_logger()
        >>> logger.info("消息")
        
        >>> auth_logger = get_logger("auth")
        >>> auth_logger.info("用户登录")
    """
    if name is None:
        return logger
    else:
        return logger.bind(name=name)


# 导出公共 API
__all__ = ["get_logger", "configure_logging"]
