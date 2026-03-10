"""Database module for Madousho.ai."""

from .connection import Database
from .base_model import Base, BaseModel

__all__ = ["Database", "Base", "BaseModel"]
