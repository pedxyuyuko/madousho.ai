# Flow 插件加载器实现

## TL;DR

> **Quick Summary**: 实现 flow 插件加载器，自动扫描 `plugins/flows/` 目录，通过继承 `FlowBase` 类的模式实例化 flow，验证 flow 配置（独立于全局配置），然后注册到全局注册表。
> 
> **Deliverables**:
> - `src/madousho/flow/base.py` - FlowBase 基类定义
> - `src/madousho/flow/loader.py` - 插件加载器核心逻辑
> - `src/madousho/flow/registry.py` - 全局 flow 注册表
> - `src/madousho/flow/models.py` - 插件相关的 Pydantic 模型
> - `examples/example_flows/config.typehint.yaml` - 示例 typehint
> - `examples/example_flows/src/main.py` - 示例 flow（继承 FlowBase）
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Base Class → Models → Registry → Loader → Integration

---

## Context

### Original Request
用户已经创建了 flow 示例目录 (`examples/example_flows/`) 并软链接到 `plugins/flows/`，需要实现一个针对 flow 的插件加载器。

### Interview Summary
**Key Discussions**:
- **加载时机**: 启动时自动扫描 `plugins/flows/` 目录
- **插件结构**: 标准 Python 包结构（`src/main.py` 作为注册入口）
- **Flow 定义方式**: 每个 flow 的 main.py 继承框架的 `FlowBase` 类，框架实例化这个 class 作为 flow 实例
- **核心职责**: 
  1. 读取并验证 `config.typehint.yaml`（如果存在）
  2. 读取并验证 flow 的 `config.yaml`（独立于全局配置）
  3. 验证 MODEL_GROUP 在**全局配置**中存在
  4. 验证依赖的 tools/mcps 已安装
  5. 实例化 flow 类并注册
- **错误处理**: 混合模式 - 加载成功的 flow，但报告所有错误

**关键设计决策**:
- **配置分离**: flow 的 config.yaml 是 flow 自己的配置，与全局 madousho.yaml 分开
- **验证流程**: flow 配置验证时，需要引用全局配置来验证 MODEL_GROUP 等引用
- **实例化模式**: 框架加载 flow 类 → 实例化 → 调用 flow 的生命周期方法

---

## Work Objectives

### Core Objective
实现 flow 插件加载器，支持自动发现、flow 配置验证（独立但可引用全局配置）、依赖检查和 flow 实例化注册。

### Concrete Deliverables
- `src/madousho/flow/base.py` - FlowBase 基类
- `src/madousho/flow/loader.py` - 插件加载器
- `src/madousho/flow/registry.py` - flow 注册表
- `src/madousho/flow/models.py` - 插件模型
- `src/madousho/config/typehint_models.py` - Typehint 模型
- `examples/example_flows/config.typehint.yaml` - 示例 typehint
- `examples/example_flows/src/main.py` - 示例 flow 类

### Definition of Done
- [ ] `madousho run` 命令能自动加载 `plugins/flows/` 下的所有 flow
- [ ] flow 配置独立加载，验证时可引用全局配置
- [ ] 配置验证失败时有清晰的错误报告
- [ ] 通过验证的 flow 被实例化并注册到全局注册表

### Must Have
- FlowBase 基类定义标准接口
- flow 配置独立于全局配置
- 支持 `config.typehint.yaml` 定义配置类型
- 支持 `MODEL_GROUP` 类型验证（引用全局配置）
- 支持依赖的 tools/mcps 验证
- 混合错误处理模式

### Must NOT Have (Guardrails)
- 不修改现有的全局配置加载逻辑（保持向后兼容）
- 不强制要求 flow 插件必须有 `config.typehint.yaml`
- 不自动安装缺失的依赖（只报告错误）
- 不将 flow 配置合并到全局配置（保持分离）

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: YES (pytest)
- **Automated tests**: YES (TDD)
- **Framework**: pytest
- **If TDD**: 每个任务遵循 RED-GREEN-REFACTOR

### QA Policy
每个任务必须包含 agent-executed QA 场景：
- **配置验证**: 使用 pytest 运行测试验证
- **Flow 加载**: 创建测试 flow 并验证实例化
- **错误处理**: 构造错误配置验证错误报告

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - FlowBase + 模型 + 注册表):
├── Task 1: 定义 FlowBase 基类 [deep]
├── Task 2: 创建插件相关的 Pydantic 模型 [quick]
├── Task 3: 创建 typehint 验证模型 [quick]
├── Task 4: 实现全局 flow 注册表 [quick]
├── Task 5: 创建示例 flow 的 config.typehint.yaml [quick]
└── Task 6: 创建示例 flow 的 src/main.py（继承 FlowBase）[quick]

Wave 2 (After Wave 1 - 加载器核心 + 集成):
├── Task 7: 实现 flow 配置验证逻辑 [deep]
├── Task 8: 实现依赖验证逻辑 [unspecified-high]
├── Task 9: 实现 flow 加载器核心（实例化 flow 类）[deep]
├── Task 10: 集成到 CLI 启动流程 [quick]
└── Task 11: 端到端测试 + 错误报告 [deep]

Wave FINAL (After ALL tasks - 独立 review):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)

Critical Path: Task 1 → Task 7/8 → Task 9 → Task 10 → Task 11
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 6 (Wave 1)
```

### Dependency Matrix

- **1-6**: — — 7-9, 1
- **7**: 1, 3 — 9, 2
- **8**: 2 — 9, 2
- **9**: 1, 4, 7, 8 — 10, 2
- **10**: 9 — 11, 2
- **11**: 10 — FINAL, 3

### Agent Dispatch Summary

- **1**: **6** — T1 → `deep`, T2-T6 → `quick`
- **2**: **5** — T7 → `deep`, T8 → `unspecified-high`, T9 → `deep`, T10 → `quick`, T11 → `deep`
- **FINAL**: **4** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## Implementation Guide

### Task 1: FlowBase 基类 - 详细实现（已根据用户反馈更新）

**设计思路（用户确认）**:
- `FlowBase` 是每个 flow 必须继承的基类
- **唯一的抽象方法**: `run()` - flow 只负责执行
- **框架负责验证** - 不在 FlowBase 中定义 validate_config()
- **元数据从 pyproject.toml 读取** - 不在 FlowBase 中定义 get_metadata()
- **生命周期钩子** - on_start(), on_complete(), on_error() 可选覆盖

**src/madousho/flow/base.py 完整实现**:

```python
"""Flow base class - All flows must inherit from this."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class FlowBase(ABC):
    """
    Flow 基类 - 所有 flow 插件必须继承此类。
    
    Usage:
        class MyFlow(FlowBase):
            def run(self, **kwargs) -> Any:
                # 执行 flow 逻辑
                pass
    
    框架加载流程:
        1. 导入 flow 类的 src/main.py
        2. 找到继承 FlowBase 的类
        3. 实例化：flow_instance = FlowClass(flow_config, global_config)
        4. 框架验证配置（在 __init__ 之前）
        5. 注册到全局注册表
        6. 执行时调用 flow_instance.run()
    """
    
    def __init__(
        self,
        flow_config: Dict[str, Any],
        global_config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化 flow 实例。
        
        Args:
            flow_config: flow 自己的配置（来自 config.yaml）
            global_config: 全局配置（来自 madousho.yaml，用于 MODEL_GROUP 等验证）
        
        Note:
            配置验证由框架在实例化之前完成，__init__ 只负责赋值。
        """
        self.flow_config = flow_config
        self.global_config = global_config or {}
    
    @abstractmethod
    def run(self, **kwargs) -> Any:
        """
        执行 flow 逻辑。
        
        Args:
            **kwargs: 运行时参数
        
        Returns:
            flow 执行结果
        """
        pass
    
    def on_start(self) -> None:
        """
        flow 启动前的钩子（可选覆盖）。
        
        在 run() 被调用之前执行，可用于初始化资源、记录日志等。
        """
        pass
    
    def on_complete(self, result: Any) -> None:
        """
        flow 完成后的钩子（可选覆盖）。
        
        Args:
            result: flow 执行结果
        
        在 run() 成功返回后执行，可用于清理资源、记录结果等。
        """
        pass
    
    def on_error(self, error: Exception) -> None:
        """
        flow 出错时的钩子（可选覆盖）。
        
        Args:
            error: 抛出的异常
        
        在 run() 抛出异常后执行，可用于错误处理、记录日志等。
        此钩子不会重新抛出异常，仅用于清理和记录。
        """
        pass
```
    
    def on_start(self) -> None:
        """
        flow 启动前的钩子（可选覆盖）。
        """
        pass
    
    def on_complete(self, result: Any) -> None:
        """
        flow 完成后的钩子（可选覆盖）。
        
        Args:
            result: flow 执行结果
        """
        pass
    
    def on_error(self, error: Exception) -> None:
        """
        flow 出错时的钩子（可选覆盖）。
        
        Args:
            error: 抛出的异常
        """
        pass

# Flow 类获取 - 框架从模块的 FlowClass 变量直接读取（用户确认设计）
def get_flow_class(module: Any) -> Type[FlowBase]:
    """
    从模块中获取 FlowClass 变量。
    
    Flow 插件的 src/main.py 必须导出 FlowClass 变量：
    
    Example:
        from madousho.flow.base import FlowBase
        
        class MyFlow(FlowBase):
            def run(self, **kwargs):
                pass
        
        FlowClass = MyFlow  # 必须导出
    
    Args:
        module: 导入的模块（src/main.py）
    
    Returns:
        FlowBase 的子类
    
    Raises:
        ValueError: 如果 FlowClass 不存在或不是 FlowBase 子类
    """
    if not hasattr(module, "FlowClass"):
        raise ValueError(
            f"Module {module} does not export 'FlowClass'. "
            "Please define: FlowClass = YourFlowClassName"
        )
    
    flow_class = getattr(module, "FlowClass")
    
    if not (isinstance(flow_class, type) and issubclass(flow_class, FlowBase)):
        raise ValueError(
            f"FlowClass in {module} must be a subclass of FlowBase, "
            f"got {type(flow_class)}"
        )
    
    return flow_class
```

**tests/flow/test_base.py 测试示例**:

```python
"""Tests for FlowBase class."""
import pytest
from madousho.flow.base import FlowBase, FlowMetadata, find_flow_class


class TestFlowMetadata:
    def test_valid_metadata(self):
        """测试有效的元数据."""
        meta = FlowMetadata(name="test_flow", version="1.0.0")
        assert meta.name == "test_flow"
        assert meta.version == "1.0.0"
        assert meta.description is None
    
    def test_metadata_with_all_fields(self):
        """测试完整元数据."""
        meta = FlowMetadata(
            name="test_flow",
            version="1.0.0",
            description="Test flow",
            author="Test Author",
            config_schema={"type": "object"}
        )
        assert meta.description == "Test flow"
        assert meta.author == "Test Author"


class MockFlow(FlowBase):
    """测试用的 mock flow."""
    
    def get_metadata(self) -> FlowMetadata:
        return FlowMetadata(name="mock_flow", version="1.0.0")
    
    def validate_config(self, config):
        if "required_field" not in config:
            raise ValueError("Missing required_field")
    
    def run(self, **kwargs):
        return "mock_result"


class TestFlowBase:
    def test_flow_initialization(self):
        """测试 flow 实例化."""
        config = {"required_field": "value"}
        flow = MockFlow(flow_config=config)
        assert flow.flow_config == config
        assert flow.global_config == {}
    
    def test_flow_with_global_config(self):
        """测试带全局配置的 flow."""
        config = {"required_field": "value"}
        global_config = {"api": {"port": 8000}}
        flow = MockFlow(flow_config=config, global_config=global_config)
        assert flow.global_config == global_config
    
    def test_flow_validation_failure(self):
        """测试配置验证失败."""
        config = {}  # 缺少 required_field
        with pytest.raises(ValueError, match="Missing required_field"):
            MockFlow(flow_config=config)
    
    def test_flow_run(self):
        """测试 flow 执行."""
        config = {"required_field": "value"}
        flow = MockFlow(flow_config=config)
        result = flow.run()
        assert result == "mock_result"
    
    def test_lifecycle_hooks(self):
        """测试生命周期钩子."""
        config = {"required_field": "value"}
        flow = MockFlow(flow_config=config)
        
        # 这些钩子不应该抛出异常
        flow.on_start()
        flow.on_complete("result")
        flow.on_error(Exception("test"))


class TestFindFlowClass:
    def test_find_single_flow_class(self):
        """测试找到单个 flow 类."""
        class TestModule:
            MyFlow = MockFlow
        
        flow_class = find_flow_class(TestModule())
        assert flow_class is MockFlow
    
    def test_no_flow_class(self):
        """测试没有找到 flow 类."""
        class TestModule:
            pass
        
        with pytest.raises(ValueError, match="No FlowBase subclass found"):
            find_flow_class(TestModule())
    
    def test_multiple_flow_classes(self):
        """测试找到多个 flow 类."""
        class TestModule:
            Flow1 = MockFlow
            
            class Flow2(FlowBase):
                def get_metadata(self): pass
                def validate_config(self, config): pass
                def run(self, **kwargs): pass
        
        with pytest.raises(ValueError, match="Multiple FlowBase subclasses found"):
            find_flow_class(TestModule())
```

---

### Task 2: Plugin Models - 详细实现（已根据用户反馈更新）

**关键变更**:
- 添加 `FlowPluginMetadata` 模型 - 从 pyproject.toml 读取元数据
- 保留 `FlowPluginConfig` - flow 自己的 config.yaml
- 保留 `FlowPlugin` - 已加载插件的完整信息
- 保留 `PluginLoadResult` - 加载结果
- **移除 `PluginDependency`** - 暂不支持 tools/mcps 依赖验证

**src/madousho/flow/models.py 完整实现**:

```python
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
```

---

### Task 3: Typehint Models - 详细实现

**src/madousho/config/typehint_models.py 完整实现**:

```python
"""Typehint definition and validation models."""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TypeHintType(str):
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
    
    field_typehint: Dict[str, TypeHintType] = Field(
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
        return v


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
```

---

### Task 4: Flow Registry - 详细实现

**src/madousho/flow/registry.py 完整实现**:

```python
"""Global flow registry."""
import threading
from typing import Dict, List, Optional, Type, Any
from dataclasses import dataclass
from madousho.flow.base import FlowBase


@dataclass
class FlowInfo:
    """Flow 注册信息."""
    name: str
    flow_class: Type[FlowBase]
    flow_instance: FlowBase
    plugin_name: str
    plugin_path: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class FlowRegistry:
    """
    全局 Flow 注册表（单例模式，线程安全）.
    
    Usage:
        registry = FlowRegistry.get_instance()
        registry.register_flow("my_flow", flow_class, flow_instance, "my_plugin")
        flow_info = registry.get_flow("my_flow")
    """
    
    _instance: Optional["FlowRegistry"] = None
    _lock = threading.Lock()
    
    def __init__(self):
        self._flows: Dict[str, FlowInfo] = {}
        self._lock = threading.Lock()
    
    @classmethod
    def get_instance(cls) -> "FlowRegistry":
        """获取单例实例."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """重置单例（用于测试）."""
        with cls._lock:
            cls._instance = None
    
    def register_flow(
        self,
        name: str,
        flow_class: Type[FlowBase],
        flow_instance: FlowBase,
        plugin_name: str,
        plugin_path: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        注册一个 flow。
        
        Args:
            name: Flow 名称
            flow_class: FlowBase 子类
            flow_instance: FlowBase 实例
            plugin_name: 插件名称
            plugin_path: 插件路径
            description: Flow 描述
            metadata: 额外元数据
        
        Raises:
            ValueError: 如果 flow 名称已存在
        """
        with self._lock:
            if name in self._flows:
                raise ValueError(f"Flow '{name}' is already registered")
            
            self._flows[name] = FlowInfo(
                name=name,
                flow_class=flow_class,
                flow_instance=flow_instance,
                plugin_name=plugin_name,
                plugin_path=plugin_path,
                description=description,
                metadata=metadata or {}
            )
    
    def get_flow(self, name: str) -> FlowInfo:
        """获取已注册的 flow."""
        with self._lock:
            if name not in self._flows:
                raise KeyError(f"Flow '{name}' not found. Available: {list(self._flows.keys())}")
            return self._flows[name]
    
    def list_flows(self) -> List[FlowInfo]:
        """列出所有已注册的 flow."""
        with self._lock:
            return list(self._flows.values())
    
    def unregister_flow(self, name: str) -> None:
        """注销一个 flow（用于错误处理）."""
        with self._lock:
            if name not in self._flows:
                raise KeyError(f"Flow '{name}' not found")
            del self._flows[name]
    
    def clear(self) -> None:
        """清空所有注册（用于测试）."""
        with self._lock:
            self._flows.clear()


# 便捷函数
def get_registry() -> FlowRegistry:
    """获取全局 FlowRegistry 实例."""
    return FlowRegistry.get_instance()
```

---

### Task 7-8: Config & Dependency Validation - 详细实现

**src/madousho/flow/loader.py 部分实现（验证部分）**:

```python
"""Plugin loader with validation."""
import yaml
import tomli
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from madousho.flow.models import (
    FlowPlugin,
    FlowPluginConfig,
    PluginDependency,
    PluginLoadResult,
)
from madousho.config.typehint_models import (
    TypeHintDefinition,
    TypeHintValidator,
)


def load_yaml_file(path: Path) -> Dict[str, Any]:
    """加载 YAML 文件."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_toml_file(path: Path) -> Dict[str, Any]:
    """加载 TOML 文件 (pyproject.toml)."""
    with open(path, "rb") as f:
        return tomli.load(f)


def validate_flow_config(
    plugin_path: Path,
    global_config: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any], List[str], List[str]]:
    """
    验证 flow 配置（独立于全局配置）。
    
    Args:
        plugin_path: 插件根目录
        global_config: 全局配置（用于验证 MODEL_GROUP 等引用）
    
    Returns:
        (success, flow_config, errors, warnings)
    
    注意：flow 配置和全局配置是分开的，验证时 flow 配置可以引用全局配置。
    """
    errors = []
    warnings = []
    
    config_path = plugin_path / "config.yaml"
    typehint_path = plugin_path / "config.typehint.yaml"
    
    # 加载 flow 的 config.yaml
    if not config_path.exists():
        errors.append(f"config.yaml not found in {plugin_path}")
        return False, {}, errors, warnings
    
    try:
        flow_config = load_yaml_file(config_path)
    except yaml.YAMLError as e:
        errors.append(f"Failed to parse config.yaml: {e}")
        return False, {}, errors, warnings
    
    # 如果有 typehint 文件，验证 flow 配置
    if typehint_path.exists():
        try:
            typehint_data = load_yaml_file(typehint_path)
            typehint_def = TypeHintDefinition(**typehint_data)
            
            validator = TypeHintValidator(
                typehint_def=typehint_def,
                flow_config=flow_config,
                global_config=global_config  # 引用全局配置验证 MODEL_GROUP
            )
            is_valid = validator.validate()
            
            errors.extend(validator.get_errors())
            warnings.extend(validator.get_warnings())
            
            if not is_valid:
                return False, flow_config, errors, warnings
        except Exception as e:
            errors.append(f"Failed to validate config against typehint: {e}")
            return False, flow_config, errors, warnings
    
    return True, flow_config, errors, warnings


def validate_dependencies(
    plugin_path: Path,
    installed_tools: List[str],
    installed_mcps: List[str]
) -> Tuple[bool, List[str], List[str]]:
    """
    验证插件依赖。
    
    Args:
        plugin_path: 插件根目录
        installed_tools: 已安装的 tools 列表
        installed_mcps: 已安装的 MCPs 列表
    
    Returns:
        (success, errors, warnings)
    """
    errors = []
    warnings = []
    
    pyproject_path = plugin_path / "pyproject.toml"
    
    if not pyproject_path.exists():
        warnings.append(f"pyproject.toml not found, skipping dependency check")
        return True, errors, warnings
    
    try:
        pyproject = load_toml_file(pyproject_path)
    except Exception as e:
        errors.append(f"Failed to parse pyproject.toml: {e}")
        return False, errors, warnings
    
    # 读取 madousho-ai 配置
    madousho_config = pyproject.get("tool", {}).get("madousho-ai", {})
    dep_tools = madousho_config.get("dependencies-tools", [])
    dep_mcps = madousho_config.get("dependencies-mcps", [])
    
    # 验证 tools
    for tool in dep_tools:
        if tool not in installed_tools:
            errors.append(f"Missing required tool: {tool}")
    
    # 验证 MCPs
    for mcp in dep_mcps:
        if mcp not in installed_mcps:
            errors.append(f"Missing required MCP: {mcp}")
    
    return len(errors) == 0, errors, warnings
```

---

### Task 9: Flow Loader - 详细实现（已根据用户反馈更新）

**关键变更**:
- 移除依赖验证（暂不支持 tools/mcps）
- 使用 `FlowClass` 导出而不是自动查找
- 移除 `get_metadata()` 调用，直接从 pyproject.toml 读取

**src/madousho/flow/loader.py 完整实现（加载部分）**:

```python
import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from madousho.flow.base import FlowBase, get_flow_class
from madousho.flow.models import (
    FlowPlugin,
    FlowPluginMetadata,
    FlowPluginConfig,
    PluginLoadResult
)


def load_plugin(
    plugin_path: Path,
    global_config: Dict[str, Any]
) -> PluginLoadResult:
    """
    加载单个插件。
    
    Args:
        plugin_path: 插件根目录
        global_config: 全局配置（用于验证 MODEL_GROUP）
    
    Returns:
        PluginLoadResult: 加载结果
    """
    all_errors = []
    all_warnings = []
    
    # 1. 验证 flow 配置（独立于全局配置）
    config_valid, flow_config, config_errors, config_warnings = validate_flow_config(
        plugin_path, global_config
    )
    all_errors.extend(config_errors)
    all_warnings.extend(config_warnings)
    
    if not config_valid:
        return PluginLoadResult.failure_result(all_errors, all_warnings)
    
    # 2. 加载 pyproject.toml 获取元数据
    pyproject_path = plugin_path / "pyproject.toml"
    try:
        pyproject = load_toml_file(pyproject_path)
        project_info = pyproject.get("project", {})
        
        metadata = FlowPluginMetadata(
            name=project_info.get("name", plugin_path.name),
            version=project_info.get("version", "0.0.0"),
            description=project_info.get("description"),
            author=project_info.get("authors", [{}])[0].get("name") if project_info.get("authors") else None
        )
    except Exception as e:
        all_errors.append(f"Failed to read pyproject.toml: {e}")
        return PluginLoadResult.failure_result(all_errors, all_warnings)
    
    # 3. 导入 src/main.py
    main_path = plugin_path / "src" / "main.py"
    if not main_path.exists():
        all_errors.append(f"src/main.py not found in {plugin_path}")
        return PluginLoadResult.failure_result(all_errors, all_warnings)
    
    try:
        main_module = import_plugin_main(plugin_path, main_path)
    except Exception as e:
        all_errors.append(f"Failed to import main.py: {e}")
        return PluginLoadResult.failure_result(all_errors, all_warnings)
    
    # 4. 获取 FlowClass（flow 插件必须导出 FlowClass 变量）
    try:
        flow_class = get_flow_class(main_module)
        
        # 实例化 flow（传入 flow 配置和全局配置）
        flow_instance = flow_class(
            flow_config=flow_config,
            global_config=global_config
        )
        
    except Exception as e:
        all_errors.append(f"Failed to instantiate flow: {e}")
        return PluginLoadResult.failure_result(all_errors, all_warnings)
    
    # 5. 创建插件信息
    plugin = FlowPlugin(
        metadata=metadata,
        path=plugin_path,
        config=flow_config,
        flow_class=flow_class,
        flow_instance=flow_instance
        # Note: dependencies 字段暂不添加
    )
    
    return PluginLoadResult.success_result(plugin, all_warnings)
```
        all_errors.append(f"Failed to instantiate flow: {e}")
        return PluginLoadResult.failure_result(all_errors, all_warnings)
    
    # 7. 创建插件对象
    plugin = FlowPlugin(
        name=plugin_name,
        version=plugin_version,
        path=plugin_path,
        config=FlowPluginConfig(**flow_config),
        dependencies=dependencies,
        flow_class=flow_class,
        flow_instance=flow_instance,
    )
    
    return PluginLoadResult.success_result(plugin, all_warnings)


def import_plugin_main(plugin_path: Path, main_path: Path) -> Any:
    """动态导入插件的 main.py."""
    module_name = f"plugin_{plugin_path.name}"
    
    spec = importlib.util.spec_from_file_location(module_name, main_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load spec from {main_path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    return module


def load_all_plugins(
    plugins_dir: Path,
    global_config: Dict[str, Any],
    installed_tools: List[str],
    installed_mcps: List[str]
) -> Tuple[List[FlowPlugin], List[PluginLoadResult]]:
    """
    加载所有插件。
    
    Args:
        plugins_dir: plugins/flows 目录
        global_config: 全局配置
        installed_tools: 已安装的 tools
        installed_mcps: 已安装的 MCPs
    
    Returns:
        (成功加载的插件列表，失败的加载结果列表)
    """
    successful = []
    failed = []
    
    if not plugins_dir.exists():
        return successful, failed
    
    # 扫描所有插件目录
    for item in plugins_dir.iterdir():
        if not item.is_dir():
            continue
        
        # 检查是否有 pyproject.toml
        if not (item / "pyproject.toml").exists():
            continue
        
        result = load_plugin(
            item,
            global_config,
            installed_tools,
            installed_mcps
        )
        
        if result.success and result.plugin:
            successful.append(result.plugin)
            
            # 注册 flow 实例到全局注册表
            metadata = result.plugin.flow_instance.get_metadata()
            from madousho.flow.registry import get_registry
            registry = get_registry()
            
            try:
                registry.register_flow(
                    name=metadata.name,
                    flow_class=result.plugin.flow_class,
                    flow_instance=result.plugin.flow_instance,
                    plugin_name=result.plugin.name,
                    plugin_path=str(result.plugin.path),
                    description=metadata.description,
                    metadata=metadata.model_dump()
                )
            except Exception as e:
                # 注册失败，回滚
                failed.append(PluginLoadResult.failure_result(
                    [f"Failed to register flow '{metadata.name}': {e}"],
                    result.warnings
                ))
                successful.pop()
        else:
            failed.append(result)
    
    return successful, failed
```

---

### Task 10: CLI Integration - 详细实现

**src/madousho/commands/run.py 修改**:

```python
"""Run command - Start the madousho service."""
from madousho.logger import logger
from madousho.flow.loader import load_all_plugins
from pathlib import Path
import typer


def run_cmd(ctx: typer.Context):
    """
    Start the madousho service.
    
    This command loads the global configuration, loads all flow plugins,
    and starts the service.
    """
    config_path = ctx.obj["config_path"]
    verbose = ctx.obj["verbose"]
    
    # Load GLOBAL configuration (madousho.yaml)
    from madousho.config.loader import load_config
    global_config = load_config(str(config_path))
    global_config_dict = global_config.model_dump()
    
    logger.info("Starting madousho service...")
    
    # Load all flow plugins
    # 注意：flow 配置是独立的，每个 flow 有自己的 config.yaml
    # 这里只是传递全局配置用于验证 MODEL_GROUP 等引用
    plugins_dir = Path("plugins/flows")
    
    # TODO: Get installed tools/MCPs from registry
    installed_tools = []  # Placeholder
    installed_mcps = []   # Placeholder
    
    successful, failed = load_all_plugins(
        plugins_dir,
        global_config_dict,  # 传递全局配置（用于验证引用）
        installed_tools,
        installed_mcps
    )
    
    # Report results
    logger.info(f"Loaded {len(successful)} flow plugin(s)")
    
    if verbose:
        for plugin in successful:
            logger.info(
                f"  - {plugin.name} v{plugin.version} at {plugin.path}",
                dependencies=[d.name for d in plugin.dependencies]
            )
        
        # 显示已注册的 flows
        from madousho.flow.registry import get_registry
        registry = get_registry()
        for flow_info in registry.list_flows():
            logger.info(
                f"  Flow: {flow_info.name} (from {flow_info.plugin_name})",
                description=flow_info.description
            )
    
    if failed:
        logger.warning(f"Failed to load {len(failed)} plugin(s):")
        for result in failed:
            for error in result.errors:
                logger.error(f"  - {error}")
            for warning in result.warnings:
                logger.warning(f"  - {warning}")
    
    if verbose:
        logger.info(
            "Global configuration loaded",
            config_path=str(config_path),
            api_host=global_config.api.host,
            api_port=global_config.api.port,
            model_groups=list(global_config.model_groups.keys())
        )
```

---

## TODOs

> Implementation + Test = ONE Task. Never separate.

- [ ] 1. 定义 FlowBase 基类

  **What to do**:
  - 创建 `src/madousho/flow/base.py`
  - 定义 `FlowMetadata` 模型：name, version, description, author
  - 定义 `FlowBase` 抽象基类：`__init__`, `get_metadata`, `validate_config`, `run`
  - 添加生命周期钩子：`on_start`, `on_complete`, `on_error`
  - 实现 `find_flow_class()` 工具函数

  **Must NOT do**:
  - 不包含加载逻辑
  - 不修改现有全局配置

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2-6)
  - **Blocks**: Tasks 7, 9
  - **Blocked By**: None

  **References**:
  - Python `abc` 模块 - 抽象基类
  - `src/madousho/config/models.py` - Pydantic v2 模型定义

  **Acceptance Criteria**:
  - [ ] 测试文件创建：`tests/flow/test_base.py`
  - [ ] `pytest tests/flow/test_base.py` → PASS

  **QA Scenarios**:
  ```
  Scenario: 验证 FlowBase 子类可以实例化
    Tool: Bash (pytest)
    Preconditions: 测试文件已创建
    Steps:
      1. 运行 pytest tests/flow/test_base.py::TestFlowBase::test_flow_initialization -v
      2. 验证测试通过
    Expected Result: 测试通过
    Evidence: .sisyphus/evidence/task-1-flow-init.png

  Scenario: 验证配置验证失败
    Tool: Bash (pytest)
    Preconditions: MockFlow 需要 required_field
    Steps:
      1. 运行 pytest tests/flow/test_base.py::TestFlowBase::test_flow_validation_failure -v
      2. 验证抛出 ValueError
    Expected Result: 测试通过，验证异常被正确抛出
    Evidence: .sisyphus/evidence/task-1-validation-fail.png

  Scenario: 验证 find_flow_class 找到正确的类
    Tool: Bash (pytest)
    Preconditions: 测试模块包含 FlowBase 子类
    Steps:
      1. 运行 pytest tests/flow/test_base.py::TestFindFlowClass::test_find_single_flow_class -v
      2. 验证返回正确的类
    Expected Result: 测试通过
    Evidence: .sisyphus/evidence/task-1-find-class.png
  ```

  **Commit**: YES (groups with 2-6)
  - Message: `feat(flow): add FlowBase abstract class and metadata model`
  - Files: `src/madousho/flow/base.py`, `tests/flow/test_base.py`
  - Pre-commit: `pytest tests/flow/test_base.py`

- [ ] 2. 创建插件相关的 Pydantic 模型

  **What to do**:
  - 创建 `src/madousho/flow/models.py`
  - 定义 `PluginDependency` 模型
  - 定义 `FlowPluginConfig` 模型（允许 extra 字段）
  - 定义 `FlowPlugin` 模型
  - 定义 `PluginLoadResult` 模型

  **Must NOT do**:
  - 不包含加载逻辑

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3-6)
  - **Blocks**: Tasks 7, 9
  - **Blocked By**: None

  **References**:
  - `src/madousho/config/models.py:6-40` - Pydantic v2 模型定义

  **Acceptance Criteria**:
  - [ ] 测试文件创建：`tests/flow/test_models.py`
  - [ ] `pytest tests/flow/test_models.py` → PASS

  **Commit**: YES (groups with 1, 3-6)
  - Message: `feat(flow): add plugin pydantic models`
  - Files: `src/madousho/flow/models.py`, `tests/flow/test_models.py`
  - Pre-commit: `pytest tests/flow/test_models.py`

- [ ] 3. 创建 typehint 验证模型

  **What to do**:
  - 创建 `src/madousho/config/typehint_models.py`
  - 定义 `TypeHintType` 枚举
  - 定义 `TypeHintDefinition` 模型
  - 定义 `TypeHintValidator` 类（支持引用全局配置）

  **Must NOT do**:
  - 不包含 YAML 加载逻辑

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-2, 4-6)
  - **Blocks**: Tasks 7, 9
  - **Blocked By**: None

  **References**:
  - `src/madousho/config/models.py:15-20` - field_validator 用法

  **Acceptance Criteria**:
  - [ ] 测试文件创建：`tests/config/test_typehint_models.py`
  - [ ] `pytest tests/config/test_typehint_models.py` → PASS

  **Commit**: YES (groups with 1-2, 4-6)
  - Message: `feat(config): add typehint definition and validator models`
  - Files: `src/madousho/config/typehint_models.py`, `tests/config/test_typehint_models.py`
  - Pre-commit: `pytest tests/config/test_typehint_models.py`

- [ ] 4. 实现全局 flow 注册表

  **What to do**:
  - 创建 `src/madousho/flow/registry.py`
  - 定义 `FlowInfo` dataclass
  - 实现 `FlowRegistry` 单例类（线程安全）
  - 实现便捷函数 `get_registry()`

  **Must NOT do**:
  - 不包含加载逻辑

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-3, 5-6)
  - **Blocks**: Tasks 9
  - **Blocked By**: None

  **References**:
  - `src/madousho/cli.py:13` - Typer app 注册模式

  **Acceptance Criteria**:
  - [ ] 测试文件创建：`tests/flow/test_registry.py`
  - [ ] `pytest tests/flow/test_registry.py` → PASS

  **Commit**: YES (groups with 1-3, 5-6)
  - Message: `feat(flow): add global flow registry with thread safety`
  - Files: `src/madousho/flow/registry.py`, `tests/flow/test_registry.py`
  - Pre-commit: `pytest tests/flow/test_registry.py`

- [ ] 5. 创建示例 flow 的 config.typehint.yaml

  **What to do**:
  - 创建 `examples/example_flows/config.typehint.yaml`
  - 定义 `field_typehint` 结构
  - 添加示例：`.example_use_model_group`: `MODEL_GROUP`

  **Must NOT do**:
  - 不修改 config.yaml

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-4, 6)
  - **Blocks**: Tasks 7, 9
  - **Blocked By**: None

  **References**:
  - `examples/example_flows/config.yaml:9-12` - typehint 注释

  **Acceptance Criteria**:
  - [ ] YAML 文件语法正确

  **Commit**: YES (groups with 1-4, 6)
  - Message: `docs(example): add config.typehint.yaml example`
  - Files: `examples/example_flows/config.typehint.yaml`
  - Pre-commit: N/A

- [ ] 6. 创建示例 flow 的 src/main.py（继承 FlowBase + 导出 FlowClass）

  **What to do**:
  - 创建 `examples/example_flows/src/main.py`
  - 定义 `ExampleFlow(FlowBase)` 类
  - **只实现 `run()` 方法**（唯一的抽象方法）
  - 可选实现 `on_start()`, `on_complete()`, `on_error()` 钩子
  - **必须导出**: `FlowClass = ExampleFlow`
  - 添加文档字符串

  **Must NOT do**:
  - 不实现 `get_metadata()`（元数据从 pyproject.toml 读取）
  - 不实现 `validate_config()`（框架负责验证）
  - 不实现真实的 flow 逻辑（示例骨架）

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-5)
  - **Blocks**: Tasks 9
  - **Blocked By**: None

  **References**:
  - `src/madousho/flow/base.py` (Task 1) - FlowBase 接口
  - `examples/example_flows/pyproject.toml` - 元数据来源

  **Acceptance Criteria**:
  - [ ] main.py 可以被导入
  - [ ] 包含继承 FlowBase 的类
  - [ ] 只实现 `run()` 方法（`get_metadata` 和 `validate_config` 不存在）
  - [ ] 导出 `FlowClass = ExampleFlow`
  - [ ] 可以实例化：`ExampleFlow(flow_config={}, global_config={})`

  **Commit**: YES (groups with 1-5)
  - Message: `feat(example): add example flow class with FlowClass export`
  - Files: `examples/example_flows/src/main.py`
  - Pre-commit: N/A

- [ ] 7. 实现 flow 配置验证逻辑

  **What to do**:
  - 在 `src/madousho/flow/loader.py` 中实现 `validate_flow_config()`
  - 读取 flow 的 `config.yaml`（独立配置）
  - 读取 `config.typehint.yaml`（如果存在）
  - 使用 `TypeHintValidator` 验证（可引用全局配置）

  **Must NOT do**:
  - 不验证依赖
  - 不加载 flow

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 8)
  - **Parallel Group**: Wave 2 (with Task 8)
  - **Blocks**: Task 9
  - **Blocked By**: Tasks 1, 3

  **References**:
  - `src/madousho/config/loader.py:116-145` - config 加载逻辑
  - `src/madousho/config/typehint_models.py` (Task 3) - TypeHintValidator

  **Acceptance Criteria**:
  - [ ] 测试文件创建：`tests/flow/test_config_validation.py`
  - [ ] `pytest tests/flow/test_config_validation.py` → PASS

  **Commit**: YES (groups with 8)
  - Message: `feat(flow): implement flow config validation with typehint support`
  - Files: `src/madousho/flow/loader.py`, `tests/flow/test_config_validation.py`
  - Pre-commit: `pytest tests/flow/test_config_validation.py`

- [ ] 8. 实现依赖验证逻辑

  **What to do**:
  - 在 `src/madousho/flow/loader.py` 中实现 `validate_dependencies()`
  - 读取 `pyproject.toml` 中的依赖
  - 验证 tools/mcps 已安装

  **Must NOT do**:
  - 不自动安装缺失的依赖

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 7)
  - **Parallel Group**: Wave 2 (with Task 7)
  - **Blocks**: Task 9
  - **Blocked By**: Task 2

  **References**:
  - `examples/example_flows/pyproject.toml:33-37` - 依赖声明格式

  **Acceptance Criteria**:
  - [ ] 测试文件创建：`tests/flow/test_dependency_validation.py`
  - [ ] `pytest tests/flow/test_dependency_validation.py` → PASS

  **Commit**: YES (groups with 7)
  - Message: `feat(flow): implement dependency validation for tools/mcps`
  - Files: `src/madousho/flow/loader.py`, `tests/flow/test_dependency_validation.py`
  - Pre-commit: `pytest tests/flow/test_dependency_validation.py`

- [ ] 9. 实现 flow 加载器核心（实例化 flow 类）

  **What to do**:
  - 在 `src/madousho/flow/loader.py` 中实现 `load_plugin()`
  - 扫描 `plugins/flows/` 目录
  - 对每个插件：
    1. 调用 `validate_flow_config()`
    2. 调用 `validate_dependencies()`
    3. 导入 `src/main.py`
    4. 使用 `find_flow_class()` 找到 FlowBase 子类
    5. 实例化 flow 类
    6. 注册到全局注册表

  **Must NOT do**:
  - 不修改注册表实现
  - 不修改 CLI 启动流程

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (depends on Tasks 7, 8)
  - **Blocks**: Tasks 10, 11
  - **Blocked By**: Tasks 1, 4, 7, 8

  **References**:
  - `src/madousho/flow/loader.py` (Tasks 7-8) - 验证函数
  - `src/madousho/flow/base.py` (Task 1) - find_flow_class
  - `src/madousho/flow/registry.py` (Task 4) - 注册表 API

  **Acceptance Criteria**:
  - [ ] 测试文件创建：`tests/flow/test_loader.py`
  - [ ] `pytest tests/flow/test_loader.py` → PASS

  **Commit**: YES (groups with 10)
  - Message: `feat(flow): implement plugin loader with flow instantiation`
  - Files: `src/madousho/flow/loader.py`, `tests/flow/test_loader.py`
  - Pre-commit: `pytest tests/flow/test_loader.py`

- [ ] 10. 集成到 CLI 启动流程

  **What to do**:
  - 修改 `src/madousho/commands/run.py` 的 `run_cmd()`
  - 加载全局配置后，调用 `load_all_plugins()`
  - 打印加载报告
  - verbose 模式显示 flow 详情

  **Must NOT do**:
  - 不修改加载器逻辑
  - 不合并 flow 配置到全局配置

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (depends on Task 9)
  - **Blocks**: Task 11
  - **Blocked By**: Task 9

  **References**:
  - `src/madousho/commands/run.py:8-25` - 现有 run_cmd 实现

  **Acceptance Criteria**:
  - [ ] `madousho run` 能自动加载 flow 插件
  - [ ] 输出包含插件加载报告

  **Commit**: YES (groups with 9)
  - Message: `feat(cli): integrate flow loader into run command`
  - Files: `src/madousho/commands/run.py`
  - Pre-commit: `pytest tests/flow/test_integration.py`

- [ ] 11. 端到端测试 + 错误报告

  **What to do**:
  - 创建集成测试 `tests/flow/test_integration.py`
  - 测试完整的加载流程
  - 测试混合模式错误报告

  **Must NOT do**:
  - 不修改实现代码

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (depends on Task 10)
  - **Blocks**: FINAL
  - **Blocked By**: Task 10

  **Acceptance Criteria**:
  - [ ] 测试文件创建：`tests/flow/test_integration.py`
  - [ ] `pytest tests/flow/test_integration.py` → PASS
  - [ ] 测试覆盖率 ≥90%

  **Commit**: YES (groups with 9-10)
  - Message: `test(flow): add comprehensive integration tests`
  - Files: `tests/flow/test_integration.py`
  - Pre-commit: `pytest tests/flow/ --cov=madousho/flow --cov-fail-under=90`

---

## Final Verification Wave

> 4 review agents run in PARALLEL. ALL must APPROVE.

- [ ] F1. **Plan Compliance Audit** — `oracle`
- [ ] F2. **Code Quality Review** — `unspecified-high`
- [ ] F3. **Real Manual QA** — `unspecified-high`
- [ ] F4. **Scope Fidelity Check** — `deep`

---

## Commit Strategy

- **1-6**: `feat(flow): add FlowBase, models, registry, and example` — base.py, models.py, registry.py, typehint_models.py, example_flows/*
- **7-8**: `feat(flow): implement config and dependency validation` — loader.py, test_*.py
- **9-10**: `feat(flow): implement loader and integrate with CLI` — loader.py, run.py, test_loader.py
- **11**: `test(flow): add comprehensive integration tests` — test_integration.py
- **FINAL**: `chore: final verification and cleanup`

---

## Success Criteria

### Verification Commands
```bash
# All flow tests pass
pytest tests/flow/ -v --cov=madousho/flow --cov-fail-under=90

# CLI loads flows successfully
madousho run

# Verbose mode shows flow details
madousho run --verbose
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass (90% coverage)
- [ ] Evidence files captured for all QA scenarios
- [ ] Final verification wave APPROVE
