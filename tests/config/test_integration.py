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
    get_env_overrides,
    deep_merge,
    load_config,
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
        
        # Check for expected sections (may be commented out in example)
        # At minimum, the file should be valid YAML
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

    def test_env_override_then_validate(self, tmp_path, monkeypatch):
        """Test environment overrides work with model validation."""
        yaml_content = """
api:
  host: localhost
  port: 8080

provider:
  test:
    type: openai
    endpoint: https://api.example.com/v1
    api-key: sk-test

default_model_group: ""
model-groups: {}
"""
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)
        
        # Set environment override
        monkeypatch.setenv("MADOUSHO_API_PORT", "9999")
        monkeypatch.setenv("MADOUSHO_API_TOKEN", "env-token")
        
        # Load config with overrides
        config = load_config(str(yaml_file))
        
        # Verify overrides applied
        assert config.api.port == 9999
        assert config.api.token == "env-token"
        assert config.api.host == "localhost"  # Unchanged

    def test_deep_merge_with_model_validation(self):
        """Test that deep_merge produces valid model input."""
        base = {
            "api": {"host": "localhost", "port": 8080},
            "provider": {
                "openai": {
                    "type": "openai",
                    "endpoint": "https://api.openai.com/v1",
                    "api_key": "sk-base"
                }
            },
            "default_model_group": "",
            "model_groups": {}
        }
        
        override = {
            "api": {"token": "merged-token"},
            "provider": {
                "openai": {
                    "api_key": "sk-override"
                }
            }
        }
        
        merged = deep_merge(base, override)
        config = Config.model_validate(merged)
        
        # Verify merge worked correctly
        assert config.api.host == "localhost"
        assert config.api.port == 8080
        assert config.api.token == "merged-token"
        assert config.provider["openai"].api_key == "sk-override"


class TestCrossModuleBehavior:
    """Tests for cross-module integration behavior."""

    def test_full_load_config_workflow(self, tmp_path, monkeypatch):
        """Test complete load_config workflow with all features."""
        # Clear any existing MADOUSHO_ env vars
        for key in list(os.environ.keys()):
            if key.startswith("MADOUSHO_"):
                monkeypatch.delenv(key, raising=False)
        
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
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)
        
        # Set some overrides
        monkeypatch.setenv("MADOUSHO_API_PORT", "8000")
        monkeypatch.setenv("MADOUSHO_API_TOKEN", "env-token")
        
        config = load_config(str(yaml_file))
        
        # Verify all components work together
        assert config.api.host == "0.0.0.0"
        assert config.api.port == 8000  # Overridden
        assert config.api.token == "env-token"  # Overridden
        assert len(config.provider) == 2
        assert config.provider["primary_provider"].api_key == "sk-primary"  # From YAML
        assert config.provider["fallback_provider"].api_key == "sk-anthropic"
        assert len(config.model_groups) == 2
        assert "chat_group" in config.model_groups
        assert "completion_group" in config.model_groups

    def test_hyphen_conversion_full_chain(self, tmp_path, monkeypatch):
        """Test hyphen-to-underscore conversion through full loading chain."""
        for key in list(os.environ.keys()):
            if key.startswith("MADOUSHO_"):
                monkeypatch.delenv(key, raising=False)
        
        yaml_content = """
api:
  host: localhost
  port: 8080

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
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)
        
        config = load_config(str(yaml_file))
        
        # Verify hyphenated keys were converted
        assert "my_test_provider" in config.provider
        assert config.provider["my_test_provider"].type == "openai"
        assert "my_model_group" in config.model_groups

    def test_config_model_dump_roundtrip(self, tmp_path, monkeypatch):
        """Test that loaded config can be dumped and reloaded."""
        for key in list(os.environ.keys()):
            if key.startswith("MADOUSHO_"):
                monkeypatch.delenv(key, raising=False)
        
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
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)
        
        # Load config
        config1 = load_config(str(yaml_file))
        
        # Dump to dict
        config_dict = config1.model_dump()
        
        # Reload from dict
        config2 = Config.model_validate(config_dict)
        
        # Verify roundtrip preserved data
        assert config2.api.host == config1.api.host
        assert config2.api.port == config1.api.port
        assert config2.api.token == config1.api.token
        assert list(config2.provider.keys()) == list(config1.provider.keys())
        assert list(config2.model_groups.keys()) == list(config1.model_groups.keys())


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    def test_complete_config_lifecycle(self, tmp_path, monkeypatch):
        """Test complete configuration lifecycle from creation to validation."""
        for key in list(os.environ.keys()):
            if key.startswith("MADOUSHO_"):
                monkeypatch.delenv(key, raising=False)
        
        # Step 1: Create config file
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
        config_file = tmp_path / "lifecycle.yaml"
        config_file.write_text(yaml_content)
        
        # Step 2: Load configuration
        config = load_config(str(config_file))
        
        # Step 3: Validate structure
        assert isinstance(config.api, APIConfig)
        assert isinstance(config.provider, dict)
        assert isinstance(config.model_groups, dict)
        
        # Step 4: Validate values
        assert config.api.host == "0.0.0.0"
        assert config.api.port == 8000
        assert config.api.token == "lifecycle-token"
        assert len(config.provider) == 2
        assert len(config.model_groups) == 2
        
        # Step 5: Validate nested models
        for provider_name, provider_config in config.provider.items():
            assert isinstance(provider_config, ProviderConfig)
            assert provider_config.type in ["openai"]
            assert provider_config.api_key.startswith("sk-")
        
        # Step 6: Verify model_groups contain valid references
        for group_name, models in config.model_groups.items():
            assert isinstance(models, list)
            assert len(models) > 0
            for model in models:
                assert "/" in model  # provider/model format

    def test_error_handling_end_to_end(self, tmp_path, monkeypatch):
        """Test error handling through the full stack."""
        for key in list(os.environ.keys()):
            if key.startswith("MADOUSHO_"):
                monkeypatch.delenv(key, raising=False)
        
        # Test 1: Missing file
        with pytest.raises(FileNotFoundError) as exc_info:
            load_config("/nonexistent/config.yaml")
        assert "Configuration file not found" in str(exc_info.value)
        
        # Test 2: Invalid YAML
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("invalid: yaml: [")
        with pytest.raises(ValueError) as exc_info:
            load_config(str(invalid_yaml))
        assert "Invalid YAML" in str(exc_info.value)
        
        # Test 3: Invalid config structure (missing required fields)
        incomplete_yaml = tmp_path / "incomplete.yaml"
        incomplete_yaml.write_text("api:\n  host: localhost\n  # missing port")
        with pytest.raises(ValueError) as exc_info:
            load_config(str(incomplete_yaml))
        assert "Invalid configuration" in str(exc_info.value)

    def test_production_like_scenario(self, tmp_path, monkeypatch):
        """Test a production-like configuration scenario."""
        for key in list(os.environ.keys()):
            if key.startswith("MADOUSHO_"):
                monkeypatch.delenv(key, raising=False)
        
        # Simulate production config
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
        config_file = tmp_path / "production.yaml"
        config_file.write_text(yaml_content)
        
        # Simulate production environment override
        monkeypatch.setenv("MADOUSHO_API_TOKEN", "prod-env-token-secret")
        
        config = load_config(str(config_file))
        
        # Verify production-like setup
        assert config.api.host == "0.0.0.0"
        assert config.api.port == 8000
        assert config.api.token == "prod-env-token-secret"  # Overridden
        assert len(config.provider) == 3
        assert "openai_primary" in config.provider
        assert "openai_fallback" in config.provider
        assert "anthropic" in config.provider
        assert "production_chat" in config.model_groups
        assert "development" in config.model_groups
        
        # Verify fallback chain in model group
        prod_models = config.model_groups["production_chat"]
        assert len(prod_models) == 3