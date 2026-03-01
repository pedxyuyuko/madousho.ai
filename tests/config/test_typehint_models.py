"""Tests for typehint models."""
import pytest
from src.madousho.config.typehint_models import (
    TypeHintType, 
    TypeHintDefinition, 
    TypeHintValidator
)


class TestTypeHintType:
    """Test TypeHintType enum."""
    
    def test_values(self):
        """Test all enum values."""
        assert TypeHintType.MODEL_GROUP.value == "MODEL_GROUP"
        assert TypeHintType.STRING.value == "STRING"
        assert TypeHintType.INTEGER.value == "INTEGER"
        assert TypeHintType.BOOLEAN.value == "BOOLEAN"
        assert TypeHintType.LIST.value == "LIST"
        assert TypeHintType.DICT.value == "DICT"


class TestTypeHintDefinition:
    """Test TypeHintDefinition model."""
    
    def test_valid_typehint(self):
        """Test valid typehint definition."""
        definition = TypeHintDefinition(
            field_typehint={
                "flow.model_group": "MODEL_GROUP",
                "flow.name": "STRING",
                "flow.timeout": "INTEGER"
            }
        )
        assert len(definition.field_typehint) == 3
        assert definition.field_typehint["flow.model_group"] == TypeHintType.MODEL_GROUP
    
    def test_invalid_typehint_raises_error(self):
        """Test invalid typehint raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            TypeHintDefinition(
                field_typehint={
                    "flow.invalid": "INVALID_TYPE"
                }
            )
        assert "Invalid type 'INVALID_TYPE'" in str(exc_info.value)
        assert "MODEL_GROUP" in str(exc_info.value)


class TestTypeHintValidator:
    """Test TypeHintValidator."""
    
    def test_string_validation_success(self):
        """Test successful string validation."""
        definition = TypeHintDefinition(
            field_typehint={"flow.name": "STRING"}
        )
        flow_config = {"flow": {"name": "test_flow"}}
        
        validator = TypeHintValidator(definition, flow_config)
        result = validator.validate()
        
        assert result is True
        assert len(validator.get_errors()) == 0
    
    def test_string_validation_failure(self):
        """Test string validation failure."""
        definition = TypeHintDefinition(
            field_typehint={"flow.name": "STRING"}
        )
        flow_config = {"flow": {"name": 123}}
        
        validator = TypeHintValidator(definition, flow_config)
        result = validator.validate()
        
        assert result is False
        assert len(validator.get_errors()) == 1
        assert "must be a string" in validator.get_errors()[0]
    
    def test_integer_validation_success(self):
        """Test successful integer validation."""
        definition = TypeHintDefinition(
            field_typehint={"flow.timeout": "INTEGER"}
        )
        flow_config = {"flow": {"timeout": 30}}
        
        validator = TypeHintValidator(definition, flow_config)
        result = validator.validate()
        
        assert result is True
        assert len(validator.get_errors()) == 0
    
    def test_integer_validation_failure(self):
        """Test integer validation failure."""
        definition = TypeHintDefinition(
            field_typehint={"flow.timeout": "INTEGER"}
        )
        flow_config = {"flow": {"timeout": "thirty"}}
        
        validator = TypeHintValidator(definition, flow_config)
        result = validator.validate()
        
        assert result is False
        assert len(validator.get_errors()) == 1
        assert "must be an integer" in validator.get_errors()[0]
    
    def test_boolean_validation_success(self):
        """Test successful boolean validation."""
        definition = TypeHintDefinition(
            field_typehint={"flow.enabled": "BOOLEAN"}
        )
        flow_config = {"flow": {"enabled": True}}
        
        validator = TypeHintValidator(definition, flow_config)
        result = validator.validate()
        
        assert result is True
        assert len(validator.get_errors()) == 0
    
    def test_boolean_validation_failure(self):
        """Test boolean validation failure."""
        definition = TypeHintDefinition(
            field_typehint={"flow.enabled": "BOOLEAN"}
        )
        flow_config = {"flow": {"enabled": "yes"}}
        
        validator = TypeHintValidator(definition, flow_config)
        result = validator.validate()
        
        assert result is False
        assert len(validator.get_errors()) == 1
        assert "must be a boolean" in validator.get_errors()[0]
    
    def test_list_validation_success(self):
        """Test successful list validation."""
        definition = TypeHintDefinition(
            field_typehint={"flow.steps": "LIST"}
        )
        flow_config = {"flow": {"steps": ["step1", "step2"]}}
        
        validator = TypeHintValidator(definition, flow_config)
        result = validator.validate()
        
        assert result is True
        assert len(validator.get_errors()) == 0
    
    def test_list_validation_failure(self):
        """Test list validation failure."""
        definition = TypeHintDefinition(
            field_typehint={"flow.steps": "LIST"}
        )
        flow_config = {"flow": {"steps": "not_a_list"}}
        
        validator = TypeHintValidator(definition, flow_config)
        result = validator.validate()
        
        assert result is False
        assert len(validator.get_errors()) == 1
        assert "must be a list" in validator.get_errors()[0]
    
    def test_dict_validation_success(self):
        """Test successful dict validation."""
        definition = TypeHintDefinition(
            field_typehint={"flow.params": "DICT"}
        )
        flow_config = {"flow": {"params": {"key": "value"}}}
        
        validator = TypeHintValidator(definition, flow_config)
        result = validator.validate()
        
        assert result is True
        assert len(validator.get_errors()) == 0
    
    def test_dict_validation_failure(self):
        """Test dict validation failure."""
        definition = TypeHintDefinition(
            field_typehint={"flow.params": "DICT"}
        )
        flow_config = {"flow": {"params": "not_a_dict"}}
        
        validator = TypeHintValidator(definition, flow_config)
        result = validator.validate()
        
        assert result is False
        assert len(validator.get_errors()) == 1
        assert "must be a dictionary" in validator.get_errors()[0]
    
    def test_model_group_validation_success(self):
        """Test successful model group validation."""
        definition = TypeHintDefinition(
            field_typehint={"flow.model_group": "MODEL_GROUP"}
        )
        flow_config = {"flow": {"model_group": "openai_models"}}
        global_config = {
            "model_groups": {
                "openai_models": {"provider": "openai"},
                "anthropic_models": {"provider": "anthropic"}
            }
        }
        
        validator = TypeHintValidator(definition, flow_config, global_config)
        result = validator.validate()
        
        assert result is True
        assert len(validator.get_errors()) == 0
    
    def test_model_group_validation_failure(self):
        """Test model group validation failure."""
        definition = TypeHintDefinition(
            field_typehint={"flow.model_group": "MODEL_GROUP"}
        )
        flow_config = {"flow": {"model_group": "nonexistent_group"}}
        global_config = {
            "model_groups": {
                "openai_models": {"provider": "openai"},
                "anthropic_models": {"provider": "anthropic"}
            }
        }
        
        validator = TypeHintValidator(definition, flow_config, global_config)
        result = validator.validate()
        
        assert result is False
        assert len(validator.get_errors()) == 1
        assert "references non-existent model group" in validator.get_errors()[0]
    
    def test_model_group_empty_with_default(self):
        """Test model group validation with empty value and global default."""
        definition = TypeHintDefinition(
            field_typehint={"flow.model_group": "MODEL_GROUP"}
        )
        flow_config = {"flow": {"model_group": ""}}
        global_config = {
            "default_model_group": "openai_models",
            "model_groups": {
                "openai_models": {"provider": "openai"},
                "anthropic_models": {"provider": "anthropic"}
            }
        }
        
        validator = TypeHintValidator(definition, flow_config, global_config)
        result = validator.validate()
        
        # Should pass validation but generate a warning
        assert result is True
        assert len(validator.get_errors()) == 0
        assert len(validator.get_warnings()) == 1
        assert "empty, using global default_model_group" in validator.get_warnings()[0]
    
    def test_model_group_empty_without_default(self):
        """Test model group validation with empty value and no global default."""
        definition = TypeHintDefinition(
            field_typehint={"flow.model_group": "MODEL_GROUP"}
        )
        flow_config = {"flow": {"model_group": ""}}
        global_config = {
            "model_groups": {
                "openai_models": {"provider": "openai"},
                "anthropic_models": {"provider": "anthropic"}
            }
        }
        
        validator = TypeHintValidator(definition, flow_config, global_config)
        result = validator.validate()
        
        assert result is False
        assert len(validator.get_errors()) == 1
        assert "no 'default_model_group' defined in global config" in validator.get_errors()[0]
    
    def test_nested_field_access(self):
        """Test accessing deeply nested fields."""
        definition = TypeHintDefinition(
            field_typehint={"flow.settings.model_group": "MODEL_GROUP"}
        )
        flow_config = {"flow": {"settings": {"model_group": "openai_models"}}}
        global_config = {
            "model_groups": {
                "openai_models": {"provider": "openai"}
            }
        }
        
        validator = TypeHintValidator(definition, flow_config, global_config)
        result = validator.validate()
        
        assert result is True
        assert len(validator.get_errors()) == 0
    
    def test_missing_field_skipped(self):
        """Test that missing fields are skipped during validation."""
        definition = TypeHintDefinition(
            field_typehint={"flow.missing_field": "STRING"}
        )
        flow_config = {"flow": {"other_field": "value"}}
        
        validator = TypeHintValidator(definition, flow_config)
        result = validator.validate()
        
        assert result is True
        assert len(validator.get_errors()) == 0
    
    def test_none_global_config(self):
        """Test validator works with None global config."""
        definition = TypeHintDefinition(
            field_typehint={"flow.name": "STRING"}
        )
        flow_config = {"flow": {"name": "test_flow"}}
        
        validator = TypeHintValidator(definition, flow_config, None)
        result = validator.validate()
        
        assert result is True
        assert len(validator.get_errors()) == 0