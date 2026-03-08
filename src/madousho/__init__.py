"""Madousho.ai (魔导书) - Systematic AI Agent Framework."""

from ._version import __version__

# 导出 logging 相关函数（不自动初始化）
from .logging import get_logger

__all__ = ["__version__", "get_logger"]
