"""Configuration module for madousho.ai.

This module provides configuration loading and validation functionality.

Usage:
    from madousho.config import init_config, get_config, Config
    
    # Initialize once at startup
    init_config("/path/to/config/dir")
    
    # Get config anywhere
    config = get_config()
    print(config.api.host)
"""

from .models import APIConfig, ProviderConfig, Config
from .loader import ConfigManager, init_config, get_config

__all__ = ["APIConfig", "ProviderConfig", "Config", "ConfigManager", "init_config", "get_config"]