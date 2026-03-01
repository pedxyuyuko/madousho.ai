"""Unit tests for flow loader."""
import tempfile
import types
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

from madousho.flow.base import FlowBase
from madousho.flow.loader import (
    load_pyproject_metadata,
    import_flow_module,
    load_plugin,
)
from madousho.flow.models import FlowPluginMetadata, PluginLoadResult


class MockFlow(FlowBase):
    """Mock flow for testing purposes."""

    def run(self, **kwargs) -> Any:
        """Execute mock flow logic."""
        return "mock_result"


FlowClass = MockFlow  # Export as required by loader


class TestLoadPyprojectMetadata:
    """Tests for load_pyproject_metadata function."""

    def test_load_metadata_valid_pyproject(self, tmp_path: Path):
        """Test loading metadata from valid pyproject.toml."""
        pyproject_content = """
[project]
name = "test-flow"
version = "1.0.0"
description = "A test flow"
authors = [{name = "Test Author", email = "test@example.com"}]
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        metadata = load_pyproject_metadata(tmp_path)

        assert metadata.name == "test-flow"
        assert metadata.version == "1.0.0"
        assert metadata.description == "A test flow"
        assert metadata.author == "Test Author"

    def test_load_metadata_minimal_pyproject(self, tmp_path: Path):
        """Test loading metadata from minimal pyproject.toml."""
        pyproject_content = """
[project]
name = "minimal-flow"
version = "0.1.0"
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        metadata = load_pyproject_metadata(tmp_path)

        assert metadata.name == "minimal-flow"
        assert metadata.version == "0.1.0"
        assert metadata.description is None
        assert metadata.author is None

    def test_load_metadata_missing_pyproject(self, tmp_path: Path):
        """Test loading metadata when pyproject.toml is missing."""
        with pytest.raises(FileNotFoundError) as exc_info:
            load_pyproject_metadata(tmp_path)

        assert "pyproject.toml" in str(exc_info.value)

    def test_load_metadata_invalid_toml(self, tmp_path: Path):
        """Test loading metadata from invalid TOML file."""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text("invalid toml content [")

        with pytest.raises(ValueError) as exc_info:
            load_pyproject_metadata(tmp_path)

        assert "Invalid TOML" in str(exc_info.value)

    def test_load_metadata_missing_project_section(self, tmp_path: Path):
        """Test loading metadata when project section is missing."""
        pyproject_content = """
[tool.some_other_tool]
setting = "value"
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        metadata = load_pyproject_metadata(tmp_path)

        # Should use directory name as fallback
        assert metadata.name == tmp_path.name
        assert metadata.version == "0.0.0"

    def test_load_metadata_empty_authors_list(self, tmp_path: Path):
        """Test loading metadata with empty authors list."""
        pyproject_content = """
[project]
name = "test-flow"
version = "1.0.0"
authors = []
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        metadata = load_pyproject_metadata(tmp_path)

        assert metadata.name == "test-flow"
        assert metadata.author is None


class TestImportFlowModule:
    """Tests for import_flow_module function."""

    def test_import_module_valid(self, tmp_path: Path):
        """Test importing valid src/main.py module."""
        # Create src/main.py
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        main_py = src_dir / "main.py"
        main_py.write_text("""
from madousho.flow.base import FlowBase

class TestFlow(FlowBase):
    def run(self, **kwargs):
        return "test"

FlowClass = TestFlow
""")

        module = import_flow_module(tmp_path)

        assert hasattr(module, "FlowClass")
        assert module.FlowClass is not None

    def test_import_module_missing_main_py(self, tmp_path: Path):
        """Test importing when src/main.py is missing."""
        with pytest.raises(FileNotFoundError) as exc_info:
            import_flow_module(tmp_path)

        assert "src/main.py" in str(exc_info.value)

    def test_import_module_missing_src_directory(self, tmp_path: Path):
        """Test importing when src directory is missing."""
        with pytest.raises(FileNotFoundError) as exc_info:
            import_flow_module(tmp_path)

        assert "src" in str(exc_info.value)

    def test_import_module_syntax_error(self, tmp_path: Path):
        """Test importing module with syntax error."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        main_py = src_dir / "main.py"
        main_py.write_text("invalid python syntax {{{")

        with pytest.raises(SyntaxError) as exc_info:
            import_flow_module(tmp_path)

        assert "main.py" in str(exc_info.value) or "invalid syntax" in str(exc_info.value).lower()

    def test_import_module_creates_unique_name(self, tmp_path: Path):
        """Test that imported modules get unique names."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        main_py = src_dir / "main.py"
        main_py.write_text("""
from madousho.flow.base import FlowBase
class TestFlow(FlowBase):
    def run(self, **kwargs): pass
FlowClass = TestFlow
""")

        module1 = import_flow_module(tmp_path)
        module2 = import_flow_module(tmp_path)

        # Should be different module instances
        assert module1 is not module2


class TestLoadPlugin:
    """Tests for load_plugin function."""

    def create_valid_plugin(self, tmp_path: Path, config_content: str = "") -> Path:
        """Helper to create a valid plugin structure."""
        # Create pyproject.toml
        pyproject_content = """
[project]
name = "test-flow"
version = "1.0.0"
description = "A test flow"
"""
        (tmp_path / "pyproject.toml").write_text(pyproject_content)

        # Create config.yaml
        if not config_content:
            config_content = "field_typehint: {}"
        (tmp_path / "config.yaml").write_text(config_content)

        # Create src/main.py
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        main_py = src_dir / "main.py"
        main_py.write_text("""
from madousho.flow.base import FlowBase

class TestFlow(FlowBase):
    def run(self, **kwargs):
        return "test_result"

FlowClass = TestFlow
""")

        return tmp_path

    def test_load_plugin_success(self, tmp_path: Path):
        """Test successful plugin loading."""
        plugin_path = self.create_valid_plugin(tmp_path)
        global_config: Dict[str, Any] = {}

        result = load_plugin(plugin_path, global_config)

        assert result.success is True
        assert result.plugin is not None
        assert result.errors == []
        assert result.plugin.metadata.name == "test-flow"
        assert result.plugin.metadata.version == "1.0.0"
        assert result.plugin.flow_class is not None
        assert result.plugin.flow_instance is not None
        assert isinstance(result.plugin.flow_instance, FlowBase)

    def test_load_plugin_with_global_config(self, tmp_path: Path):
        """Test plugin loading with global config."""
        plugin_path = self.create_valid_plugin(tmp_path)
        global_config = {
            "api": {"port": 8000},
            "default_model_group": "gpt-4"
        }

        result = load_plugin(plugin_path, global_config)

        assert result.success is True
        assert result.plugin is not None
        assert result.plugin.flow_instance.global_config == global_config

    def test_load_plugin_missing_config_yaml(self, tmp_path: Path):
        """Test loading plugin without config.yaml."""
        # Create pyproject.toml
        pyproject_content = """
[project]
name = "test-flow"
version = "1.0.0"
"""
        (tmp_path / "pyproject.toml").write_text(pyproject_content)

        # Create src/main.py but NO config.yaml
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        main_py = src_dir / "main.py"
        main_py.write_text("""
from madousho.flow.base import FlowBase
class TestFlow(FlowBase):
    def run(self, **kwargs): pass
FlowClass = TestFlow
""")

        result = load_plugin(tmp_path, {})

        assert result.success is False
        assert len(result.errors) > 0
        assert "config.yaml" in str(result.errors[0]).lower() or "not found" in str(result.errors[0]).lower()

    def test_load_plugin_invalid_config_yaml(self, tmp_path: Path):
        """Test loading plugin with invalid config.yaml."""
        plugin_path = self.create_valid_plugin(tmp_path)
        (plugin_path / "config.yaml").write_text("invalid: yaml: [")

        result = load_plugin(plugin_path, {})

        assert result.success is False
        assert len(result.errors) > 0
        assert "YAML" in str(result.errors[0]) or "invalid" in str(result.errors[0]).lower()

    def test_load_plugin_missing_pyproject(self, tmp_path: Path):
        """Test loading plugin without pyproject.toml."""
        # Create config.yaml
        (tmp_path / "config.yaml").write_text("field_typehint: {}")

        # Create src/main.py
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        main_py = src_dir / "main.py"
        main_py.write_text("""
from madousho.flow.base import FlowBase
class TestFlow(FlowBase):
    def run(self, **kwargs): pass
FlowClass = TestFlow
""")

        result = load_plugin(tmp_path, {})

        assert result.success is False
        assert len(result.errors) > 0
        assert "pyproject.toml" in str(result.errors[0]).lower()

    def test_load_plugin_missing_main_py(self, tmp_path: Path):
        """Test loading plugin without src/main.py."""
        # Create pyproject.toml
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\nversion = '1.0.0'")

        # Create config.yaml
        (tmp_path / "config.yaml").write_text("field_typehint: {}")

        # NO src/main.py

        result = load_plugin(tmp_path, {})

        assert result.success is False
        assert len(result.errors) > 0
        assert "main.py" in str(result.errors[0]).lower()

    def test_load_plugin_missing_flowclass(self, tmp_path: Path):
        """Test loading plugin without FlowClass export."""
        plugin_path = self.create_valid_plugin(tmp_path)
        (plugin_path / "src" / "main.py").write_text("""
from madousho.flow.base import FlowBase

class TestFlow(FlowBase):
    def run(self, **kwargs): pass

# Missing: FlowClass = TestFlow
""")

        result = load_plugin(plugin_path, {})

        assert result.success is False
        assert len(result.errors) > 0
        assert "FlowClass" in str(result.errors[0])

    def test_load_plugin_flowclass_not_subclass(self, tmp_path: Path):
        """Test loading plugin with FlowClass that is not FlowBase subclass."""
        plugin_path = self.create_valid_plugin(tmp_path)
        (plugin_path / "src" / "main.py").write_text("""
class NotAFlow:
    pass

FlowClass = NotAFlow
""")

        result = load_plugin(plugin_path, {})

        assert result.success is False
        assert len(result.errors) > 0
        assert "FlowBase" in str(result.errors[0]) or "subclass" in str(result.errors[0]).lower()

    def test_load_plugin_with_typehint(self, tmp_path: Path):
        """Test loading plugin with config.typehint.yaml."""
        plugin_path = self.create_valid_plugin(tmp_path)

        # Add config.typehint.yaml
        typehint_content = """field_typehint:
  example_field: STRING
"""
        (plugin_path / "config.typehint.yaml").write_text(typehint_content)

        # Update config.yaml to match typehint
        config_content = """field_typehint: {}
example_field: "test_value"
"""
        (plugin_path / "config.yaml").write_text(config_content)

        result = load_plugin(plugin_path, {})

        # Should still succeed (typehint validation is separate)
        assert result.success is True

    def test_load_plugin_warning_no_typehint(self, tmp_path: Path):
        """Test that missing typehint generates warning."""
        plugin_path = self.create_valid_plugin(tmp_path)

        result = load_plugin(plugin_path, {})

        assert result.success is True
        # Should have warning about missing typehint
        assert any("typehint" in w.lower() for w in result.warnings)

    def test_load_plugin_config_validation_error(self, tmp_path: Path):
        """Test loading plugin with config validation error."""
        plugin_path = self.create_valid_plugin(tmp_path)

        # Add a typehint that requires a field
        typehint_content = """
fields:
  required_field:
    type: string
    required: true
"""
        (plugin_path / "config.typehint.yaml").write_text(typehint_content)

        # Config missing the required field
        config_content = """
field_typehint: {}
# missing required_field
"""
        (plugin_path / "config.yaml").write_text(config_content)

        result = load_plugin(plugin_path, {})

        # Should fail validation
        assert result.success is False
        assert len(result.errors) > 0

    def test_load_plugin_flow_config_passed_to_instance(self, tmp_path: Path):
        """Test that flow config is passed to flow instance."""
        plugin_path = self.create_valid_plugin(tmp_path)

        # Add custom config
        config_content = """
field_typehint: {}
custom_setting: "custom_value"
nested:
  key: "value"
"""
        (plugin_path / "config.yaml").write_text(config_content)

        result = load_plugin(plugin_path, {})

        assert result.success is True
        assert result.plugin is not None
        # Flow instance should have access to the config
        assert result.plugin.flow_instance.flow_config.get("custom_setting") == "custom_value"

    def test_load_plugin_multiple_errors_accumulated(self, tmp_path: Path):
        """Test that multiple errors are accumulated."""
        # Create plugin with multiple issues
        pyproject_content = "invalid yaml ["
        (tmp_path / "pyproject.toml").write_text(pyproject_content)

        # Missing config.yaml

        result = load_plugin(tmp_path, {})

        assert result.success is False
        # Should have at least one error (pyproject.toml or config.yaml)
        assert len(result.errors) > 0


class TestLoadPluginIntegration:
    """Integration tests for plugin loading."""

    def test_complete_plugin_lifecycle(self, tmp_path: Path):
        """Test complete plugin loading and execution lifecycle."""
        # Create plugin
        plugin_path = self.create_valid_plugin_structure(tmp_path)

        # Load plugin
        global_config = {"default_model_group": "gpt-4"}
        result = load_plugin(plugin_path, global_config)

        assert result.success is True
        assert result.plugin is not None

        plugin = result.plugin

        # Test flow instance can be executed
        flow_instance = plugin.flow_instance
        assert flow_instance is not None

        # Call lifecycle hooks
        flow_instance.on_start()
        run_result = flow_instance.run()
        flow_instance.on_complete(run_result)

        # Verify metadata
        assert plugin.metadata.name == "integration-test-flow"
        assert plugin.metadata.version == "2.0.0"

    def create_valid_plugin_structure(self, tmp_path: Path) -> Path:
        """Create a complete plugin structure for integration testing."""
        # pyproject.toml
        pyproject_content = """
[project]
name = "integration-test-flow"
version = "2.0.0"
description = "Integration test flow"
authors = [{name = "Integration Tester"}]
"""
        (tmp_path / "pyproject.toml").write_text(pyproject_content)

        # config.yaml
        config_content = """
field_typehint: {}
integration_test_field: "test_value"
"""
        (tmp_path / "config.yaml").write_text(config_content)

        # src/main.py
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        main_py = src_dir / "main.py"
        main_py.write_text("""
from madousho.flow.base import FlowBase
from typing import Any, Dict

class IntegrationTestFlow(FlowBase):
    def __init__(self, flow_config: Dict[str, Any], global_config: Dict[str, Any] = None):
        super().__init__(flow_config, global_config)
        self.executed = False
    
    def run(self, **kwargs) -> Any:
        self.executed = True
        return {
            "status": "success",
            "flow_config": self.flow_config,
            "global_config": self.global_config
        }

FlowClass = IntegrationTestFlow
""")

        return tmp_path


if __name__ == "__main__":
    pytest.main([__file__])
