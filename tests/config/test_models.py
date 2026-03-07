"""Unit tests for Pydantic configuration models."""

import pytest
from pydantic import ValidationError

from madousho.config.models import APIConfig, ProviderConfig, Config


class TestAPIConfig:
    """Tests for APIConfig model."""

    def test_valid_api_config_minimal(self):
        """Test valid APIConfig with required fields only."""
        config = APIConfig(host="localhost", port=8080, token="test-token")
        assert config.host == "localhost"
        assert config.port == 8080
        assert config.token == "test-token"

    def test_valid_api_config_with_token(self):
        """Test valid APIConfig with optional token field."""
        config = APIConfig(host="0.0.0.0", port=3000, token="test-token-123")
        assert config.host == "0.0.0.0"
        assert config.port == 3000
        assert config.token == "test-token-123"

    def test_valid_port_boundaries(self):
        """Test valid port values at boundaries."""
        # Minimum valid port
        config_min = APIConfig(host="localhost", port=1, token="token")
        assert config_min.port == 1

        # Maximum valid port
        config_max = APIConfig(host="localhost", port=65535, token="token")
        assert config_max.port == 65535

    def test_invalid_port_zero(self):
        """Test that port=0 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            APIConfig(host="localhost", port=0, token="token")
        assert "port must be between 1 and 65535" in str(exc_info.value)

    def test_invalid_port_negative(self):
        """Test that negative port is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            APIConfig(host="localhost", port=-1, token="token")
        assert "port must be between 1 and 65535" in str(exc_info.value)

    def test_invalid_port_too_large(self):
        """Test that port > 65535 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            APIConfig(host="localhost", port=65536, token="token")
        assert "port must be between 1 and 65535" in str(exc_info.value)

    def test_extra_fields_rejected(self):
        """Test that extra fields are rejected in APIConfig."""
        with pytest.raises(ValidationError) as exc_info:
            APIConfig(host="localhost", port=8080, token="token", timeout=30)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestProviderConfig:
    """Tests for ProviderConfig model."""

    def test_valid_provider_config(self):
        """Test valid ProviderConfig instantiation."""
        config = ProviderConfig(
            type="openai",
            endpoint="https://api.openai.com/v1",
            api_key="sk-test123"
        )
        assert config.type == "openai"
        assert config.endpoint == "https://api.openai.com/v1"
        assert config.api_key == "sk-test123"

    def test_provider_config_different_types(self):
        """Test ProviderConfig with different provider types."""
        providers = [
            ("anthropic", "https://api.anthropic.com"),
            ("ollama", "http://localhost:11434"),
            ("custom", "https://custom.api.example.com"),
        ]
        for provider_type, endpoint in providers:
            config = ProviderConfig(type=provider_type, endpoint=endpoint, api_key="key")
            assert config.type == provider_type
            assert config.endpoint == endpoint

    def test_provider_extra_fields_rejected(self):
        """Test that extra fields are rejected in ProviderConfig."""
        with pytest.raises(ValidationError) as exc_info:
            ProviderConfig(
                type="openai",
                endpoint="https://api.openai.com/v1",
                api_key="sk-test",
                timeout=30
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_provider_required_fields(self):
        """Test that all fields are required in ProviderConfig."""
        # Missing type
        with pytest.raises(ValidationError):
            ProviderConfig(endpoint="https://api.example.com", api_key="key")

        # Missing endpoint
        with pytest.raises(ValidationError):
            ProviderConfig(type="openai", api_key="key")

        # Missing api_key
        with pytest.raises(ValidationError):
            ProviderConfig(type="openai", endpoint="https://api.example.com")


class TestConfig:
    """Tests for main Config model with nested models."""

    def test_valid_config(self):
        """Test valid Config with nested APIConfig and ProviderConfig."""
        config = Config(
            api=APIConfig(host="localhost", port=8080, token="test-token"),
            provider={
                "openai": ProviderConfig(
                    type="openai",
                    endpoint="https://api.openai.com/v1",
                    api_key="sk-test"
                )
            },
            default_model_group="gpt-models",
            model_groups={
                "gpt-models": ["gpt-3.5-turbo", "gpt-4"]
            }
        )
        assert config.api.host == "localhost"
        assert config.api.port == 8080
        assert "openai" in config.provider
        assert config.provider["openai"].type == "openai"
        assert "gpt-models" in config.model_groups

    def test_config_multiple_providers(self):
        """Test Config with multiple providers."""
        config = Config(
            api=APIConfig(host="0.0.0.0", port=3000, token="test-token"),
            provider={
                "openai": ProviderConfig(
                    type="openai",
                    endpoint="https://api.openai.com/v1",
                    api_key="sk-openai"
                ),
                "anthropic": ProviderConfig(
                    type="anthropic",
                    endpoint="https://api.anthropic.com",
                    api_key="sk-anthropic"
                )
            },
            default_model_group="chat",
            model_groups={
                "chat": ["gpt-4", "claude-3"],
                "completion": ["text-davinci-003"]
            }
        )
        assert len(config.provider) == 2
        assert len(config.model_groups) == 2
        assert config.api.token == "test-token"

    def test_config_extra_fields_rejected(self):
        """Test that extra fields are rejected in Config."""
        with pytest.raises(ValidationError) as exc_info:
            Config(
                api=APIConfig(host="localhost", port=8080, token="token"),
                provider={},
                default_model_group="",
                model_groups={},
                extra_field="should fail"
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_config_nested_extra_fields_rejected(self):
        """Test that extra fields in nested models are also rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Config(
                api=APIConfig(host="localhost", port=8080, token="token", extra="reject"),
                provider={},
                default_model_group="",
                model_groups={}
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_config_empty_provider_dict(self):
        """Test Config with empty provider dictionary."""
        config = Config(
            api=APIConfig(host="localhost", port=8080, token="token"),
            provider={},
            default_model_group="",
            model_groups={}
        )
        assert config.provider == {}
        assert config.model_groups == {}

    def test_config_invalid_nested_api_port(self):
        """Test Config with invalid API port in nested model."""
        with pytest.raises(ValidationError) as exc_info:
            Config(
                api=APIConfig(host="localhost", port=0, token="token"),
                provider={},
                default_model_group="",
                model_groups={}
            )
        assert "port must be between 1 and 65535" in str(exc_info.value)

    def test_config_invalid_nested_provider(self):
        """Test Config with invalid nested provider config (extra field)."""
        with pytest.raises(ValidationError) as exc_info:
            Config(
                api=APIConfig(host="localhost", port=8080, token="token"),
                provider={
                    "bad": ProviderConfig(
                        type="openai",
                        endpoint="http://test",
                        api_key="key",
                        extra_field="should_fail"
                    )
                },
                default_model_group="",
                model_groups={}
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestModelValidation:
    """General validation tests for all models."""

    def test_api_config_dict_conversion(self):
        """Test APIConfig can be converted to dict."""
        config = APIConfig(host="localhost", port=8080, token="test")
        config_dict = config.model_dump()
        assert config_dict["host"] == "localhost"
        assert config_dict["port"] == 8080
        assert config_dict["token"] == "test"

    def test_provider_config_dict_conversion(self):
        """Test ProviderConfig can be converted to dict."""
        config = ProviderConfig(type="openai", endpoint="https://api.example.com", api_key="key")
        config_dict = config.model_dump()
        assert config_dict["type"] == "openai"
        assert config_dict["endpoint"] == "https://api.example.com"
        assert config_dict["api_key"] == "key"

    def test_config_dict_conversion(self):
        """Test Config can be converted to dict."""
        config = Config(
            api=APIConfig(host="localhost", port=8080, token="token"),
            provider={"test": ProviderConfig(type="test", endpoint="http://test", api_key="key")},
            default_model_group="group",
            model_groups={"group": ["model1"]}
        )
        config_dict = config.model_dump()
        assert config_dict["api"]["host"] == "localhost"
        assert "test" in config_dict["provider"]
        assert "group" in config_dict["model_groups"]
