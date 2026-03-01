from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class APIConfig(BaseModel):
    """Configuration for the API server."""

    model_config = ConfigDict(extra="forbid")

    host: str
    port: int
    token: Optional[str] = None

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if v < 1 or v > 65535:
            raise ValueError("port must be between 1 and 65535")
        return v


class ProviderConfig(BaseModel):
    """Configuration for a single provider."""

    model_config = ConfigDict(extra="forbid")

    type: str
    endpoint: str
    api_key: str


class Config(BaseModel):
    """Main application configuration."""

    model_config = ConfigDict(extra="forbid")

    api: APIConfig
    provider: Dict[str, ProviderConfig]
    default_model_group: str
    model_groups: Dict[str, List[str]]
