"""Pydantic models for Madousho configuration."""

import secrets
from typing import Dict, List

from loguru import logger
from pydantic import BaseModel, Field, field_validator, model_validator


class ApiConfig(BaseModel):
    """Configuration for the API server."""

    token: str = Field(default="", description="API authentication token")
    host: str = Field(default="0.0.0.0", description="Server host address")
    port: int = Field(default=8000, description="Server port number")
    _token_generated: bool = False

    @model_validator(mode="after")
    def generate_token_if_empty(self) -> "ApiConfig":
        """Generate a random 32-bit token if not provided and warn user."""
        if not self.token:
            # Generate a 32-character hex token (128 bits of entropy)
            self.token = secrets.token_hex(16)
            self._token_generated = True
            logger.warning(
                f"API token was empty, generated random token: {self.token}. "
                "Token will be saved to config file automatically."
            )
        return self

    def token_was_generated(self) -> bool:
        """Check if the token was auto-generated."""
        return self._token_generated


class ProviderConfig(BaseModel):
    """Configuration for a model provider."""

    type: str = Field(default="openai-compatible", description="Provider type")
    endpoint: str = Field(default="", description="Provider API endpoint URL")
    api_key: str = Field(default="", alias="api-key", description="Provider API key")


class SqliteConfig(BaseModel):
    """Configuration for SQLite WAL mode and performance tuning."""

    wal_enabled: bool = Field(
        default=True, description="Enable Write-Ahead Logging mode"
    )
    synchronous: str = Field(
        default="NORMAL", description="Synchronization mode (OFF, NORMAL, FULL, EXTRA)"
    )
    cache_size: int = Field(
        default=-64000, description="Page cache size (negative = KB, positive = pages)"
    )
    temp_store: str = Field(
        default="DEFAULT",
        description="Temporary storage location (DEFAULT, FILE, MEMORY)",
    )
    mmap_size: int = Field(
        default=268435456, description="Memory-mapped I/O size in bytes (256MB default)"
    )
    journal_size_limit: int = Field(
        default=67108864, description="WAL file size limit in bytes (64MB default)"
    )
    busy_timeout: int = Field(default=5000, description="Busy timeout in milliseconds")
    wal_autocheckpoint: int = Field(
        default=1000, description="Auto-checkpoint page count threshold"
    )
    locking_mode: str = Field(
        default="NORMAL", description="Database locking mode (NORMAL, EXCLUSIVE)"
    )
    foreign_keys: bool = Field(
        default=True, description="Enable foreign key constraints"
    )
    ignore_check_constraints: bool = Field(
        default=False, description="Ignore CHECK constraints"
    )

    @field_validator("synchronous")
    @classmethod
    def validate_synchronous_mode(cls, v: str) -> str:
        """验证 SQLite 同步模式"""
        valid_modes = ("OFF", "NORMAL", "FULL", "EXTRA")
        if v not in valid_modes:
            raise ValueError(
                f"Invalid synchronous mode: {v}. Must be one of {valid_modes}"
            )
        return v


class DatabaseConfig(BaseModel):
    """Database configuration."""

    url: str = Field(
        default="sqlite:///./madousho.db", description="Database connection URL"
    )
    sqlite: SqliteConfig = Field(
        default_factory=SqliteConfig, description="SQLite-specific configuration"
    )

    @field_validator("url")
    @classmethod
    def validate_url_scheme(cls, v: str) -> str:
        """验证数据库 URL 格式"""
        if not v.startswith(("sqlite://", "postgresql://", "mysql://")):
            raise ValueError(
                f"Invalid database URL scheme: {v}. Must start with sqlite://, postgresql://, or mysql://"
            )
        return v


class Config(BaseModel):
    """Main configuration model for Madousho."""

    api: ApiConfig = Field(description="API server configuration")
    database: DatabaseConfig = Field(
        default_factory=DatabaseConfig, description="Database configuration"
    )
    provider: Dict[str, ProviderConfig] = Field(description="Provider configurations")
    default_model_group: str = Field(description="Default model group identifier")
    model_groups: Dict[str, List[str]] = Field(
        description="Mapping of model group names to lists of model identifiers"
    )
