"""Base model definitions for SQLAlchemy"""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, DateTime
from datetime import datetime, timezone
from typing import Optional


class Base(DeclarativeBase):
    """SQLAlchemy DeclarativeBase - 所有模型的基类"""

    pass


class BaseModel(Base):
    """
    抽象基类，包含可选的通用字段

    Usage:
        # 模式 1: 使用自增 ID（继承 BaseModel）
        class User(BaseModel):
            __tablename__ = "users"
            name = mapped_column(String(50))

        # 模式 2: 使用 UUID 或其他主键（直接继承 Base）
        class User(Base):
            __tablename__ = "users"
            id = mapped_column(String(36), primary_key=True)
            name = mapped_column(String(50))
    """

    __abstract__ = True  # 不创建表，只作为基类

    # 可选的自增 ID 字段
    id: Mapped[Optional[int]] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=True
    )

    # 可选的创建时间字段
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=True
    )

    # 可选的更新时间字段
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True,
    )
