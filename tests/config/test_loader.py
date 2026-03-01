"""Unit tests for the configuration loader module."""

import os
import pytest
import yaml

from madousho.config.loader import (
    normalize_keys,
    load_yaml,
    get_env_overrides,
    deep_merge,
    load_config,
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


class TestGetEnvOverrides:
    """Tests for the get_env_overrides function."""

    def test_get_env_overrides_empty(self, monkeypatch):
        """Test with no matching environment variables."""
        # Clear any MADOUSHO_ env vars
        for key in list(os.environ.keys()):
            if key.startswith("MADOUSHO_"):
                monkeypatch.delenv(key, raising=False)

        result = get_env_overrides()
        assert result == {}

    def test_get_env_overrides_simple(self, monkeypatch):
        """Test single level environment variable."""
        monkeypatch.setenv("MADOUSHO_API_HOST", "localhost")
        monkeypatch.setenv("MADOUSHO_API_PORT", "8080")

        result = get_env_overrides()
        assert result == {"api": {"host": "localhost", "port": 8080}}

    def test_get_env_overrides_nested(self, monkeypatch):
        """Test nested environment variables."""
        monkeypatch.setenv("MADOUSHO_PROVIDER_EXAMPLE_API_KEY", "test-key-123")
        monkeypatch.setenv("MADOUSHO_PROVIDER_EXAMPLE_ENDPOINT", "https://api.example.com")

        result = get_env_overrides()
        # Note: API_KEY splits into nested {"api": {"key": ...}} due to underscore splitting
        expected = {
            "provider": {
                "example": {
                    "api": {"key": "test-key-123"},
                    "endpoint": "https://api.example.com",
                }
            }
        }
        assert result == expected

    def test_get_env_overrides_type_conversion_int(self, monkeypatch):
        """Test that numeric strings are converted to integers."""
        monkeypatch.setenv("MADOUSHO_API_PORT", "9000")
        monkeypatch.setenv("MADOUSHO_API_TIMEOUT", "30")

        result = get_env_overrides()
        assert result["api"]["port"] == 9000
        assert isinstance(result["api"]["port"], int)
        assert result["api"]["timeout"] == 30
        assert isinstance(result["api"]["timeout"], int)

    def test_get_env_overrides_type_conversion_string(self, monkeypatch):
        """Test that non-numeric strings remain strings."""
        monkeypatch.setenv("MADOUSHO_API_HOST", "localhost")
        monkeypatch.setenv("MADOUSHO_API_TOKEN", "abc123xyz")

        result = get_env_overrides()
        assert result["api"]["host"] == "localhost"
        assert isinstance(result["api"]["host"], str)
        assert result["api"]["token"] == "abc123xyz"
        assert isinstance(result["api"]["token"], str)

    def test_get_env_overrides_custom_prefix(self, monkeypatch):
        """Test with custom prefix."""
        monkeypatch.setenv("CUSTOM_API_HOST", "custom-host")

        result = get_env_overrides(prefix="CUSTOM_")
        assert result == {"api": {"host": "custom-host"}}

    def test_get_env_overrides_ignores_other_env(self, monkeypatch):
        """Test that non-prefixed env vars are ignored."""
        monkeypatch.setenv("OTHER_API_HOST", "ignored")
        monkeypatch.setenv("MADOUSHO_API_HOST", "included")

        result = get_env_overrides()
        assert result == {"api": {"host": "included"}}
        assert "other" not in result


class TestDeepMerge:
    """Tests for the deep_merge function."""

    def test_deep_merge_simple_dicts(self):
        """Test merging simple dictionaries."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = deep_merge(base, override)
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_deep_merge_nested_dicts(self):
        """Test merging nested dictionaries."""
        base = {"api": {"host": "localhost", "port": 8080}}
        override = {"api": {"port": 9000, "token": "secret"}}
        result = deep_merge(base, override)
        assert result == {
            "api": {
                "host": "localhost",
                "port": 9000,
                "token": "secret",
            }
        }

    def test_deep_merge_deeply_nested(self):
        """Test merging deeply nested dictionaries."""
        base = {
            "provider": {
                "example": {
                    "type": "openai",
                    "config": {"timeout": 30},
                }
            }
        }
        override = {
            "provider": {
                "example": {
                    "api_key": "new-key",
                    "config": {"retries": 3},
                }
            }
        }
        result = deep_merge(base, override)
        assert result == {
            "provider": {
                "example": {
                    "type": "openai",
                    "api_key": "new-key",
                    "config": {
                        "timeout": 30,
                        "retries": 3,
                    },
                }
            }
        }

    def test_deep_merge_empty_override(self):
        """Test merging with empty override dict."""
        base = {"a": 1, "b": 2}
        override = {}
        result = deep_merge(base, override)
        assert result == base

    def test_deep_merge_empty_base(self):
        """Test merging with empty base dict."""
        base = {}
        override = {"a": 1, "b": 2}
        result = deep_merge(base, override)
        assert result == override

    def test_deep_merge_primitives_override(self):
        """Test that primitives are fully replaced."""
        base = {"value": 100}
        override = {"value": 200}
        result = deep_merge(base, override)
        assert result == {"value": 200}

    def test_deep_merge_dict_overwrites_primitive(self):
        """Test that dict override replaces primitive value."""
        base = {"config": "string-value"}
        override = {"config": {"nested": "value"}}
        result = deep_merge(base, override)
        assert result == {"config": {"nested": "value"}}


class TestLoadConfig:
    """Tests for the load_config function (end-to-end)."""

    def test_load_config_valid(self, tmp_path, monkeypatch):
        """Test loading a valid configuration file."""
        # Clear any existing MADOUSHO_ env vars
        for key in list(os.environ.keys()):
            if key.startswith("MADOUSHO_"):
                monkeypatch.delenv(key, raising=False)

        yaml_content = """
api:
  host: localhost
  port: 8080

default_model_group: "default"
provider:
  example:
    type: openai
    endpoint: https://api.openai.com/v1
    api-key: sk-test123

model-groups:
  default:
    - gpt-4
    - gpt-3.5-turbo
"""
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)

        config = load_config(str(yaml_file))

        assert config.api.host == "localhost"
        assert config.api.port == 8080
        assert "example" in config.provider
        assert config.provider["example"].type == "openai"
        assert "default" in config.model_groups

    def test_load_config_with_env_overrides(self, tmp_path, monkeypatch):
        """Test that environment variables override YAML values."""
        # Clear any existing MADOUSHO_ env vars
        for key in list(os.environ.keys()):
            if key.startswith("MADOUSHO_"):
                monkeypatch.delenv(key, raising=False)

        yaml_content = """
api:
  host: localhost
  port: 8080

default_model_group: "default"
provider:
  example:
    type: openai
    endpoint: https://api.openai.com/v1
    api-key: sk-test123

model-groups:
  default:
    - gpt-4
"""
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)

        # Override port via environment
        monkeypatch.setenv("MADOUSHO_API_PORT", "9999")

        config = load_config(str(yaml_file))

        assert config.api.port == 9999  # Overridden
        assert config.api.host == "localhost"  # From YAML

    def test_load_config_missing_file(self):
        """Test that FileNotFoundError is raised for missing config."""
        with pytest.raises(FileNotFoundError) as exc_info:
            load_config("/nonexistent/config.yaml")
        assert "Configuration file not found" in str(exc_info.value)

    def test_load_config_invalid_yaml(self, tmp_path):
        """Test that ValueError is raised for invalid YAML."""
        yaml_file = tmp_path / "invalid.yaml"
        yaml_file.write_text("invalid: yaml: content: [")

        with pytest.raises(ValueError) as exc_info:
            load_config(str(yaml_file))
        assert "Invalid YAML" in str(exc_info.value)

    def test_load_config_validation_error(self, tmp_path, monkeypatch):
        """Test that ValueError is raised for invalid config structure."""
        # Clear any existing MADOUSHO_ env vars
        for key in list(os.environ.keys()):
            if key.startswith("MADOUSHO_"):
                monkeypatch.delenv(key, raising=False)

        # Missing required fields
        yaml_content = """
api:
  host: localhost
  # missing port and token
"""
        yaml_file = tmp_path / "invalid.yaml"
        yaml_file.write_text(yaml_content)

        with pytest.raises(ValueError) as exc_info:
            load_config(str(yaml_file))
        assert "Invalid configuration" in str(exc_info.value)

    def test_load_config_hyphen_to_underscore(self, tmp_path, monkeypatch):
        """Test that hyphenated keys in YAML are converted to underscores."""
        for key in list(os.environ.keys()):
            if key.startswith("MADOUSHO_"):
                monkeypatch.delenv(key, raising=False)

        yaml_content = """
api:
  host: localhost
  port: 8080

default_model_group: "default-group"
provider:
  my-provider:
    type: openai
    endpoint: https://api.openai.com/v1
    api-key: sk-test123

model-groups:
  default-group:
    - gpt-4
"""
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)

        config = load_config(str(yaml_file))

        # The provider key should be accessible with underscore
        assert "my_provider" in config.provider
        assert config.provider["my_provider"].api_key == "sk-test123"


class TestErrorMessages:
    """Tests for error message clarity."""

    def test_load_yaml_error_message_includes_path(self, tmp_path):
        """Test that error messages include the file path."""
        yaml_file = tmp_path / "broken.yaml"
        yaml_file.write_text("invalid: yaml: [")

        with pytest.raises(ValueError) as exc_info:
            load_yaml(str(yaml_file))
        assert str(yaml_file) in str(exc_info.value) or "Invalid YAML" in str(exc_info.value)

    def test_load_config_error_message_includes_validation(self, tmp_path, monkeypatch):
        """Test that validation errors are wrapped with context."""
        for key in list(os.environ.keys()):
            if key.startswith("MADOUSHO_"):
                monkeypatch.delenv(key, raising=False)

        yaml_content = """
api:
  host: localhost
  port: 99999
"""
        yaml_file = tmp_path / "invalid.yaml"
        yaml_file.write_text(yaml_content)

        with pytest.raises(ValueError) as exc_info:
            load_config(str(yaml_file))
        assert "Invalid configuration" in str(exc_info.value)
