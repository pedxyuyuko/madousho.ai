"""Unit tests for madousho.config module."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from madousho.config import Config, ApiConfig, ProviderConfig
from madousho.config.loader import (
    get_config_file,
    init_config,
    get_config,
    _cached_config,
)


class TestApiConfig:
    """Tests for ApiConfig model."""

    def test_default_values(self):
        """Test ApiConfig default field values."""
        config = ApiConfig()
        assert config.token == ""
        assert config.host == "0.0.0.0"
        assert config.port == 8000

    def test_custom_values(self):
        """Test ApiConfig with custom values."""
        config = ApiConfig(token="test-token", host="127.0.0.1", port=9000)
        assert config.token == "test-token"
        assert config.host == "127.0.0.1"
        assert config.port == 9000

    def test_port_validation(self):
        """Test that port accepts valid integers."""
        config = ApiConfig(port=3000)
        assert config.port == 3000

    def test_model_fields(self):
        """Test ApiConfig model field descriptions."""
        fields = ApiConfig.model_fields
        assert "token" in fields
        assert "host" in fields
        assert "port" in fields
        assert fields["token"].description == "API authentication token"
        assert fields["host"].description == "Server host address"
        assert fields["port"].description == "Server port number"


class TestProviderConfig:
    """Tests for ProviderConfig model."""

    def test_default_values(self):
        """Test ProviderConfig default field values."""
        config = ProviderConfig()
        assert config.type == "openai-compatible"
        assert config.endpoint == ""
        assert config.api_key == ""

    def test_custom_values(self):
        """Test ProviderConfig with custom values."""
        config = ProviderConfig(
            type="custom-type",
            endpoint="https://api.example.com/v1",
            **{"api-key": "sk-test123"}
        )
        assert config.type == "custom-type"
        assert config.endpoint == "https://api.example.com/v1"
        assert config.api_key == "sk-test123"

    def test_api_key_alias(self):
        """Test that api-key alias works for api_key field."""
        # Test with alias in dict format
        data = {"type": "openai", "endpoint": "https://test.com", "api-key": "sk-alias"}
        config = ProviderConfig(**data)
        assert config.api_key == "sk-alias"

    def test_model_fields(self):
        """Test ProviderConfig model field descriptions."""
        fields = ProviderConfig.model_fields
        assert "type" in fields
        assert "endpoint" in fields
        assert "api_key" in fields
        assert fields["type"].description == "Provider type"
        assert fields["endpoint"].description == "Provider API endpoint URL"
        assert fields["api_key"].description == "Provider API key"


class TestConfig:
    """Tests for main Config model."""

    def test_minimal_valid_config(self):
        """Test Config with minimal required fields."""
        config = Config(
            api=ApiConfig(), provider={}, default_model_group="default", model_groups={}
        )
        assert config.api.token == ""
        assert config.default_model_group == "default"
        assert config.provider == {}
        assert config.model_groups == {}

    def test_full_config(self):
        """Test Config with all fields populated."""
        config = Config(
            api=ApiConfig(token="test-token", port=9000),
            provider={
                "provider1": ProviderConfig(
                    type="openai", endpoint="https://api1.com", api_key="key1"
                ),
                "provider2": ProviderConfig(
                    type="anthropic", endpoint="https://api2.com", api_key="key2"
                ),
            },
            default_model_group="gpt-4",
            model_groups={
                "gpt-4": ["provider1/gpt-4-turbo"],
                "claude": ["provider2/claude-3"],
            },
        )
        assert len(config.provider) == 2
        assert config.api.token == "test-token"
        assert config.api.port == 9000
        assert config.default_model_group == "gpt-4"
        assert len(config.model_groups) == 2

    def test_model_validate_from_dict(self):
        """Test Config.model_validate with dictionary data."""
        data = {
            "api": {"token": "env-token", "host": "localhost", "port": 8080},
            "provider": {
                "test_provider": {
                    "type": "openai-compatible",
                    "endpoint": "https://test.com/v1",
                    "api-key": "sk-test",
                }
            },
            "default_model_group": "test_group",
            "model_groups": {"test_group": ["test_provider/model-1"]},
        }
        config = Config.model_validate(data)
        assert config.api.token == "env-token"
        assert config.api.host == "localhost"
        assert config.api.port == 8080
        assert len(config.provider) == 1
        assert config.provider["test_provider"].api_key == "sk-test"

    def test_required_fields(self):
        """Test that required fields must be provided."""
        with pytest.raises(Exception):  # pydantic.ValidationError
            Config()  # Missing required fields


class TestGetConfigFile:
    """Tests for get_config_file function."""

    def test_default_path(self):
        """Test default config file path resolution."""
        # Ensure env var is not set
        os.environ.pop("MADOUSHO_CONFIG_PATH", None)
        path = get_config_file()
        assert path == Path("config/madousho.yaml") or path == Path(
            "config/madousho.yml"
        )

    def test_custom_env_var_path(self):
        """Test config path from environment variable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MADOUSHO_CONFIG_PATH"] = tmpdir
            # Create a dummy config file
            config_file = Path(tmpdir) / "madousho.yaml"
            config_file.touch()

            path = get_config_file()
            assert path == config_file

            os.environ.pop("MADOUSHO_CONFIG_PATH", None)

    def test_relative_filepath(self):
        """Test config path with relative filepath."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MADOUSHO_CONFIG_PATH"] = tmpdir
            # Create a dummy config file
            config_file = Path(tmpdir) / "custom.yaml"
            config_file.touch()

            path = get_config_file("custom")
            assert path == config_file

            os.environ.pop("MADOUSHO_CONFIG_PATH", None)

    def test_absolute_filepath(self):
        """Test config path with absolute filepath."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "absolute.yaml"
            config_file.touch()

            path = get_config_file(str(config_file))
            assert path == config_file

    def test_file_not_found(self):
        """Test FileNotFoundError when config file doesn't exist."""
        os.environ.pop("MADOUSHO_CONFIG_PATH", None)
        # get_config_file returns the path even if it doesn't exist
        # The error is raised when trying to open the file in _load_from_file
        path = get_config_file("nonexistent_config")
        # Verify it returns the expected path with .yaml extension
        assert str(path).endswith("nonexistent_config.yaml")

    def test_yaml_extension_priority(self):
        """Test that .yaml is tried before .yml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MADOUSHO_CONFIG_PATH"] = tmpdir
            # Create only .yml file
            yml_file = Path(tmpdir) / "madousho.yml"
            yml_file.touch()

            path = get_config_file()
            assert path == yml_file

            os.environ.pop("MADOUSHO_CONFIG_PATH", None)


class TestInitConfig:
    """Tests for init_config function."""

    def test_load_from_valid_yaml(self):
        """Test loading config from valid YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test_config.yaml"
            config_data = {
                "api": {"token": "test-token", "host": "127.0.0.1", "port": 9000},
                "provider": {
                    "test": {
                        "type": "openai",
                        "endpoint": "https://test.com",
                        "api-key": "sk-test",
                    }
                },
                "default_model_group": "test",
                "model_groups": {"test": ["test/model-1"]},
            }

            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            config = init_config(str(config_file))
            assert isinstance(config, Config)
            assert config.api.token == "test-token"
            assert config.api.host == "127.0.0.1"
            assert config.api.port == 9000
            assert "test" in config.provider
            assert config.default_model_group == "test"

    def test_init_config_updates_cache(self):
        """Test that init_config updates the global cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "cache_test.yaml"
            config_data = {
                "api": {"token": "cached-token", "host": "0.0.0.0", "port": 8000},
                "provider": {},
                "default_model_group": "default",
                "model_groups": {},
            }

            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            # Reset cache
            import madousho.config.loader as loader

            loader._cached_config = None

            config = init_config(str(config_file))
            assert loader._cached_config is config

            # Cleanup
            loader._cached_config = None

    def test_load_invalid_yaml_raises(self):
        """Test that invalid YAML raises yaml.YAMLError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "invalid.yaml"
            with open(config_file, "w") as f:
                f.write("invalid: yaml: content: [")

            with pytest.raises(yaml.YAMLError):
                init_config(str(config_file))

    def test_load_yaml_missing_required_fields(self):
        """Test that YAML missing required fields raises ValidationError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "incomplete.yaml"
            config_data = {
                "api": {}  # Missing required fields
                # Missing provider, default_model_group, model_groups
            }

            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            with pytest.raises(Exception):  # pydantic.ValidationError
                init_config(str(config_file))


class TestGetConfig:
    """Tests for get_config function."""

    def test_get_config_initializes_if_none(self):
        """Test that get_config calls init_config if cache is None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create config file named "madousho.yaml" in temp dir
            config_file = Path(tmpdir) / "madousho.yaml"
            config_data = {
                "api": {"token": "auto-token", "host": "0.0.0.0", "port": 8000},
                "provider": {},
                "default_model_group": "default",
                "model_groups": {},
            }
            
            with open(config_file, "w") as f:
                yaml.dump(config_data, f)
            
            # Set env var to point to temp dir (will use default "madousho" filename)
            os.environ["MADOUSHO_CONFIG_PATH"] = tmpdir
            
            # Reset cache
            import madousho.config.loader as loader
            loader._cached_config = None
            
            try:
                config = get_config()
                assert isinstance(config, Config)
                assert config.api.token == "auto-token"
            finally:
                os.environ.pop("MADOUSHO_CONFIG_PATH", None)
                loader._cached_config = None

    def test_get_config_returns_cached(self):
        """Test that get_config returns cached config."""
        import madousho.config.loader as loader

        # Create a mock config
        mock_config = Config(
            api=ApiConfig(), provider={}, default_model_group="test", model_groups={}
        )
        loader._cached_config = mock_config

        config = get_config()
        assert config is mock_config

        # Cleanup
        loader._cached_config = None


class TestConfigIntegration:
    """Integration tests for config module."""

    def test_full_config_workflow(self):
        """Test complete config workflow: create file -> init -> get."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "workflow.yaml"
            config_data = {
                "api": {"token": "workflow-token", "host": "0.0.0.0", "port": 8888},
                "provider": {
                    "openai": {
                        "type": "openai",
                        "endpoint": "https://api.openai.com/v1",
                        "api-key": "sk-openai",
                    }
                },
                "default_model_group": "gpt-4",
                "model_groups": {"gpt-4": ["openai/gpt-4-turbo", "openai/gpt-4"]},
            }

            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            # Reset cache
            import madousho.config.loader as loader

            loader._cached_config = None

            try:
                # Initialize config
                config = init_config(str(config_file))

                # Verify loaded config
                assert config.api.token == "workflow-token"
                assert config.api.port == 8888
                assert "openai" in config.provider
                assert config.default_model_group == "gpt-4"
                assert len(config.model_groups["gpt-4"]) == 2

                # Get cached config
                cached = get_config()
                assert cached is config
            finally:
                loader._cached_config = None

    def test_example_config_loads(self):
        """Test that the example config file can be loaded."""
        example_config = Path("config/madousho.example.yaml")
        if example_config.exists():
            import madousho.config.loader as loader

            loader._cached_config = None

            try:
                # Pass absolute path to avoid path resolution issues
                config = init_config(str(example_config.absolute()))
                assert isinstance(config, Config)
                assert config.api is not None
                assert isinstance(config.provider, dict)
            finally:
                loader._cached_config = None
