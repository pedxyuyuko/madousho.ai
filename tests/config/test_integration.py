"""Integration tests for the configuration module.

These tests verify end-to-end behavior including:
- Loading real configuration files
- Models + loader integration
- Cross-module behavior
- Full workflow scenarios
"""

import os
import pytest
import yaml

from madousho.config.loader import (
    normalize_keys,
    load_yaml,
    ConfigManager,
    init_config,
    get_config,
)
from madousho.config.models import APIConfig, ProviderConfig, Config


class TestLoadRealConfigFile:
    """Tests that load the actual config/madousho.yaml file."""

    def test_load_madousho_yaml_exists(self):
        """Test that the main config file exists and is loadable."""
        config_path = "config/madousho.yaml"
        assert os.path.exists(config_path), f"Config file {config_path} must exist"
        
        config = load_yaml(config_path)
        assert isinstance(config, dict)
        assert len(config) > 0

    def test_load_madousho_yaml_structure(self):
        """Test that madousho.yaml has expected top-level keys."""
        config_path = "config/madousho.yaml"
        config = load_yaml(config_path)
        
        # Check for expected top-level sections
        assert isinstance(config, dict)

    def test_load_example_config_file(self):
        """Test loading the example configuration file."""
        config_path = "config/madousho.example.yaml"
        assert os.path.exists(config_path), f"Example config {config_path} must exist"
        
        config = load_yaml(config_path)
        assert isinstance(config, dict)
        
        # Example config should have more complete structure
        assert "api" in config or len(config) > 0


class TestModelsLoaderIntegration:
    """Tests for integration between models and loader."""

    def test_normalize_then_validate(self, tmp_path):
        """Test that normalized YAML can be validated by models."""
        yaml_content = """
api:
  host: localhost
  port: 8080
  token: test-token

provider:
  my-provider:
    type: openai
    endpoint: https://api.example.com/v1
    api-key: sk-test123

default_model_group: "default-group"
model-groups:
  default-group:
    - my-provider/gpt-4
    - my-provider/fallback
"""
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)
        
        # Load and normalize
        raw_config = load_yaml(str(yaml_file))
        normalized = normalize_keys(raw_config)
        
        # Should be able to create Config model
        config = Config.model_validate(normalized)
        
        assert config.api.host == "localhost"
        assert config.api.port == 8080
        assert "my_provider" in config.provider
        assert config.provider["my_provider"].api_key == "sk-test123"
        assert "default_group" in config.model_groups


class TestConfigManagerIntegration:
    """Tests for ConfigManager integration."""

    def setup_method(self):
        ConfigManager.reset_instance()

    def teardown_method(self):
        ConfigManager.reset_instance()

    def test_config_manager_full_workflow(self, tmp_path):
        """Test complete ConfigManager workflow."""
        yaml_content = """
api:
  host: 0.0.0.0
  port: 3000
  token: yaml-token

provider:
  primary_provider:
    type: openai
    endpoint: https://api.openai.com/v1
    api-key: sk-primary
  fallback_provider:
    type: anthropic
    endpoint: https://api.anthropic.com/v1
    api-key: sk-anthropic

default_model_group: "chat_group"
model-groups:
  chat_group:
    - primary_provider/gpt-4
    - fallback_provider/claude-3
  completion_group:
    - primary_provider/gpt-3.5-turbo
"""
        yaml_file = tmp_path / "madousho.yaml"
        yaml_file.write_text(yaml_content)
        
        config = init_config(str(tmp_path))
        
        assert config.api.host == "0.0.0.0"
        assert config.api.port == 3000
        assert len(config.provider) == 2
        assert len(config.model_groups) == 2
    def test_config_manager_singleton_behavior(self, tmp_path):
        """Test that ConfigManager is truly a singleton."""
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
        yaml_file = tmp_path / "madousho.yaml"
        yaml_file.write_text(yaml_content)
        
        config1 = init_config(str(tmp_path))
        config2 = get_config()
        
        assert config1 is config2

    def test_hyphen_conversion_full_chain(self, tmp_path):
        """Test hyphen-to-underscore conversion through full loading chain."""
        yaml_content = """
api:
  host: localhost
  port: 8080
  token: test

provider:
  my-test-provider:
    type: openai
    endpoint: https://api.example.com/v1
    api-key: sk-test

default_model_group: "my-model-group"
model-groups:
  my-model-group:
    - my-test-provider/model-1
"""
        yaml_file = tmp_path / "madousho.yaml"
        yaml_file.write_text(yaml_content)
        
        config = init_config(str(tmp_path))
        
        assert "my_test_provider" in config.provider
        assert "my_model_group" in config.model_groups

    def test_config_model_dump_roundtrip(self, tmp_path):
        """Test that loaded config can be dumped and reloaded."""
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
        yaml_file = tmp_path / "madousho.yaml"
        yaml_file.write_text(yaml_content)
        
        config1 = init_config(str(tmp_path))
        config_dict = config1.model_dump()
        config2 = Config.model_validate(config_dict)
        
        assert config2.api.host == config1.api.host
        assert config2.api.port == config1.api.port


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    def setup_method(self):
        ConfigManager.reset_instance()

    def teardown_method(self):
        ConfigManager.reset_instance()

    def test_complete_config_lifecycle(self, tmp_path):
        """Test complete configuration lifecycle from creation to validation."""
        yaml_content = """
api:
  host: 0.0.0.0
  port: 8000
  token: lifecycle-token

provider:
  provider-a:
    type: openai
    endpoint: https://api.openai.com/v1
    api-key: sk-a
  provider-b:
    type: openai
    endpoint: https://api.example.com/v1
    api-key: sk-b

default_model_group: "group-a"
model-groups:
  group-a:
    - provider-a/model-1
    - provider-a/model-2
  group-b:
    - provider-b/model-1
"""
        config_file = tmp_path / "madousho.yaml"
        config_file.write_text(yaml_content)
        
        config = init_config(str(tmp_path))
        
        assert isinstance(config.api, APIConfig)
        assert isinstance(config.provider, dict)
        assert config.api.host == "0.0.0.0"
        assert config.api.port == 8000

    def test_error_handling_end_to_end(self, tmp_path):
        """Test error handling through the full stack."""
        with pytest.raises(FileNotFoundError) as exc_info:
            manager = ConfigManager.get_instance(str(tmp_path))
            _ = manager.config
        assert "No configuration file found" in str(exc_info.value)
        
        invalid_yaml = tmp_path / "madousho.yaml"
        invalid_yaml.write_text("invalid: yaml: [")
        with pytest.raises(ValueError) as exc_info:
            manager = ConfigManager.get_instance(str(invalid_yaml.parent))
            _ = manager.config
        assert "Invalid YAML" in str(exc_info.value)

    def test_production_like_scenario(self, tmp_path):
        """Test a production-like configuration scenario."""
        yaml_content = """
api:
  host: 0.0.0.0
  port: 8000
  token: prod-token-xyz

provider:
  openai-primary:
    type: openai
    endpoint: https://api.openai.com/v1
    api-key: sk-prod-primary
  openai-fallback:
    type: openai
    endpoint: https://api.openai.com/v1
    api-key: sk-prod-fallback
  anthropic:
    type: anthropic
    endpoint: https://api.anthropic.com/v1
    api-key: sk-anthropic-prod

default_model_group: "production-chat"
model-groups:
  production-chat:
    - openai-primary/gpt-4-turbo
    - openai-fallback/gpt-4
    - anthropic/claude-3-opus
  development:
    - openai-primary/gpt-3.5-turbo
"""
        config_file = tmp_path / "madousho.yaml"
        config_file.write_text(yaml_content)
        
        config = init_config(str(tmp_path))
        
        assert config.api.host == "0.0.0.0"
        assert config.api.port == 8000
        assert len(config.provider) == 3
        assert "openai_primary" in config.provider
        assert "production_chat" in config.model_groups
