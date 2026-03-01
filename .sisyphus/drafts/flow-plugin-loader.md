
## Design Update (from User Feedback - FlowBase Review)

**User reviewed base.py pseudo-code and clarified**:

### FlowBase Design (User's Version)
```python
class FlowBase(ABC):
    # Framework handles config validation, NOT the flow class
    
    @abstractmethod
    def run(self, **kwargs) -> Any:
        """Execute flow logic"""
        pass
    
    def on_start(self) -> None: ...
    def on_complete(self, result: Any) -> None: ...
    def on_error(self, error: Exception) -> None: ...
```

### Key Decisions
- **__init__ signature**: `__init__(self, flow_config: Dict, global_config: Dict)`
  - Flow receives both configs but framework handles validation
- **Metadata source**: `pyproject.toml` (not get_metadata() method)
  - Framework reads plugin's pyproject.toml for name, version, description
- **Validation responsibility**: Framework validates, flow executes
  - FlowBase does NOT have validate_config() method
  - Config validation happens before flow instantiation

### Impact on Plan
- Task 1 (FlowBase): Simplify to user's design
- Task 2 (Plugin Models): Add FlowPluginInfo model for pyproject.toml metadata
- Task 7-8 (Validation): Move validation entirely to loader, remove from flow class
- Task 6 (Example Flow): Example class only needs run() + optional hooks


## Design Update 2 (最新用户反馈)

### 1. Flow 类导出方式变更
**用户要求**: "让第三方 flow 自己主动 export 类"

**变更前**: 
```python
# 框架自动查找
def find_flow_class(module):
    for name in dir(module):
        if issubclass(obj, FlowBase):
            flow_classes.append(obj)
```

**变更后**:
```python
# Flow 插件的 src/main.py 必须导出 FlowClass 变量
from madousho.flow.base import FlowBase

class ExampleFlow(FlowBase):
    def run(self, **kwargs):
        pass

# 主动导出 - 框架直接读取
FlowClass = ExampleFlow
```

**优点**:
- 更明确，不依赖魔法查找
- 如果有多个类，flow 作者自己决定导出哪个
- 错误信息更清晰（FlowClass 不存在 vs 找到 0 个类）

### 2. 移除依赖验证（暂时）
**用户**: "我们还没做到 tools 和 mcp 的支持"

**决策**:
- 移除 `PluginDependency` 模型
- 移除 `dependencies` 字段
- 移除依赖验证相关任务
- 专注核心加载逻辑，依赖验证以后再加

### 影响的任务
- Task 2 (Plugin Models): 移除 PluginDependency
- Task 8 (依赖验证): 从 Wave 2 移除或标记为可选
- loader.py: 移除 validate_dependencies() 调用
