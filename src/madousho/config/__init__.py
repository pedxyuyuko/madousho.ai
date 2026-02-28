"""Configuration module for madousho.ai.

This module provides configuration loading and validation functionality.

Usage:
    from madousho.config import load_config, Config
    
    config = load_config("config.yaml")
    print(config.api.host)
"""

from .models import APIConfig, ProviderConfig, Config
from .loader import load_config

__all__ = ["APIConfig", "ProviderConfig", "Config", "load_config"]