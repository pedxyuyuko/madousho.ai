import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from src.madousho.database.base_model import Base
from src.madousho.models.enums import FlowStatus


class Flow(Base):
    """Flow model for storing AI agent workflow definitions."""

    __tablename__: str = "flows"

    uuid: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    plugin: Mapped[str] = mapped_column(String(255), nullable=False)
    tasks: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True, comment="List of task UUIDs"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="created", index=True
    )
    flow_template: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=True
    )
