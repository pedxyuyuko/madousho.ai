"""Tests for flow configuration validation."""
# pyright: reportAttributeAccessIssue=none, reportUnknownMemberType=none, reportUnusedVariable=none, reportUnusedCallResult=none, reportUnknownArgumentType=none, reportOperatorIssue=none

from pathlib import Path

import pytest
import yaml

from src.madousho.flow.loader import (
    load_flow_config,
    load_typehint,
    validate_flow_config,
)
from src.madousho.flow.models import FlowPluginConfig


class TestLoadFlowConfig:
    """Test load_flow_config function."""

    def test_load_valid_config(self, tmp_path: Path):
        """Test loading a valid config.yaml."""
        config_data = {
            "field_typehint": {".example": "MODEL_GROUP"},
            "custom_setting": "value"
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        config = load_flow_config(tmp_path)

        assert config.field_typehint == {".example": "MODEL_GROUP"}
        assert config.custom_setting == "value"  # type: ignore

    def test_load_empty_config(self, tmp_path: Path):
        """Test loading an empty config.yaml."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("")

        config = load_flow_config(tmp_path)

        assert config.field_typehint == {}

    def test_load_missing_config(self, tmp_path: Path):
        """Test loading non-existent config.yaml raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError) as exc_info:
            load_flow_config(tmp_path)

        assert "Flow config file not found" in str(exc_info.value)

    def test_load_invalid_yaml(self, tmp_path: Path):
        """Test loading invalid YAML raises ValueError."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: yaml: content: [")

        with pytest.raises(ValueError) as exc_info:
            load_flow_config(tmp_path)

        assert "Invalid YAML" in str(exc_info.value)

    def test_load_config_with_hyphens(self, tmp_path: Path):
        """Test loading config with hyphenated keys (auto-normalized)."""
        config_data = {
            "field-typehint": {".example": "MODEL_GROUP"},
            "custom-setting": "value"
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        config = load_flow_config(tmp_path)

        # Pydantic should handle the key normalization
        # Pydantic should handle the key normalization
        assert ".example" in config.field_typehint  # type: ignore[operator]


class TestLoadTypehint:
    """Test load_typehint function."""

    def test_load_valid_typehint(self, tmp_path: Path):
        """Test loading a valid config.typehint.yaml."""
        typehint_data = {
            "field_typehint": {
                "flow.model_group": "MODEL_GROUP",
                "flow.name": "STRING",
                "flow.timeout": "INTEGER"
            }
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        typehint_def = load_typehint(tmp_path)

        assert typehint_def is not None
        assert len(typehint_def.field_typehint) == 3

    def test_load_missing_typehint(self, tmp_path: Path):
        """Test loading non-existent config.typehint.yaml returns None."""
        # Only create config.yaml, not config.typehint.yaml
        config_file = tmp_path / "config.yaml"
        config_file.write_text("")

        typehint_def = load_typehint(tmp_path)

        assert typehint_def is None

    def test_load_invalid_typehint_yaml(self, tmp_path: Path):
        """Test loading invalid typehint YAML raises ValueError."""
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text("invalid: yaml: [")

        with pytest.raises(ValueError) as exc_info:
            load_typehint(tmp_path)

        assert "Invalid YAML" in str(exc_info.value)

    def test_load_invalid_typehint_type(self, tmp_path: Path):
        """Test loading typehint with invalid type raises ValueError."""
        typehint_data = {
            "field_typehint": {
                "flow.invalid": "INVALID_TYPE"
            }
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        with pytest.raises(ValueError) as exc_info:
            load_typehint(tmp_path)

        assert "Invalid typehint" in str(exc_info.value)


class TestValidateFlowConfig:
    """Test validate_flow_config function."""

    def test_validate_success_with_typehint(self, tmp_path: Path):
        """Test successful validation with typehint."""
        # Create config.yaml
        config_data = {
            "field_typehint": {".example": "MODEL_GROUP"},
            "model_group": "openai_models"
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        # Create config.typehint.yaml
        typehint_data = {
            "field_typehint": {
                "model_group": "MODEL_GROUP"
            }
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        global_config = {
            "model_groups": {
                "openai_models": {"provider": "openai"}
            }
        }

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, global_config
        )

        assert is_valid is True
        assert len(errors) == 0
        assert config.model_group == "openai_models"  # type: ignore

    def test_validate_success_without_typehint(self, tmp_path: Path):
        """Test successful validation without typehint file."""
        # Create only config.yaml
        config_data = {
            "field_typehint": {".example": "MODEL_GROUP"}
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        global_config = {}

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, global_config
        )

        assert is_valid is True
        assert len(errors) == 0
        assert len(warnings) == 1
        assert "No config.typehint.yaml found" in warnings[0]

    def test_validate_missing_config(self, tmp_path: Path):
        """Test validation fails when config.yaml is missing."""
        global_config = {}

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, global_config
        )

        assert is_valid is False
        assert len(errors) == 1
        assert "Flow config file not found" in errors[0]
        assert isinstance(config, FlowPluginConfig)

    def test_validate_invalid_config_yaml(self, tmp_path: Path):
        """Test validation fails with invalid config YAML."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: yaml: [")

        global_config = {}

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, global_config
        )

        assert is_valid is False
        assert len(errors) == 1
        assert "Invalid YAML" in errors[0]

    def test_validate_invalid_typehint_yaml(self, tmp_path: Path):
        """Test validation fails with invalid typehint YAML."""
        # Create valid config.yaml
        config_file = tmp_path / "config.yaml"
        config_file.write_text("")

        # Create invalid typehint.yaml
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text("invalid: yaml: [")

        global_config = {}

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, global_config
        )

        assert is_valid is False
        assert len(errors) == 1
        assert "Invalid YAML" in errors[0]

    def test_validate_model_group_success(self, tmp_path: Path):
        """Test MODEL_GROUP validation passes with valid group."""
        config_data = {"model_group": "anthropic_models"}
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        typehint_data = {
            "field_typehint": {"model_group": "MODEL_GROUP"}
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        global_config = {
            "model_groups": {
                "openai_models": {"provider": "openai"},
                "anthropic_models": {"provider": "anthropic"}
            }
        }

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, global_config
        )

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_model_group_failure(self, tmp_path: Path):
        """Test MODEL_GROUP validation fails with invalid group."""
        config_data = {"model_group": "nonexistent_group"}
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        typehint_data = {
            "field_typehint": {"model_group": "MODEL_GROUP"}
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        global_config = {
            "model_groups": {
                "openai_models": {"provider": "openai"}
            }
        }

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, global_config
        )

        assert is_valid is False
        assert len(errors) == 1
        assert "references non-existent model group" in errors[0]

    def test_validate_model_group_empty_with_default(self, tmp_path: Path):
        """Test MODEL_GROUP validation with empty value and global default."""
        config_data = {"model_group": ""}
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        typehint_data = {
            "field_typehint": {"model_group": "MODEL_GROUP"}
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        global_config = {
            "default_model_group": "openai_models",
            "model_groups": {
                "openai_models": {"provider": "openai"}
            }
        }

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, global_config
        )

        assert is_valid is True
        assert len(errors) == 0
        assert len(warnings) == 1
        assert "empty, using global default_model_group" in warnings[0]

    def test_validate_model_group_empty_without_default(self, tmp_path: Path):
        """Test MODEL_GROUP validation with empty value and no global default."""
        config_data = {"model_group": ""}
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        typehint_data = {
            "field_typehint": {"model_group": "MODEL_GROUP"}
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        global_config = {
            "model_groups": {
                "openai_models": {"provider": "openai"}
            }
        }

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, global_config
        )

        assert is_valid is False
        assert len(errors) == 1
        assert "no 'default_model_group' defined in global config" in errors[0]

    def test_validate_string_type_success(self, tmp_path: Path):
        """Test STRING type validation passes."""
        config_data = {"flow_name": "test_flow"}
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        typehint_data = {
            "field_typehint": {"flow_name": "STRING"}
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, {}
        )

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_string_type_failure(self, tmp_path: Path):
        """Test STRING type validation fails with wrong type."""
        config_data = {"flow_name": 123}
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        typehint_data = {
            "field_typehint": {"flow_name": "STRING"}
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, {}
        )

        assert is_valid is False
        assert len(errors) == 1
        assert "must be a string" in errors[0]

    def test_validate_integer_type_success(self, tmp_path: Path):
        """Test INTEGER type validation passes."""
        config_data = {"timeout": 30}
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        typehint_data = {
            "field_typehint": {"timeout": "INTEGER"}
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, {}
        )

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_integer_type_failure(self, tmp_path: Path):
        """Test INTEGER type validation fails with wrong type."""
        config_data = {"timeout": "thirty"}
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        typehint_data = {
            "field_typehint": {"timeout": "INTEGER"}
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, {}
        )

        assert is_valid is False
        assert len(errors) == 1
        assert "must be an integer" in errors[0]

    def test_validate_boolean_type_success(self, tmp_path: Path):
        """Test BOOLEAN type validation passes."""
        config_data = {"enabled": True}
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        typehint_data = {
            "field_typehint": {"enabled": "BOOLEAN"}
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, {}
        )

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_list_type_success(self, tmp_path: Path):
        """Test LIST type validation passes."""
        config_data = {"steps": ["step1", "step2"]}
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        typehint_data = {
            "field_typehint": {"steps": "LIST"}
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, {}
        )

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_dict_type_success(self, tmp_path: Path):
        """Test DICT type validation passes."""
        config_data = {"params": {"key": "value"}}
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        typehint_data = {
            "field_typehint": {"params": "DICT"}
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, {}
        )

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_nested_field_path(self, tmp_path: Path):
        """Test validation with nested field paths."""
        config_data = {
            "flow": {
                "settings": {
                    "model_group": "openai_models"
                }
            }
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        typehint_data = {
            "field_typehint": {
                "flow.settings.model_group": "MODEL_GROUP"
            }
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        global_config = {
            "model_groups": {
                "openai_models": {"provider": "openai"}
            }
        }

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, global_config
        )

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_missing_field_skipped(self, tmp_path: Path):
        """Test that missing fields in config are skipped during validation."""
        config_data = {"other_field": "value"}
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        typehint_data = {
            "field_typehint": {"missing_field": "STRING"}
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, {}
        )

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_invalid_typehint_definition(self, tmp_path: Path):
        """Test validation fails with invalid typehint definition."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("")

        # Invalid typehint type
        typehint_data = {
            "field_typehint": {"field": "INVALID_TYPE"}
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, {}
        )

        assert is_valid is False
        assert len(errors) == 1
        assert "Invalid typehint" in errors[0]


class TestValidateFlowConfigIntegration:
    """Integration tests for validate_flow_config."""

    def test_full_validation_workflow(self, tmp_path: Path):
        """Test complete validation workflow with multiple fields."""
        # Create comprehensive config.yaml
        config_data = {
            "flow_name": "test_flow",
            "timeout": 60,
            "enabled": True,
            "model_group": "anthropic_models",
            "steps": ["step1", "step2"],
            "params": {"key": "value"},
            "custom_field": "custom_value"
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        # Create comprehensive typehint
        typehint_data = {
            "field_typehint": {
                "flow_name": "STRING",
                "timeout": "INTEGER",
                "enabled": "BOOLEAN",
                "model_group": "MODEL_GROUP",
                "steps": "LIST",
                "params": "DICT"
            }
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        global_config = {
            "default_model_group": "openai_models",
            "model_groups": {
                "openai_models": {"provider": "openai"},
                "anthropic_models": {"provider": "anthropic"}
            }
        }

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, global_config
        )

        assert is_valid is True
        assert len(errors) == 0
        assert config.flow_name == "test_flow"  # type: ignore
        assert config.timeout == 60  # type: ignore
        assert config.enabled is True  # type: ignore
        assert config.model_group == "anthropic_models"  # type: ignore

    def test_multiple_errors_collected(self, tmp_path: Path):
        """Test that multiple validation errors are collected."""
        config_data = {
            "flow_name": 123,  # Should be STRING
            "timeout": "invalid",  # Should be INTEGER
            "model_group": "nonexistent"  # Invalid MODEL_GROUP
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        typehint_data = {
            "field_typehint": {
                "flow_name": "STRING",
                "timeout": "INTEGER",
                "model_group": "MODEL_GROUP"
            }
        }
        typehint_file = tmp_path / "config.typehint.yaml"
        typehint_file.write_text(yaml.dump(typehint_data))

        global_config = {
            "model_groups": {
                "openai_models": {"provider": "openai"}
            }
        }

        is_valid, config, errors, warnings = validate_flow_config(
            tmp_path, global_config
        )

        assert is_valid is False
        assert len(errors) >= 2  # At least 2 type errors
        # MODEL_GROUP error might be caught first
