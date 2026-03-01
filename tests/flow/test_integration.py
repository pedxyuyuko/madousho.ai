"""Integration tests for flow plugin loading system."""
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

from madousho.flow.base import FlowBase
from madousho.flow.loader import load_plugin
from madousho.flow.registry import FlowRegistry, get_registry
from madousho.flow.models import PluginLoadResult


def create_valid_plugin(
    tmp_path: Path,
    plugin_name: str = "test-flow",
    version: str = "1.0.0",
    config_content: str = "",
    has_typehint: bool = False,
) -> Path:
    """Helper to create a valid plugin structure."""
    # Ensure directory exists
    tmp_path.mkdir(parents=True, exist_ok=True)
    
    # Create pyproject.toml
    # Create pyproject.toml
    pyproject_content = f"""
[project]
name = "{plugin_name}"
version = "{version}"
description = "A test flow plugin"
authors = [{{name = "Test Author"}}]
"""
    (tmp_path / "pyproject.toml").write_text(pyproject_content)

    # Create config.yaml
    if not config_content:
        config_content = "field_typehint: {}"
    (tmp_path / "config.yaml").write_text(config_content)

    # Create config.typehint.yaml if requested
    if has_typehint:
        typehint_content = """
field_typehint:
  flow_name: STRING
  timeout: INTEGER
"""
        (tmp_path / "config.typehint.yaml").write_text(typehint_content)

    # Create src/main.py
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    main_py = src_dir / "main.py"
    main_py.write_text(f"""
from madousho.flow.base import FlowBase
from typing import Any, Dict

class {plugin_name.replace('-', '_').title().replace('_', '')}Flow(FlowBase):
    def run(self, **kwargs) -> Any:
        return {{"status": "success", "plugin": "{plugin_name}"}}

FlowClass = {plugin_name.replace('-', '_').title().replace('_', '')}Flow
""")

    return tmp_path


class TestHappyPath:
    """Test successful plugin loading workflow."""

    def test_complete_plugin_loading_success(self, tmp_path: Path):
        """Test complete plugin loading from directory scan to instantiation."""
        plugin_path = create_valid_plugin(tmp_path)
        global_config: Dict[str, Any] = {}

        result = load_plugin(plugin_path, global_config)

        # Verify result
        assert result.success is True
        assert result.plugin is not None
        assert result.errors == []
        assert len(result.warnings) >= 0  # May have warning about missing typehint

        # Verify plugin metadata
        plugin = result.plugin
        assert plugin.metadata.name == "test-flow"
        assert plugin.metadata.version == "1.0.0"
        assert plugin.metadata.description == "A test flow plugin"
        assert plugin.metadata.author == "Test Author"

        # Verify flow instance
        assert plugin.flow_instance is not None
        assert isinstance(plugin.flow_instance, FlowBase)
        assert plugin.flow_instance.flow_config == plugin.config.model_dump()
        assert plugin.flow_instance.global_config == global_config

    def test_plugin_with_full_configuration(self, tmp_path: Path):
        """Test plugin loading with comprehensive config and typehint."""
        config_content = """
field_typehint: {}
flow_name: "my_custom_flow"
timeout: 60
enabled: true
model_group: "openai_models"
nested:
  key: "value"
  another: 123
"""
        plugin_path = create_valid_plugin(
            tmp_path,
            plugin_name="full-config-flow",
            config_content=config_content,
            has_typehint=True,
        )

        global_config = {
            "model_groups": {
                "openai_models": {"provider": "openai"}
            }
        }

        result = load_plugin(plugin_path, global_config)

        assert result.success is True
        assert result.plugin is not None
        assert result.plugin.config.flow_name == "my_custom_flow"  # type: ignore
        assert result.plugin.config.timeout == 60  # type: ignore
        assert result.plugin.config.enabled is True  # type: ignore

    def test_plugin_execution_after_loading(self, tmp_path: Path):
        """Test that loaded plugin can be executed successfully."""
        plugin_path = create_valid_plugin(tmp_path, plugin_name="exec-flow")
        global_config: Dict[str, Any] = {}

        result = load_plugin(plugin_path, global_config)

        assert result.success is True
        assert result.plugin is not None

        # Execute the flow
        flow_instance = result.plugin.flow_instance
        flow_instance.on_start()
        run_result = flow_instance.run(param1="value1", param2="value2")
        flow_instance.on_complete(run_result)

        # Verify execution result
        assert run_result is not None
        assert run_result["status"] == "success"
        assert run_result["plugin"] == "exec-flow"


class TestMissingConfigYaml:
    """Test error handling when config.yaml is missing."""

    def test_missing_config_yaml_error(self, tmp_path: Path):
        """Test that missing config.yaml produces clear error."""
        # Create pyproject.toml
        pyproject_content = """
[project]
name = "missing-config-flow"
version = "1.0.0"
"""
        (tmp_path / "pyproject.toml").write_text(pyproject_content)

        # Create src/main.py but NO config.yaml
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        main_py = src_dir / "main.py"
        main_py.write_text("""
from madousho.flow.base import FlowBase

class MissingConfigFlow(FlowBase):
    def run(self, **kwargs):
        return "result"

FlowClass = MissingConfigFlow
""")

        result = load_plugin(tmp_path, {})

        assert result.success is False
        assert len(result.errors) > 0
        assert any("config.yaml" in err.lower() or "not found" in err.lower() for err in result.errors)
        assert result.plugin is None

    def test_missing_config_yaml_with_valid_main_py(self, tmp_path: Path):
        """Test missing config.yaml even when main.py is valid."""
        # Create complete plugin except config.yaml
        pyproject_content = """
[project]
name = "no-config-flow"
version = "1.0.0"
"""
        (tmp_path / "pyproject.toml").write_text(pyproject_content)

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("""
from madousho.flow.base import FlowBase

class NoConfigFlow(FlowBase):
    def run(self, **kwargs):
        pass

FlowClass = NoConfigFlow
""")

        result = load_plugin(tmp_path, {})

        assert result.success is False
        assert any("config" in err.lower() for err in result.errors)


class TestInvalidConfigYaml:
    """Test error handling when config.yaml is invalid."""

    def test_invalid_yaml_syntax_error(self, tmp_path: Path):
        """Test that invalid YAML syntax produces clear error."""
        plugin_path = create_valid_plugin(tmp_path)
        # Corrupt the YAML
        (plugin_path / "config.yaml").write_text("invalid: yaml: [unclosed")

        result = load_plugin(plugin_path, {})

        assert result.success is False
        assert len(result.errors) > 0
        assert any("YAML" in err or "invalid" in err.lower() for err in result.errors)

    def test_invalid_config_validation_error(self, tmp_path: Path):
        """Test that config validation errors are reported."""
        # Create plugin with typehint requiring specific fields
        config_content = """
field_typehint: {}
"""
        plugin_path = create_valid_plugin(
            tmp_path,
            plugin_name="invalid-config-flow",
            config_content=config_content,
            has_typehint=True,
        )

        # Add typehint that requires a field
        typehint_content = """
fields:
  required_field:
    type: string
    required: true
"""
        (plugin_path / "config.typehint.yaml").write_text(typehint_content)

        result = load_plugin(plugin_path, {})

        assert result.success is False
        assert len(result.errors) > 0


class TestMissingFlowClass:
    """Test error handling when FlowClass is missing."""

    def test_missing_flowclass_export(self, tmp_path: Path):
        """Test that missing FlowClass export produces clear error."""
        plugin_path = create_valid_plugin(tmp_path)
        # Remove FlowClass export
        (plugin_path / "src" / "main.py").write_text("""
from madousho.flow.base import FlowBase

class TestFlow(FlowBase):
    def run(self, **kwargs):
        return "result"

# Missing: FlowClass = TestFlow
""")

        result = load_plugin(plugin_path, {})

        assert result.success is False
        assert len(result.errors) > 0
        assert any("FlowClass" in err for err in result.errors)

    def test_flowclass_not_subclass_of_flowbase(self, tmp_path: Path):
        """Test that FlowClass must be FlowBase subclass."""
        plugin_path = create_valid_plugin(tmp_path)
        # Export wrong class
        (plugin_path / "src" / "main.py").write_text("""
class NotAFlowClass:
    pass

FlowClass = NotAFlowClass
""")

        result = load_plugin(plugin_path, {})

        assert result.success is False
        assert len(result.errors) > 0
        assert any("FlowBase" in err or "subclass" in err.lower() for err in result.errors)

    def test_flowclass_is_instance_not_class(self, tmp_path: Path):
        """Test that FlowClass must be a class, not an instance."""
        plugin_path = create_valid_plugin(tmp_path)
        (plugin_path / "src" / "main.py").write_text("""
from madousho.flow.base import FlowBase

class TestFlow(FlowBase):
    def run(self, **kwargs):
        pass

# Wrong: exporting instance instead of class
FlowClass = TestFlow()
""")

        result = load_plugin(plugin_path, {})

        assert result.success is False
        assert len(result.errors) > 0


class TestModelGroupValidation:
    """Test MODEL_GROUP validation failures."""

    def test_model_group_not_in_global_config(self, tmp_path: Path):
        """Test that MODEL_GROUP validation fails when group not in global config."""
        config_content = """
field_typehint: {}
model_group: "nonexistent_group"
"""
        plugin_path = create_valid_plugin(
            tmp_path,
            plugin_name="model-group-flow",
            config_content=config_content,
            has_typehint=True,
        )

        # Add typehint for model_group
        typehint_content = """
field_typehint:
  model_group: MODEL_GROUP
"""
        (plugin_path / "config.typehint.yaml").write_text(typehint_content)

        # Global config without the referenced model group
        global_config = {
            "model_groups": {
                "openai_models": {"provider": "openai"},
                "anthropic_models": {"provider": "anthropic"}
            }
        }

        result = load_plugin(plugin_path, global_config)

        assert result.success is False
        assert len(result.errors) > 0
        assert any("nonexistent_group" in err or "model group" in err.lower() for err in result.errors)

    def test_model_group_empty_no_default(self, tmp_path: Path):
        """Test MODEL_GROUP validation with empty value and no global default."""
        config_content = """
field_typehint: {}
model_group: ""
"""
        plugin_path = create_valid_plugin(
            tmp_path,
            plugin_name="empty-model-group-flow",
            config_content=config_content,
            has_typehint=True,
        )

        typehint_content = """
field_typehint:
  model_group: MODEL_GROUP
"""
        (plugin_path / "config.typehint.yaml").write_text(typehint_content)

        global_config = {
            "model_groups": {
                "openai_models": {"provider": "openai"}
            }
            # No default_model_group
        }

        result = load_plugin(plugin_path, global_config)

        assert result.success is False
        assert len(result.errors) > 0
        assert any("default_model_group" in err or "empty" in err.lower() for err in result.errors)

    def test_model_group_success_with_valid_config(self, tmp_path: Path):
        """Test MODEL_GROUP validation passes with valid configuration."""
        config_content = """
field_typehint: {}
model_group: "anthropic_models"
"""
        plugin_path = create_valid_plugin(
            tmp_path,
            plugin_name="valid-model-group-flow",
            config_content=config_content,
            has_typehint=True,
        )

        typehint_content = """
field_typehint:
  model_group: MODEL_GROUP
"""
        (plugin_path / "config.typehint.yaml").write_text(typehint_content)

        global_config = {
            "model_groups": {
                "openai_models": {"provider": "openai"},
                "anthropic_models": {"provider": "anthropic"}
            }
        }

        result = load_plugin(plugin_path, global_config)

        assert result.success is True
        assert result.plugin is not None
        assert result.errors == []

    def test_model_group_uses_global_default(self, tmp_path: Path):
        """Test MODEL_GROUP validation uses global default when empty."""
        config_content = """
field_typehint: {}
model_group: ""
"""
        plugin_path = create_valid_plugin(
            tmp_path,
            plugin_name="default-model-group-flow",
            config_content=config_content,
            has_typehint=True,
        )

        typehint_content = """
field_typehint:
  model_group: MODEL_GROUP
"""
        (plugin_path / "config.typehint.yaml").write_text(typehint_content)

        global_config = {
            "default_model_group": "openai_models",
            "model_groups": {
                "openai_models": {"provider": "openai"}
            }
        }

        result = load_plugin(plugin_path, global_config)

        assert result.success is True
        # Should have warning about using default
        assert any("default" in w.lower() for w in result.warnings)


class TestMixedModeErrorReporting:
    """Test mixed mode: some plugins load successfully, others fail."""

    def create_plugin_structure(
        self,
        base_path: Path,
        plugin_name: str,
        include_config: bool = True,
        valid_yaml: bool = True,
        include_flowclass: bool = True,
        model_group: str = None,
    ) -> Path:
        """Helper to create plugin with specific characteristics."""
        plugin_dir = base_path / plugin_name
        plugin_dir.mkdir()

        # pyproject.toml
        pyproject_content = f"""
[project]
name = "{plugin_name}"
version = "1.0.0"
"""
        (plugin_dir / "pyproject.toml").write_text(pyproject_content)

        # config.yaml
        if include_config:
            if valid_yaml:
                config_content = "field_typehint: {}"
                if model_group:
                    config_content += f"\nmodel_group: {model_group}"
                (plugin_dir / "config.yaml").write_text(config_content)
            else:
                (plugin_dir / "config.yaml").write_text("invalid: [")
        # else: no config.yaml

        # src/main.py
        src_dir = plugin_dir / "src"
        src_dir.mkdir()
        if include_flowclass:
            (src_dir / "main.py").write_text(f"""
from madousho.flow.base import FlowBase

class {plugin_name.replace('-', '_').title().replace('_', '')}Flow(FlowBase):
    def run(self, **kwargs):
        pass

FlowClass = {plugin_name.replace('-', '_').title().replace('_', '')}Flow
""")
        else:
            (src_dir / "main.py").write_text("""
from madousho.flow.base import FlowBase

class SomeFlow(FlowBase):
    def run(self, **kwargs):
        pass

# Missing FlowClass export
""")

        return plugin_dir

    def test_mixed_mode_multiple_plugins_some_fail(self, tmp_path: Path):
        """Test loading multiple plugins where some succeed and some fail."""
        # Create 3 plugins: 1 valid, 2 with different errors
        plugin1 = self.create_plugin_structure(tmp_path, "valid-plugin")
        plugin2 = self.create_plugin_structure(
            tmp_path, "no-config-plugin", include_config=False
        )
        plugin3 = self.create_plugin_structure(
            tmp_path, "no-flowclass-plugin", include_flowclass=False
        )

        # Load all plugins
        results = []
        global_config: Dict[str, Any] = {}

        for plugin_path in [plugin1, plugin2, plugin3]:
            result = load_plugin(plugin_path, global_config)
            results.append((plugin_path.name, result))

        # Verify mixed results
        valid_result = next(r for name, r in results if name == "valid-plugin")
        no_config_result = next(r for name, r in results if name == "no-config-plugin")
        no_flowclass_result = next(r for name, r in results if name == "no-flowclass-plugin")

        # Plugin 1: Success
        assert valid_result.success is True
        assert valid_result.plugin is not None
        assert valid_result.errors == []

        # Plugin 2: Failed (missing config)
        assert no_config_result.success is False
        assert len(no_config_result.errors) > 0
        assert any("config" in err.lower() for err in no_config_result.errors)

        # Plugin 3: Failed (missing FlowClass)
        assert no_flowclass_result.success is False
        assert len(no_flowclass_result.errors) > 0
        assert any("FlowClass" in err for err in no_flowclass_result.errors)

    def test_mixed_mode_error_messages_are_clear(self, tmp_path: Path):
        """Test that error messages in mixed mode are clear and specific."""
        plugin1 = self.create_plugin_structure(tmp_path, "good-plugin")
        plugin2 = self.create_plugin_structure(
            tmp_path, "bad-yaml-plugin", valid_yaml=False
        )
        plugin3 = self.create_plugin_structure(
            tmp_path, "bad-model-group-plugin", model_group="invalid_group"
        )

        # Add typehint for plugin3
        typehint_content = """
field_typehint:
  model_group: MODEL_GROUP
"""
        (plugin3 / "config.typehint.yaml").write_text(typehint_content)

        global_config = {
            "model_groups": {
                "valid_group": {"provider": "openai"}
            }
        }

        results = []
        for plugin_path in [plugin1, plugin2, plugin3]:
            result = load_plugin(plugin_path, global_config)
            results.append((plugin_path.name, result))

        # Verify each has specific, clear error
        bad_yaml_result = next(r for name, r in results if name == "bad-yaml-plugin")
        assert bad_yaml_result.success is False
        assert any("YAML" in err or "invalid" in err.lower() for err in bad_yaml_result.errors)

        bad_model_group_result = next(r for name, r in results if name == "bad-model-group-plugin")
        assert bad_model_group_result.success is False
        assert any("model group" in err.lower() or "invalid_group" in err for err in bad_model_group_result.errors)


class TestFlowRegistrationAndRetrieval:
    """Test successful flow registration and retrieval from registry."""

    def test_register_loaded_flow_to_registry(self, tmp_path: Path):
        """Test registering a successfully loaded flow to the registry."""
        # Reset registry to clean state
        FlowRegistry.reset_instance()
        registry = get_registry()
        registry.clear()

        # Create and load plugin
        plugin_path = create_valid_plugin(tmp_path, plugin_name="registry-test-flow")
        global_config: Dict[str, Any] = {}

        result = load_plugin(plugin_path, global_config)

        assert result.success is True
        assert result.plugin is not None

        # Register the flow
        flow_name = "registry-test-flow"
        registry.register(flow_name, result.plugin.flow_instance)

        # Verify registration
        assert flow_name in registry.list_all()

        # Retrieve and verify
        retrieved_flow = registry.get(flow_name)
        assert retrieved_flow is result.plugin.flow_instance
        assert isinstance(retrieved_flow, FlowBase)

    def test_register_multiple_flows(self, tmp_path: Path):
        """Test registering multiple flows to the registry."""
        FlowRegistry.reset_instance()
        registry = get_registry()
        registry.clear()

        # Create and load multiple plugins
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        flow_names = ["flow-a", "flow-b", "flow-c"]
        loaded_flows = []

        for name in flow_names:
            plugin_path = create_valid_plugin(plugins_dir / name, plugin_name=name)
            result = load_plugin(plugin_path, {})
            assert result.success is True
            loaded_flows.append(result.plugin.flow_instance)

            # Register
            registry.register(name, result.plugin.flow_instance)

        # Verify all registered
        registered = registry.list_all()
        assert set(registered) == set(flow_names)

        # Verify all retrievable
        for name in flow_names:
            flow = registry.get(name)
            assert isinstance(flow, FlowBase)

    def test_register_flow_prevents_duplicate(self, tmp_path: Path):
        """Test that registering duplicate flow name raises error."""
        FlowRegistry.reset_instance()
        registry = get_registry()
        registry.clear()

        plugin_path = create_valid_plugin(tmp_path, plugin_name="duplicate-test-flow")
        result = load_plugin(plugin_path, {})

        assert result.success is True

        # Register first time
        registry.register("test-flow", result.plugin.flow_instance)

        # Try to register again with same name
        with pytest.raises(ValueError, match="Flow 'test-flow' is already registered"):
            registry.register("test-flow", result.plugin.flow_instance)

    def test_end_to_end_load_register_execute(self, tmp_path: Path):
        """Test complete end-to-end workflow: load → register → execute."""
        FlowRegistry.reset_instance()
        registry = get_registry()
        registry.clear()

        # Create plugin with execution tracking
        plugin_path = create_valid_plugin(tmp_path, plugin_name="e2e-flow")
        (plugin_path / "src" / "main.py").write_text("""
from madousho.flow.base import FlowBase
from typing import Any, Dict

class E2eFlow(FlowBase):
    def __init__(self, flow_config: Dict[str, Any], global_config: Dict[str, Any] = None):
        super().__init__(flow_config, global_config)
        self.executed = False
        self.execution_params = None
    
    def run(self, **kwargs) -> Any:
        self.executed = True
        self.execution_params = kwargs
        return {
            "status": "completed",
            "params": kwargs,
            "flow_config": self.flow_config,
            "global_config": self.global_config
        }

FlowClass = E2eFlow
""")

        global_config = {
            "default_model_group": "openai_models",
            "model_groups": {
                "openai_models": {"provider": "openai"}
            }
        }

        # Load plugin
        result = load_plugin(plugin_path, global_config)
        assert result.success is True

        # Register flow
        flow_name = "e2e-flow"
        registry.register(flow_name, result.plugin.flow_instance)

        # Retrieve flow
        flow = registry.get(flow_name)
        assert flow is not None

        # Execute flow
        flow.on_start()
        execution_result = flow.run(param1="value1", param2=42)
        flow.on_complete(execution_result)

        # Verify execution
        assert execution_result["status"] == "completed"
        assert execution_result["params"]["param1"] == "value1"
        assert execution_result["params"]["param2"] == 42
        assert flow.executed is True
        assert flow.execution_params == {"param1": "value1", "param2": 42}

        # Verify config was passed correctly
        assert flow.flow_config is not None
        assert flow.global_config == global_config


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_plugin_with_empty_pyproject(self, tmp_path: Path):
        """Test plugin with minimal pyproject.toml."""
        (tmp_path / "pyproject.toml").write_text("""
[project]
name = "minimal"
version = "0.0.1"
""")

        (tmp_path / "config.yaml").write_text("field_typehint: {}")

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("""
from madousho.flow.base import FlowBase

class MinimalFlow(FlowBase):
    def run(self, **kwargs):
        return "minimal"

FlowClass = MinimalFlow
""")

        result = load_plugin(tmp_path, {})

        assert result.success is True
        assert result.plugin is not None
        assert result.plugin.metadata.name == "minimal"
        assert result.plugin.metadata.version == "0.0.1"
        assert result.plugin.metadata.description is None
        assert result.plugin.metadata.author is None

    def test_plugin_with_unicode_content(self, tmp_path: Path):
        """Test plugin with unicode characters in content."""
        pyproject_content = """
[project]
name = "unicode-flow"
version = "1.0.0"
description = "测试插件 - テストプラグイン - Plugin de test"
authors = [{name = "测试作者"}]
"""
        (tmp_path / "pyproject.toml").write_text(pyproject_content, encoding="utf-8")
        (tmp_path / "config.yaml").write_text("field_typehint: {}", encoding="utf-8")

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("""
from madousho.flow.base import FlowBase

class UnicodeFlow(FlowBase):
    def run(self, **kwargs):
        return {"message": "こんにちは世界"}

FlowClass = UnicodeFlow
""", encoding="utf-8")

        result = load_plugin(tmp_path, {})

        assert result.success is True
        assert result.plugin is not None
        assert "测试" in result.plugin.metadata.description or "テスト" in result.plugin.metadata.description

    def test_nested_directory_structure(self, tmp_path: Path):
        """Test plugin in deeply nested directory structure."""
        nested_path = tmp_path / "level1" / "level2" / "level3" / "nested-flow"
        nested_path.mkdir(parents=True)

        plugin_path = create_valid_plugin(nested_path, plugin_name="nested-flow")

        result = load_plugin(plugin_path, {})

        assert result.success is True
        assert result.plugin is not None
        assert result.plugin.metadata.name == "nested-flow"
