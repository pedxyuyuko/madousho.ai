"""Pydantic models for Madousho configuration."""

from typing import Dict, List

from pydantic import BaseModel, Field


class ApiConfig(BaseModel):
    """Configuration for the API server."""

    token: str = Field(default="", description="API authentication token")
    host: str = Field(default="0.0.0.0", description="Server host address")
    port: int = Field(default=8000, description="Server port number")


class ProviderConfig(BaseModel):
    """Configuration for a model provider."""

    type: str = Field(default="openai-compatible", description="Provider type")
    endpoint: str = Field(default="", description="Provider API endpoint URL")
    api_key: str = Field(default="", alias="api-key", description="Provider API key")




class Config(BaseModel):
    """Main configuration model for Madousho."""

    api: ApiConfig = Field(description="API server configuration")
    provider: Dict[str, ProviderConfig] = Field(description="Provider configurations")
    default_model_group: str = Field(description="Default model group identifier")
    model_groups: Dict[str, List[str]] = Field(
        description="Mapping of model group names to lists of model identifiers"
    )
