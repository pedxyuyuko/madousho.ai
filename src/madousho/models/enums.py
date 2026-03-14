"""Flow status enums for lifecycle management."""

from enum import Enum


class FlowStatus(Enum):
    """Flow lifecycle status values."""

    CREATED = "created"
    PROCESSING = "processing"
    FINISHED = "finished"
