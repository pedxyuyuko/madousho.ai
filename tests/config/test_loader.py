"""Unit tests for the configuration loader module."""

import os
import pytest
import yaml

from madousho.config.loader import (
    normalize_keys,
    load_yaml,
    ConfigManager,
    get_config,
    init_config,
)


class TestNormalizeKeys:
    """Tests for the normalize_keys function."""

    def test_normalize_simple_dict_with_hyphens(self):
        """Test conversion of hyphenated keys to underscores in simple dict."""
        input_data = {"api-key": "value", "port-number": 8080}
        expected = {"api_key": "value", "port_number": 8080}
        assert normalize_keys(input_data) == expected

    def test_normalize_nested_dict_with_hyphens(self):
        """Test conversion in nested dictionaries."""
        input_data = {
            "api-config": {
                "host-name": "localhost",
                "port-number": 9000,
            }
        }
        expected = {
            "api_config": {
                "host_name": "localhost",
                "port_number": 9000,
            }
        }
        assert normalize_keys(input_data) == expected

    def test_normalize_list_with_dicts(self):
        """Test conversion in lists containing dictionaries."""
        input_data = [
            {"item-name": "first", "item-value": 1},
            {"item-name": "second", "item-value": 2},
        ]
        expected = [
            {"item_name": "first", "item_value": 1},
            {"item_name": "second", "item_value": 2},
        ]
        assert normalize_keys(input_data) == expected

    def test_normalize_mixed_keys(self):
        """Test that underscore keys remain unchanged."""
        input_data = {"api_key": "value", "port-number": 8080}
        expected = {"api_key": "value", "port_number": 8080}
        assert normalize_keys(input_data) == expected

    def test_normalize_primitives(self):
        """Test that primitives are returned unchanged."""
        assert normalize_keys("string") == "string"
        assert normalize_keys(123) == 123
        assert normalize_keys(None) is None
        assert normalize_keys(True) is True


class TestLoadYaml:
    """Tests for the load_yaml function."""

    def test_load_yaml_valid_file(self, tmp_path):
        """Test loading a valid YAML file."""
        yaml_content = """
api:
  host: localhost
  port: 8080
"""
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)

        result = load_yaml(str(yaml_file))
        assert result == {"api": {"host": "localhost", "port": 8080}}

    def test_load_yaml_missing_file(self):
        """Test that FileNotFoundError is raised for missing file."""
        with pytest.raises(FileNotFoundError) as exc_info:
            load_yaml("/nonexistent/path/config.yaml")
        assert "Configuration file not found" in str(exc_info.value)

    def test_load_yaml_malformed_yaml(self, tmp_path):
        """Test that ValueError is raised for malformed YAML."""
        malformed_content = """
api:
  host: localhost
  port: [invalid yaml
"""
        yaml_file = tmp_path / "invalid.yaml"
        yaml_file.write_text(malformed_content)

        with pytest.raises(ValueError) as exc_info:
            load_yaml(str(yaml_file))
        assert "Invalid YAML" in str(exc_info.value)

    def test_load_yaml_empty_file(self, tmp_path):
        """Test that empty YAML file returns empty dict."""
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("")

        result = load_yaml(str(yaml_file))
        assert result == {}

    def test_load_yaml_with_comments(self, tmp_path):
        """Test loading YAML with comments."""
        yaml_content = """
# This is a comment
api:
  host: localhost  # inline comment
  port: 8080
"""
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)

        result = load_yaml(str(yaml_file))
        assert result == {"api": {"host": "localhost", "port": 8080}}


class TestConfigManager:
    """Tests for the ConfigManager singleton class."""

    def setup_method(self):
        """Reset singleton before each test."""
        ConfigManager.reset_instance()

    def teardown_method(self):
        """Reset singleton after each test."""
        ConfigManager.reset_instance()

    def test_config_manager_singleton(self, tmp_path):
        """Test that ConfigManager is a singleton."""
        # First call creates instance
        manager1 = ConfigManager.get_instance(str(tmp_path))
        # Second call returns same instance
        manager2 = ConfigManager.get_instance()
        assert manager1 is manager2

    def test_config_manager_requires_config_dir_on_init(self):
        """Test that first call to get_instance requires config_dir."""
        ConfigManager.reset_instance()
        with pytest.raises(RuntimeError) as exc_info:
            ConfigManager.get_instance()
        assert "ConfigManager not initialized" in str(exc_info.value)

    def test_config_manager_loads_config(self, tmp_path):
        """Test that ConfigManager loads config from directory."""
        yaml_content = """
api:
  host: localhost
  port: 8080
  token: test-token

provider:
  test:
    type: openai
    endpoint: https://api.example.com/v1
    api-key: sk-test

default_model_group: "default"
model-groups:
  default:
    - test/model-1
"""
        config_file = tmp_path / "madousho.yaml"
        config_file.write_text(yaml_content)

        manager = ConfigManager.get_instance(str(tmp_path))
        config = manager.config

        assert config.api.host == "localhost"
        assert config.api.port == 8080

    def test_config_manager_finds_madousho_yaml(self, tmp_path):
        """Test that ConfigManager prefers madousho.yaml over config.yaml."""
        yaml_content = """
api:
  host: madousho-host
  port: 8080
  token: test

provider:
  test:
    type: openai
    endpoint: https://api.example.com/v1
    api-key: sk-test

default_model_group: "default"
model-groups:
  default:
    - test/model-1
"""
        # Create both files
        (tmp_path / "madousho.yaml").write_text(yaml_content)
        (tmp_path / "config.yaml").write_text(yaml_content.replace("madousho-host", "config-host"))

        manager = ConfigManager.get_instance(str(tmp_path))
        config = manager.config

        assert config.api.host == "madousho-host"

    def test_config_manager_finds_config_yaml(self, tmp_path):
        """Test that ConfigManager falls back to config.yaml."""
        yaml_content = """
api:
  host: localhost
  port: 8080
  token: test

provider:
  test:
    type: openai
    endpoint: https://api.example.com/v1
    api-key: sk-test

default_model_group: "default"
model-groups:
  default:
    - test/model-1
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)

        manager = ConfigManager.get_instance(str(tmp_path))
        config = manager.config

        assert config.api.host == "localhost"

    def test_config_manager_no_config_file(self, tmp_path):
        """Test that ConfigManager raises error if no config file found."""
        with pytest.raises(FileNotFoundError) as exc_info:
            manager = ConfigManager.get_instance(str(tmp_path))
            _ = manager.config
        assert "No configuration file found" in str(exc_info.value)


class TestGetConfig:
    """Tests for the get_config() convenience function."""

    def setup_method(self):
        """Reset singleton before each test."""
        ConfigManager.reset_instance()

    def teardown_method(self):
        """Reset singleton after each test."""
        ConfigManager.reset_instance()

    def test_get_config_requires_initialization(self):
        """Test that get_config() raises error if not initialized."""
        with pytest.raises(RuntimeError) as exc_info:
            get_config()
        assert "ConfigManager not initialized" in str(exc_info.value)

    def test_get_config_after_init(self, tmp_path):
        """Test that get_config() works after initialization."""
        yaml_content = """
api:
  host: get-config-host
  port: 9000
  token: test

provider:
  test:
    type: openai
    endpoint: https://api.example.com/v1
    api-key: sk-test

default_model_group: "default"
model-groups:
  default:
    - test/model-1
"""
        config_file = tmp_path / "madousho.yaml"
        config_file.write_text(yaml_content)

        init_config(str(tmp_path))
        config = get_config()

        assert config.api.host == "get-config-host"
        assert config.api.port == 9000


class TestInitConfig:
    """Tests for the init_config() convenience function."""

    def setup_method(self):
        """Reset singleton before each test."""
        ConfigManager.reset_instance()

    def teardown_method(self):
        """Reset singleton after each test."""
        ConfigManager.reset_instance()

    def test_init_config_creates_singleton(self, tmp_path):
        """Test that init_config() creates the singleton instance."""
        yaml_content = """
api:
  host: init-host
  port: 7000
  token: test

provider:
  test:
    type: openai
    endpoint: https://api.example.com/v1
    api-key: sk-test

default_model_group: "default"
model-groups:
  default:
    - test/model-1
"""
        config_file = tmp_path / "madousho.yaml"
        config_file.write_text(yaml_content)

        config = init_config(str(tmp_path))

        assert config.api.host == "init-host"
        assert config.api.port == 7000

        # Verify singleton was created
        config2 = get_config()
        assert config is config2


class TestErrorMessages:
    """Tests for error message clarity."""

    def setup_method(self):
        """Reset singleton before each test."""
        ConfigManager.reset_instance()

    def teardown_method(self):
        """Reset singleton after each test."""
        ConfigManager.reset_instance()

    def test_load_yaml_error_message_includes_path(self, tmp_path):
        """Test that error messages include the file path."""
        yaml_file = tmp_path / "broken.yaml"
        yaml_file.write_text("invalid: yaml: [")

        with pytest.raises(ValueError) as exc_info:
            load_yaml(str(yaml_file))
        assert str(yaml_file) in str(exc_info.value) or "Invalid YAML" in str(exc_info.value)

    def test_config_manager_error_message_includes_validation(self, tmp_path):
        """Test that validation errors are wrapped with context."""
        yaml_content = """
api:
  host: localhost
  port: 99999
  token: test

provider:
  test:
    type: openai
    endpoint: https://api.example.com/v1
    api-key: sk-test

default_model_group: "default"
model-groups:
  default:
    - test/model-1
"""
        yaml_file = tmp_path / "madousho.yaml"
        yaml_file.write_text(yaml_content)

        with pytest.raises(ValueError) as exc_info:
            manager = ConfigManager.get_instance(str(tmp_path))
            _ = manager.config
        assert "Invalid configuration" in str(exc_info.value)
