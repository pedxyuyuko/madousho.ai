"""Tests for flow plugin models."""
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any

import pytest
from pydantic import ValidationError

from src.madousho.flow.models import (
    FlowPluginMetadata,
    FlowPluginConfig,
    FlowPlugin,
    PluginLoadResult
)


def test_flow_plugin_metadata_valid():
    """Test valid FlowPluginMetadata creation."""
    metadata = FlowPluginMetadata(
        name="test-flow",
        version="1.0.0",
        description="A test flow",
        author="Test Author"
    )
    
    assert metadata.name == "test-flow"
    assert metadata.version == "1.0.0"
    assert metadata.description == "A test flow"
    assert metadata.author == "Test Author"


def test_flow_plugin_metadata_required_fields():
    """Test FlowPluginMetadata requires name and version."""
    # Should fail without name
    with pytest.raises(ValidationError):
        FlowPluginMetadata(version="1.0.0")
    
    # Should fail without version
    with pytest.raises(ValidationError):
        FlowPluginMetadata(name="test-flow")


def test_flow_plugin_metadata_extra_forbidden():
    """Test FlowPluginMetadata rejects extra fields."""
    with pytest.raises(ValidationError):
        FlowPluginMetadata(
            name="test-flow",
            version="1.0.0",
            extra_field="should_not_be_allowed"
        )


def test_flow_plugin_config_allows_extra():
    """Test FlowPluginConfig allows extra fields."""
    config = FlowPluginConfig(
        field_typehint={".example": "MODEL_GROUP"},
        custom_field="custom_value",
        another_custom_field=42
    )
    
    assert config.field_typehint == {".example": "MODEL_GROUP"}
    assert config.custom_field == "custom_value"  # type: ignore
    assert config.another_custom_field == 42  # type: ignore


def test_flow_plugin_config_field_typehint_default():
    """Test FlowPluginConfig field_typehint defaults to empty dict."""
    config = FlowPluginConfig()
    assert config.field_typehint == {}


def test_flow_plugin_valid():
    """Test valid FlowPlugin creation."""
    temp_dir = Path(tempfile.mkdtemp())
    
    metadata = FlowPluginMetadata(
        name="test-flow",
        version="1.0.0",
        description="A test flow",
        author="Test Author"
    )
    
    config = FlowPluginConfig(
        field_typehint={".example": "MODEL_GROUP"}
    )
    
    plugin = FlowPlugin(
        metadata=metadata,
        path=temp_dir,
        config=config,
        flow_class=None,
        flow_instance=None
    )
    
    assert plugin.metadata == metadata
    assert plugin.path == temp_dir
    assert plugin.config == config
    assert plugin.flow_class is None
    assert plugin.flow_instance is None


def test_flow_plugin_extra_forbidden():
    """Test FlowPlugin rejects extra fields."""
    temp_dir = Path(tempfile.mkdtemp())
    
    metadata = FlowPluginMetadata(
        name="test-flow",
        version="1.0.0"
    )
    
    config = FlowPluginConfig()
    
    with pytest.raises(ValidationError):
        FlowPlugin(
            metadata=metadata,
            path=temp_dir,
            config=config,
            flow_class=None,
            flow_instance=None,
            extra_field="should_not_be_allowed"
        )


def test_plugin_load_result_success():
    """Test PluginLoadResult success creation."""
    temp_dir = Path(tempfile.mkdtemp())
    metadata = FlowPluginMetadata(name="test", version="1.0.0")
    config = FlowPluginConfig()
    plugin = FlowPlugin(
        metadata=metadata,
        path=temp_dir,
        config=config,
        flow_class=None,
        flow_instance=None
    )
    
    result = PluginLoadResult.success_result(plugin)
    
    assert result.success is True
    assert result.plugin == plugin
    assert result.errors == []
    assert result.warnings == []


def test_plugin_load_result_failure():
    """Test PluginLoadResult failure creation."""
    errors = ["Error 1", "Error 2"]
    warnings = ["Warning 1"]
    
    result = PluginLoadResult.failure_result(errors, warnings)
    
    assert result.success is False
    assert result.plugin is None
    assert result.errors == errors
    assert result.warnings == warnings


def test_plugin_load_result_defaults():
    """Test PluginLoadResult default values."""
    result = PluginLoadResult(success=False)
    
    assert result.success is False
    assert result.plugin is None
    assert result.errors == []
    assert result.warnings == []


def test_plugin_load_result_extra_forbidden():
    """Test PluginLoadResult rejects extra fields."""
    with pytest.raises(ValidationError):
        PluginLoadResult(
            success=True,
            extra_field="should_not_be_allowed"
        )


if __name__ == "__main__":
    pytest.main([__file__])