"""Typehint validation models for flow configuration."""
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict


class TypeHintType(str, Enum):
    """支持的类型提示枚举."""
    MODEL_GROUP = "MODEL_GROUP"
    STRING = "STRING"
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"
    LIST = "LIST"
    DICT = "DICT"


class TypeHintDefinition(BaseModel):
    """Typehint 定义：字段路径 -> 类型."""
    model_config = ConfigDict(extra="forbid")
    
    field_typehint: Dict[str, str] = Field(
        default_factory=dict,
        description="字段路径到类型的映射"
    )
    
    @field_validator("field_typehint")
    @classmethod
    def validate_typehint(cls, v: Dict[str, str]) -> Dict[str, TypeHintType]:
        """验证 typehint 值是否为支持的类型."""
        valid_types = {t.value for t in TypeHintType}
        for path, type_str in v.items():
            if type_str not in valid_types:
                raise ValueError(
                    f"Invalid type '{type_str}' for field '{path}'. "
                    f"Valid types: {valid_types}"
                )
        # Convert string values to TypeHintType enums
        validated_dict = {}
        for path, type_str in v.items():
            validated_dict[path] = TypeHintType(type_str)
        return validated_dict


class TypeHintValidator:
    """
    配置 typehint 验证器。
    
    验证 flow 配置符合 typehint 定义，可以引用全局配置。
    """
    
    def __init__(
        self,
        typehint_def: TypeHintDefinition,
        flow_config: Dict[str, Any],
        global_config: Optional[Dict[str, Any]] = None
    ):
        """
        Args:
            typehint_def: typehint 定义
            flow_config: flow 的配置
            global_config: 全局配置（用于验证 MODEL_GROUP 等引用）
        """
        self.typehint_def = typehint_def
        self.flow_config = flow_config
        self.global_config = global_config or {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self) -> bool:
        """
        验证 flow 配置符合 typehint 定义。

        Returns:
            bool: 验证是否通过
        """
        self.errors = []
        self.warnings = []
        
        for field_path, expected_type in self.typehint_def.field_typehint.items():
            # 获取字段值（支持 .path.to.field 格式）
            field_value = self._get_field_value(self.flow_config, field_path)
            
            if field_value is None:
                # 字段不存在，跳过（可选字段）
                continue
            
            # 验证类型
            if expected_type == TypeHintType.MODEL_GROUP:
                self._validate_model_group(field_value, field_path)
            elif expected_type == TypeHintType.STRING:
                if not isinstance(field_value, str):
                    self.errors.append(
                        f"Field '{field_path}' must be a string, got {type(field_value).__name__}"
                    )
            elif expected_type == TypeHintType.INTEGER:
                if not isinstance(field_value, int):
                    self.errors.append(
                        f"Field '{field_path}' must be an integer, got {type(field_value).__name__}"
                    )
            elif expected_type == TypeHintType.BOOLEAN:
                if not isinstance(field_value, bool):
                    self.errors.append(
                        f"Field '{field_path}' must be a boolean, got {type(field_value).__name__}"
                    )
            elif expected_type == TypeHintType.LIST:
                if not isinstance(field_value, list):
                    self.errors.append(
                        f"Field '{field_path}' must be a list, got {type(field_value).__name__}"
                    )
            elif expected_type == TypeHintType.DICT:
                if not isinstance(field_value, dict):
                    self.errors.append(
                        f"Field '{field_path}' must be a dictionary, got {type(field_value).__name__}"
                    )
        
        return len(self.errors) == 0
    
    def _get_field_value(self, config: Dict[str, Any], field_path: str) -> Optional[Any]:
        """获取嵌套字段的值."""
        path = field_path.lstrip(".")
        if not path:
            return None
        
        keys = path.split(".")
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def _validate_model_group(self, value: Any, field_path: str) -> None:
        """
        验证 MODEL_GROUP 类型。
        
        - 如果值为空字符串，回退到全局配置的 default_model_group
        - 否则检查全局配置的 model_groups 中是否存在
        """
        if value == "" or value is None:
            # 空值，回退到全局配置的默认值
            if "default_model_group" not in self.global_config:
                self.errors.append(
                    f"Field '{field_path}' is empty but no 'default_model_group' defined in global config"
                )
            else:
                self.warnings.append(
                    f"Field '{field_path}' is empty, using global default_model_group: "
                    f"'{self.global_config['default_model_group']}'"
                )
            return
        
        # 检查全局配置的 model_groups
        model_groups = self.global_config.get("model_groups", {})
        if value not in model_groups:
            self.errors.append(
                f"Field '{field_path}' references non-existent model group '{value}'. "
                f"Available groups in global config: {list(model_groups.keys())}"
            )
    
    def get_errors(self) -> List[str]:
        """获取所有错误."""
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """获取所有警告."""
        return self.warnings