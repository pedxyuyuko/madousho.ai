"""Plugin system models."""
from typing import Dict, List, Optional, Any
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field


class FlowPluginMetadata(BaseModel):
    """
    Flow 插件元数据 - 从 pyproject.toml 读取。
    
    框架在加载 flow 插件时，从插件的 pyproject.toml 中提取这些信息，
    而不是要求 flow 类实现 get_metadata() 方法。
    """
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., description="插件名称（来自 project.name）")
    version: str = Field(..., description="插件版本（来自 project.version）")
    description: Optional[str] = Field(None, description="插件描述（来自 project.description）")
    author: Optional[str] = Field(None, description="作者（来自 project.authors[0].name）")


class FlowPluginConfig(BaseModel):
    """
    Flow 插件的 config.yaml 内容。
    
    注意：这是 flow 自己的配置，独立于全局 madousho.yaml。
    验证时可能需要引用全局配置（如 MODEL_GROUP）。
    """
    model_config = ConfigDict(extra="allow")  # 允许 flow 自定义配置项
    
    field_typehint: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="字段类型提示：路径 -> 类型 (e.g., '.example_use_model_group': 'MODEL_GROUP')"
    )


class FlowPlugin(BaseModel):
    """已加载的 Flow 插件信息."""
    model_config = ConfigDict(extra="forbid")
    
    metadata: FlowPluginMetadata = Field(..., description="插件元数据（来自 pyproject.toml）")
    path: Path = Field(..., description="插件根目录路径")
    config: FlowPluginConfig = Field(..., description="插件配置（来自 config.yaml）")
    flow_class: Optional[Any] = Field(None, description="FlowBase 子类")
    flow_instance: Optional[Any] = Field(None, description="FlowBase 实例")
    # Note: dependencies 字段暂不添加，等待 tools/mcps 支持后再实现


class PluginLoadResult(BaseModel):
    """插件加载结果."""
    model_config = ConfigDict(extra="forbid")
    
    success: bool = Field(..., description="是否成功")
    plugin: Optional[FlowPlugin] = Field(None, description="加载的插件信息")
    errors: List[str] = Field(default_factory=list, description="错误列表")
    warnings: List[str] = Field(default_factory=list, description="警告列表")
    
    @classmethod
    def success_result(cls, plugin: FlowPlugin, warnings: Optional[List[str]] = None) -> "PluginLoadResult":
        """创建成功结果."""
        return cls(success=True, plugin=plugin, errors=[], warnings=warnings or [])
    
    @classmethod
    def failure_result(cls, errors: List[str], warnings: Optional[List[str]] = None) -> "PluginLoadResult":
        """创建失败结果."""
        return cls(success=False, plugin=None, errors=errors, warnings=warnings or [])