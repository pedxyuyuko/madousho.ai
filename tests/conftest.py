# pytest configuration file

import pytest
from pathlib import Path

from madousho.config.loader import ConfigManager


@pytest.fixture(scope="function", autouse=True)
def init_config():
    """Initialize configuration manager before each test.
    
    This fixture runs automatically before every test to ensure
    ConfigManager is initialized with the project config directory.
    """
    ConfigManager.reset_instance()
    config_dir = Path(__file__).parent.parent / "config"
    ConfigManager.get_instance(str(config_dir))
    yield
    ConfigManager.reset_instance()
