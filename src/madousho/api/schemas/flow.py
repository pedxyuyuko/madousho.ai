"""Pydantic schemas for Flow CRUD API endpoints."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class FlowCreate(BaseModel):
    """Request body for creating a new Flow.

    Attributes:
        name: Flow name (required)
        plugin: Plugin identifier (required)
        flow_template: Template name string (required)
        description: Optional description
    """

    name: str = Field(description="Flow name")
    plugin: str = Field(description="Plugin identifier")
    flow_template: str = Field(description="Template name")
    description: str | None = Field(default=None, description="Optional description")


class FlowResponse(BaseModel):
    """Response model for a single Flow.

    Attributes:
        uuid: Unique identifier
        name: Flow name
        description: Optional description
        plugin: Plugin identifier
        tasks: List of task UUIDs
        status: Current status (created, processing, finished)
        flow_template: Template name
        created_at: Creation timestamp
    """

    uuid: str = Field(description="Unique identifier")
    name: str = Field(description="Flow name")
    description: str | None = Field(default=None, description="Optional description")
    plugin: str = Field(description="Plugin identifier")
    tasks: list[str] | None = Field(default=None, description="List of task UUIDs")
    status: str = Field(description="Current status")
    flow_template: str | None = Field(default=None, description="Template name")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")


class FlowListResponse(BaseModel):
    """Response model for paginated Flow list.

    Attributes:
        items: List of Flow objects
        total: Total number of matching flows
        offset: Current offset
        limit: Current limit
    """

    items: list[FlowResponse] = Field(description="List of Flows")
    total: int = Field(description="Total number of matching flows")
    offset: int = Field(description="Current offset")
    limit: int = Field(description="Current limit")
