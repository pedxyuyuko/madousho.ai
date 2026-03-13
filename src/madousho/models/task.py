import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import String, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from src.madousho.database.base_model import BaseModel


class Task(BaseModel):
    """Task model for storing individual task execution data."""

    __tablename__: str = "tasks"

    uuid: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    flow_uuid: Mapped[str] = mapped_column(
        String(36), ForeignKey("flows.uuid", ondelete="CASCADE"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="pending, running, completed, failed"
    )
    timeout: Mapped[float | None] = mapped_column(nullable=True)
    messages: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True, comment="OpenAI format messages"
    )
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    __table_args__: tuple[Index, ...] = (
        Index("idx_task_flow_uuid", "flow_uuid"),
        Index("idx_task_state", "state"),
        Index("idx_task_created_at", "created_at"),
    )
