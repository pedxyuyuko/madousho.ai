# Draft: Task System Design

## Requirements (confirmed)
- **Style**: 类风格方法 (class-based API)
- **Flow Instance**: 实例化时传入唯一 UUID、名字、简介 (可选)、上下文
- **Persistence**: 每个 flow instance 用 JSON 记录输出和状态
- **Recording**: 1+N 个 JSON 文件
  - 1 个记录 flow 生成了哪些 task
  - N 个记录每个 task 的输出和状态 (N = flow 开启的 task 数量)

## Technical Decisions
- **Task 定义方式**: 核心框架实现 Task 基类 (`src/madousho/flow/tasks`)，用户自定义具体 Task
- **Task 执行方式**: 
  - 用户实例化 task 类 → `task.run()`
  - Flow 提供方法：`self.get_flow().wait_for_task(task_label)` 或 `self.get_flow().get_task(task_label)`
  - 包装方法：`run_until_condition_met(task, condition, max_retry=3)` - Flow 作者自定义重试逻辑
  - 并行执行：`start_parallel(task1, task2, task_n)`
- **存储目录**: 
  - `data/flow/{flow_uuid}/meta.json` - flow 元数据 + task uuid list
  - `data/flow/{flow_uuid}/{task_uuid}.json` - 每个 task 的状态和输出
- **Task 数据传递**: 
  - Task 通过 `self.get_flow()` 获取 Flow 实例
  - 调用 `flow.wait_for_task(label)` 或 `flow.get_task(label)` 获取其他 task 的输出
  - **Label 不唯一**：相同 label 的多个 task 返回 `[task_result, task_result, ...]` (对话历史列表)
- **Task 原则**: 每个 task 只做一件事，不能在 task 内部启动其他 task
- **Flow Meta 格式**: 
  ```json
  {
    "uuid": "...",
    "name": "...",
    "description": "...",
    "created_at": "...",
    "status": "running|completed|failed",
    "tasks": [
      {"task_id": "task_001", "label": "search", "status": "completed"},
      {"task_id": "task_002", "label": "search", "status": "pending"}
    ]
  }
  ```
- **Task State 格式**:
  ```json
  {
    "task_id": "task_001",
    "flow_uuid": "abc-123",
    "label": "search",
    "status": "completed",
    "messages": [
      {"role": "user", "content": "..."},
      {"role": "assistant", "content": "..."}
    ],
    "result": {},
    "error": null,
    "started_at": "...",
    "completed_at": "..."
  }
  ```
- **错误处理**: 由 Flow 作者决定（框架不提供默认行为）
- **重试策略**: 
  - Flow 作者可以选择：重新来过（重置上下文）或自定义重试逻辑
  - 框架提供基础工具：`run_until_condition_met` 等方法
  - Task 内部可以实现自己的重试逻辑（如重试 LLM 对话）
- **并发安全**: 
  - `meta.json` 仅由 Flow 编辑，Task 只读
  - Flow 的 task 执行是阻塞的，理论上无竞争
  #YR|  - `task_{uuid}.json` 每个 task 独立写入，无竞争

## Technical Decisions (Final)
67#AS|- **并行执行模型**: asyncio（异步并发）
68#KL|  - 理由：LLM API 调用是 IO 密集型任务
  - Task 的 `run()` 方法设计为 `async def`
  - 并行执行：`asyncio.gather()` 并发启动多个 task
- **UUID 生成**: `uuid.uuid4()`（标准库，足够随机）
- **原子写入方案**: 标准库 tempfile + os.replace + fsync
  - 零依赖，POSIX 保证的原子性
74#LK|  - 异步集成：`asyncio.run_in_executor()` 在线程池运行
  - 并发保护：`asyncio.Lock` 防止并发写入同一文件
- **存储格式**: 
  - 全局索引：`data/flow/flows.jsonl` - JSON Lines（行式 JSON，支持懒加载）
  - Flow Meta：`data/flow/{flow_uuid}/meta.json` - Flow 详情 + task 索引
  - Task State：`data/flow/{flow_uuid}/{task_uuid}.json` - Task 详细状态
- **JSONL 优势**: 逐行读取、支持分页、追加写入高效、无需全量加载
  - 示例：`{"uuid":"abc","name":"flow1","created_at":"..."}\n{"uuid":"def",...}`

## Open Questions (Resolved)
82#PL|- ✅ 并行执行模型：asyncio（已确认）
- ✅ UUID 生成：uuid.uuid4()（已确认）
84#EG|- ✅ 原子写入：标准库方案（已确认）
85#UF|- ✅ 实时更新：关键节点保存（已确认）
86#JL|- ✅ 存储格式：JSON Lines（.jsonl）用于全局索引（已确认）

## Open Questions
1. 使用 asyncio 还是 threading 实现并行执行？
2. UUID 生成方式（uuid.uuid4() 还是其他）？

## Scope Boundaries
- INCLUDE: Task 基类、Flow 基类扩展、Storage 层、JSON 持久化
- EXCLUDE: 内置 Task 实现（由用户自定义）


---

## Agent Gap Analysis Summary (2026-03-04)

### Metis Review (ses_3483af696ffex3DEpq8gKw4F1T)

**CRITICAL Gaps** (5 items):
1. **并发安全问题** - task 注册和 JSONL 追加存在 race condition
2. **锁范围不明确** - 全局锁 vs per-flow 锁 vs per-file 锁
3. **缺少自定义异常** - 需要使用异常层次结构
4. **方法命名冲突** - 计划中重复列出相同功能的不同方法名
5. **验收标准缺失** - 缺少并发写入、错误处理的验收标准

**HIGH Gaps** (5 items):
6. **缺少防护栏** - 无最大重试次数、超时、文件大小限制
7. **13+ 边界情况未定义** - 磁盘满、JSON 损坏、文件删除等
8. **类型安全缺失** - 缺少 TypedDict 定义 TaskState
9. **测试覆盖不足** - 缺少并发、故障恢复、集成测试
10. **假设未验证** - JSONL 性能、原子写入跨平台测试

**MEDIUM Gaps** (3 items):
11. **文件结构** - 考虑分片、锁文件、临时目录
12. **范围蔓延预防** - 冻结方法签名
13. **测试组织** - 与现有测试的关系

---

### Oracle Review (ses_34839443affeXbag4vjNZ4hEav)

**并发模式建议**:
- ✅ 使用 `asyncio.Lock` + per-file 粒度（不是全局锁）
- ✅ `wait_for_task` 使用 `asyncio.Event` + polling fallback
- ✅ 参考 Celery 模式：事件通知 + 轮询安全网

**异常处理建议**:
```python
class MadoushoError(Exception): pass
class TaskError(MadoushoError): 
    def __init__(self, task_id: str, cause: Exception, state: dict = None)
class TaskTimeoutError(TaskError): pass
class TaskRetryExhaustedError(TaskError): pass
class StorageError(MadoushoError): pass
class CorruptedDataError(StorageError): pass
```
- ✅ Task 异常时自动保存状态
- ✅ `retry_until` 支持 `retryable_exceptions` 参数

**文件安全建议**:
- ✅ `tempfile + os.replace + fsync` 是正确的
- ✅ 生产环境使用 `fcntl` 文件锁（开发环境可选）
- ✅ 损坏 JSON 自动备份 + 重新初始化

**API 设计建议**:
- ✅ 使用 dataclasses 替代 Dict（类型安全）
- ✅ `TaskBase.run()` 既返回值又保存状态
- ✅ 重命名建议：`get_tasks` → `list_tasks`, `register_task` → `add_task`

**可扩展性建议**:
- ✅ JSON → SQLite 迁移触发点：50K flows 或 5 writes/sec
- ✅ 设计 `FlowStorageProtocol` 抽象，支持后端切换

**测试策略建议**:
- ✅ 使用 `pytest-asyncio` + time freeze
- ✅ 最小覆盖：FlowStorage 95%, FlowBase 90%, TaskBase 85%
- ✅ Race condition 压力测试：100 并发追加

---

## 需要决策的问题（按优先级排序）

### 🔴 CRITICAL（实施前必须决定）

1. **锁粒度**：per-file lock（推荐）还是 per-flow lock？
2. **wait_for_task 模式**：纯 polling（简单）还是 Event+polling（复杂但高效）？
3. **异常层次结构**：是否采用 5 层异常体系？
4. **dataclass vs Dict**：是否用 dataclass 替代 Dict？
5. **方法重命名**：是否采纳 Oracle 的命名建议（`list_tasks`, `add_task`）？

### 🟡 HIGH（应该决定）

6. **防护栏具体数值**：
   - `max_retries` 上限：10 还是 20？
   - `task_timeout` 上限：300s 还是 600s？
   - 文件大小上限：10MB 还是 100MB？
7. **文件结构**：是否采用分片结构（`{flow_uuid[0:2]}/{flow_uuid}/`）？
8. **fcntl 文件锁**：默认开启还是作为可选配置？
9. **迁移路径**：是否在第一版就设计 `FlowStorageProtocol` 抽象？

### 🟢 MEDIUM（可以后期优化）

10. **Event 优化**：第一版用 polling，第二版再加 Event？
11. **性能基准**：实施后再做 1000+ flows 的性能测试？
12. **测试组织**：先实现再重构测试文件结构？

---

## 建议的行动计划

### 实施前（4-6 小时）

1. **设计审查会议**（1 小时）
   - 决定 CRITICAL 的 5 个问题
   - 冻结方法签名
   - 批准文件结构

2. **Spike 任务**（2-3 小时）
   - JSONL 性能基准（1000+ lines）
   - 跨平台原子写入测试（Linux + Windows）
   - asyncio.Lock 原型

3. **更新计划**（1-2 小时）
   - 添加 13+ 边界情况规范
   - 定义异常层次结构
   - 添加 dataclass 模型
   - 更新验收标准

### 实施阶段（+30% 时间）

- Wave 1: +2 tasks（锁管理 + 异常定义）
- Wave 2: +1 task（dataclass 模型）
- Wave 3: +2 tasks（并发测试 + 压力测试）

**总时间估算**: Medium → **Medium-High**（原计划 +30%）

## Design Decision: Critical Architecture Choices (2026-03-04)

### 1. Concurrency: Per-File Lock ✅

**Decision**: Use `asyncio.Lock` with per-file granularity

**Implementation**:
```python
class FlowStorage:
    def __init__(self, base_path: Path):
        self._locks: dict[str, asyncio.Lock] = {}
        self._lock_manager = asyncio.Lock()  # Lock for lock creation
    
    async def _get_lock(self, key: str) -> asyncio.Lock:
        """Get lock for specific file (key = filename or flow_uuid)"""
        async with self._lock_manager:
            if key not in self._locks:
                self._locks[key] = asyncio.Lock()
            return self._locks[key]
    
    async def register_task(self, task_id: str, label: str, flow_uuid: str):
        lock = await self._get_lock(f"meta:{flow_uuid}")
        async with lock:
            # Safe read-modify-write
            meta = await self._read_meta()
            meta["tasks"].append({"task_id": task_id, "label": label})
            await self._write_meta(meta)
```

**Lock Keys**:
- `meta:{flow_uuid}` - Lock for each flow's meta.json
- `flows_jsonl` - Global lock for flows.jsonl appends

**Why Per-File**:
- ✅ Different flows can write in parallel
- ✅ Prevents race conditions within same flow
- ✅ Better throughput than global lock
- ✅ Simpler than per-flow lock management

---

### 2. wait_for_task: Pure Polling (500ms) ✅

**Decision**: Use simple polling with 500ms interval

**Implementation**:
```python
async def wait_for_task(self, label: str, timeout: float = 30.0) -> Dict:
    """Poll task status every 500ms until completed/failed"""
    start_time = time.time()
    
    while True:
        tasks = self.get_tasks(label)
        
        # Check if task completed
        if tasks and tasks[-1]["status"] in ["completed", "failed"]:
            return tasks[-1]
        
        # Check timeout
        elapsed = time.time() - start_time
        if elapsed >= timeout:
            raise TaskTimeoutError(
                label, 
                f"Task {label} did not complete within {timeout}s"
            )
        
        # Wait 500ms before next poll
        await asyncio.sleep(0.5)
```

**Why Polling**:
- ✅ Simple implementation
- ✅ Single-user scenario, latency not critical
- ✅ Less bug-prone than Event-based
- ✅ Can optimize to Event later if needed

---

### 3. Exception Hierarchy: 5-Layer Structure ✅

**Decision**: Implement comprehensive exception hierarchy

**Implementation**:
```python
# src/madousho/flow/exceptions.py

class MadoushoError(Exception):
    """Base exception for all Madousho errors"""
    pass

class TaskError(MadoushoError):
    """Task execution failed"""
    def __init__(self, task_id: str, message: str, cause: Exception = None):
        self.task_id = task_id
        self.cause = cause
        super().__init__(f"Task {task_id}: {message}")

class TaskTimeoutError(TaskError):
    """Task exceeded timeout"""
    pass

class TaskRetryExhaustedError(TaskError):
    """Task failed after max retries"""
    pass

class StorageError(MadoushoError):
    """Storage operation failed"""
    def __init__(self, message: str, file_path: Path = None):
        self.file_path = file_path
        super().__init__(message)

class CorruptedDataError(StorageError):
    """JSON/JSONL file is corrupted"""
    pass
```

**Usage**:
```python
try:
    await flow.retry_until(task_factory, condition, max_retries=3)
except TaskTimeoutError as e:
    logger.error(f"Task {e.task_id} timed out")
except TaskRetryExhaustedError as e:
    logger.error(f"Task {e.task_id} exhausted retries: {e.cause}")
except CorruptedDataError as e:
    logger.error(f"Data corrupted: {e.file_path}")
```

**Why 5 Layers**:
- ✅ Precise error handling
- ✅ Rich error context (task_id, file_path, cause)
- ✅ Better debugging and logging
- ✅ Professional error reporting

---

### 4. Data Model: dataclass over Dict ✅

**Decision**: Use dataclasses for type-safe state management

**Implementation**:
```python
# src/madousho/flow/models.py

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Literal, Any, Optional

@dataclass
class TaskState:
    """Task state with type safety"""
    task_id: str
    label: str | None = None
    status: Literal["pending", "running", "completed", "failed"] = "pending"
    result: Any = None
    error: str | None = None
    messages: list[dict] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.messages is None:
            self.messages = []
    
    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization"""
        data = asdict(self)
        # Convert datetime to ISO format
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TaskState':
        """Create from dict (loaded from JSON)"""
        # Parse ISO format datetime
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)
    
    @property
    def is_completed(self) -> bool:
        return self.status == "completed"
    
    @property
    def is_failed(self) -> bool:
        return self.status == "failed"
```

**Usage**:
```python
# Type-safe creation
task = TaskState(
    task_id="task-123",
    label="search",
    status="running"
)

# IDE autocomplete
task.status  # Shows valid options
task.result  # Type: Any

# Safe access
if task.is_completed:
    process(task.result)

# Serialization
json_data = task.to_dict()
task_from_json = TaskState.from_dict(json_data)
```

**Why dataclass**:
- ✅ IDE autocomplete
- ✅ Type checking (mypy support)
- ✅ Default values handled automatically
- ✅ Methods can be attached (to_dict, from_dict, is_completed)
- ✅ Prevents typos in field names

---

## Summary of Critical Decisions

| Decision | Choice | Impact |
|----------|--------|--------|
| **Lock Granularity** | Per-File Lock | Prevents race conditions, allows parallel flows |
| **wait_for_task** | Pure Polling (500ms) | Simple, sufficient for single-user |
| **Exception Hierarchy** | 5 Layers | Professional error handling |
| **Data Model** | dataclass | Type safety, IDE support |
| **API Design** | `get_tasks()` only | Simpler, more Pythonic |

**Status**: All decisions finalized and ready for implementation.


---

## Design Decision: API Simplification (2026-03-04)

### Decision: Remove `get_latest_task()` - Keep Only `get_tasks()`

**Problem**: 
- Plan had duplicate methods: `get_latest_task()` and `get_task()` both return latest matching task
- Oracle and Metis both flagged this as naming conflict

**Discussion**:
- `get_latest_task(label)` internally just does `get_tasks(label)[-1]`
- User can easily do this themselves: `tasks = flow.get_tasks("search"); latest = tasks[-1] if tasks else None`
- Removing `get_latest_task()` makes API simpler and more Pythonic

**Decision**:
```python
class FlowBase:
    def get_tasks(self, label: str) -> List[Dict]:
        """获取所有匹配 label 的 tasks（按注册顺序）"""
        return await self.storage.get_tasks(label)
    
    # ❌ Removed: get_latest_task()
```

**Usage**:
```python
# Get latest
tasks = flow.get_tasks("search")
latest = tasks[-1] if tasks else None

# Get recent 3
recent = flow.get_tasks("search")[-3:]

# Check existence
if flow.get_tasks("search"):
    ...
```

**Benefits**:
- ✅ Simpler API (one less method to remember)
- ✅ More Pythonic (list slicing is standard Python)
- ✅ More flexible (user can slice however they want)
- ✅ Resolves naming conflict identified by Metis/Oracle

**Trade-offs**:
- ⚠️ User must handle empty list case themselves
- ⚠️ Slightly more verbose for common case

**Status**: ✅ Plan updated to reflect this decision


---

## Critical Decisions (Gap Analysis Resolution - 2026-03-04)

### Decisions from Gap Analysis

| Decision | Choice | Rationale |
|----------|--------|----------|
| **flows.jsonl 争用风险** | 无需修改 | 只在 flow 启动时追加一次，冷路径，全局锁足够 |
| **崩溃恢复** | 自动检测 | 启动时扫描 `running` 状态的 task，标记为 `failed`，工作量小 |
| **Label 命名空间** | Flow 内唯一 | 不同 flow 的 label 互不影响，符合直觉 |
| **Task 结果大小** | 无限制 | JSON 能存多大就存多大，真遇到再优化 |
| **存储抽象层** | 直接 JSON 实现 | 单用户场景 JSON 足够，未来需要时再重构 |

---

### Implementation Details

#### 1. flows.jsonl 设计确认

```python
# flows.jsonl 访问模式（冷路径）
async def create_flow(uuid: str, name: str, description: str, context: dict):
    # 1. 创建目录 data/flow/{uuid}/
    # 2. 写入 meta.json
    # 3. 追加一行到 flows.jsonl ← 唯一一次触碰全局索引
    await self.index.append({
        "uuid": uuid,
        "name": name,
        "description": description,
        "created_at": datetime.utcnow().isoformat()
    })

# Flow 执行期间（热路径）
async def run_task(task):
    # 只访问：data/flow/{uuid}/meta.json
    # 只访问：data/flow/{uuid}/{task_uuid}.json
    # 再也不碰 flows.jsonl ✅
```

**并发保护**：
```python
class FlowIndex:
    def __init__(self):
        self._lock = asyncio.Lock()  # 全局锁，保护 flows.jsonl
    
    async def append(self, flow_info: dict):
        async with self._lock:  # 串行化所有追加操作
            await self._atomic_append(flow_info)
```

---

#### 2. 崩溃恢复机制（自动检测）

**TaskState 新增字段**：
```python
class TaskState(BaseModel):
    # ... existing fields ...
    pid: Optional[int] = None  # 执行进程 ID（可选，用于调试）
```

**恢复逻辑**：
```python
class FlowStorage:
    async def recover_orphaned_tasks(self):
        """启动时调用，扫描所有 running 状态的 task 并标记为 failed"""
        for flow_dir in self.data_dir.iterdir():
            if not flow_dir.is_dir():
                continue
            
            meta_file = flow_dir / "meta.json"
            if not meta_file.exists():
                continue
            
            try:
                meta = await self._read_json(meta_file)
                flow_uuid = meta["uuid"]
                
                for task_info in meta.get("tasks", []):
                    if task_info["status"] == "running":
                        # 标记为 failed
                        task_file = flow_dir / f"{task_info['task_id']}.json"
                        task_state = await self._read_json(task_file)
                        task_state["status"] = "failed"
                        task_state["error"] = "Process crashed or was killed"
                        task_state["completed_at"] = datetime.utcnow().isoformat()
                        await self._write_json(task_file, task_state)
                        
                        # 更新 meta.json
                        task_info["status"] = "failed"
                        await self._write_json(meta_file, meta)
                        
            except (json.JSONDecodeError, KeyError):
                # 损坏的 meta.json，跳过或记录日志
                continue
```

**调用时机**：
```python
# 应用启动时（例如 CLI 启动或 Web 服务启动）
async def initialize_storage():
    storage = FlowStorage(data_dir="data/flow")
    await storage.recover_orphaned_tasks()  # 清理孤儿 task
    return storage
```

---

#### 3. Label 命名空间（Flow 内唯一）

**设计**：
```python
class FlowBase:
    def __init__(self, uuid: str, name: str, description: str, context: dict):
        self.uuid = uuid
        self.storage = FlowStorage()
    
    def register_task(self, task: TaskBase) -> str:
        task_id = str(uuid.uuid4())
        # Label 只在当前 flow 内有意义
        await self.storage.register_task(
            task_id=task_id,
            label=task.label,
            flow_uuid=self.uuid  # ← 关键：绑定到当前 flow
        )
        return task_id
    
    def get_tasks(self, label: str) -> List[Dict]:
        # 只返回当前 flow 内匹配 label 的 tasks
        return await self.storage.get_tasks(
            label=label,
            flow_uuid=self.uuid  # ← 关键：限定在当前 flow
        )
```

**存储结构**：
```json
// data/flow/{flow_uuid}/meta.json
{
  "uuid": "flow-123",
  "name": "My Flow",
  "tasks": [
    {"task_id": "task-001", "label": "search", "status": "completed"},
    {"task_id": "task-002", "label": "search", "status": "completed"}
  ]
}

// data/flow/{flow_uuid}/task-001.json
{
  "task_id": "task-001",
  "flow_uuid": "flow-123",  // ← 绑定到特定 flow
  "label": "search",
  "status": "completed"
}
```

**不同 flow 的 label 互不影响**：
```python
# Flow A
flow_a = FlowBase("flow-a", ...)
flow_a.register_task(SearchTask(label="search"))  # task-001

# Flow B
flow_b = FlowBase("flow-b", ...)
flow_b.register_task(SearchTask(label="search"))  # task-002

# 查询结果
flow_a.get_tasks("search")  # 返回 [task-001]，不受 flow-b 影响 ✅
flow_b.get_tasks("search")  # 返回 [task-002]，不受 flow-a 影响 ✅
```

---

#### 4. Task 结果大小（无限制）

**设计**：
```python
class TaskState(BaseModel):
    # ... fields ...
    result: Optional[Any] = None  # 无大小限制，JSON 能存多大就存多大
    messages: List[OpenAIMessage] = []  # 无数量限制
```

**未来优化方向（如需要）**：
```python
# 如果真遇到大结果问题，可以：
# 1. 添加配置项：MAX_TASK_RESULT_SIZE = 10_000_000  # 10MB
# 2. 超过限制时抛异常或建议使用外部存储
# 3. 使用文件引用：result = {"type": "file", "path": "data/flow/.../result.txt"}
```

---

#### 5. 存储抽象层（直接 JSON 实现）

**设计**：
```python
# 不预先设计 Protocol，直接实现 JSON 版本
class FlowStorage:
    def __init__(self, data_dir: str = "data/flow"):
        self.data_dir = Path(data_dir)
        self._locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
    
    async def create_flow(self, uuid: str, name: str, description: str, context: dict):
        # 直接实现 JSON 写入逻辑
        ...
    
    async def register_task(self, task_id: str, label: str, flow_uuid: str):
        # 直接实现 JSON 写入逻辑
        ...
```

**未来迁移路径（如需要）**：
```python
# 如果将来需要 SQLite，可以：
# 1. 定义 FlowStorageProtocol（接口）
# 2. 实现 FlowStorageSQLite（新后端）
# 3. 通过配置切换：FLOW_STORAGE_BACKEND = "json" | "sqlite"
```

---

## Summary

**All Critical Decisions Finalized**:
- ✅ flows.jsonl 设计确认（全局索引 + 全局锁）
- ✅ 崩溃恢复机制（启动时自动检测孤儿 task）
- ✅ Label 命名空间（Flow 内唯一）
- ✅ Task 结果大小（无限制）
- ✅ 存储抽象层（直接 JSON 实现）

**Status**: Ready for implementation


---

## Gap Analysis Resolution - Round 2 (2026-03-04, Direct Plan Review)

### Codebase Verification Results

**Critical Findings**:

| Question | Method | Result | Implication |
|----------|--------|--------|-------------|
| TinyDB used? | `grep -r "tinydb" src/ tests/` | ❌ No matches | Pure JSON approach is safe, no conflict |
| asyncio used? | `grep -r "asyncio" src/madousho/` | ❌ No matches | FlowBase is currently synchronous |
| Existing flow module? | File system check | ✅ `src/madousho/flow/` exists | Task system will extend existing module |

---

### Metis Gap Analysis Summary (ses_345d16a8effeCoBhlbxX2QDjMw)

**Critical Gaps Identified**:

1. **Storage Backend Conflict** - RESOLVED
   - Concern: AGENTS.md mentions TinyDB, plan uses pure JSON
   - Verification: `grep -r "tinydb"` → no matches
   - Resolution: TinyDB was planned but never implemented, pure JSON is safe ✅

2. **FlowBase Synchronous vs Async** - CRITICAL
   - Current: `FlowBase.run()` is synchronous (`base.py:44`)
   - Plan requires: `async def run()` for tasks
   - Risk: Mixing sync/async could cause issues
   - Mitigation: Task 5 must add `run_async()` wrapper or convert FlowBase to async-native

3. **Missing Directory Initialization** - HIGH
   - Plan assumes: `data/flow/` directory exists
   - Reality: No task creates this directory
   - Fix: Add to FlowStorage `__init__`:
   ```python
   def __init__(self, base_dir: Path = None):
       self.base_dir = base_dir or Path("data/flow")
       self.base_dir.mkdir(parents=True, exist_ok=True)
   ```

4. **TypeHint Integration Gap** - MEDIUM
   - Existing: `config.typehint.yaml` validation system
   - Plan: No mention of task type hints
   - Fix: Add Task 4C for TypeHint integration

**Recommended Task Modifications**:

| Task | Original Scope | Modified Scope |
|------|----------------|----------------|
| 4 | FlowStorage storage layer | + Directory initialization in `__init__` |
| 4C (NEW) | — | TypeHint integration for tasks |
| 5 | FlowBase extension | + `run_async()` wrapper for backward compatibility |

---

### Oracle Architecture Review Summary (ses_345d160a4ffedR48FCaZmqoNX1)

**Strengths Identified**:
- ✅ Clear Architecture: TaskBase, FlowStorage, FlowBase extensions
- ✅ Robust Storage Design: JSON + JSONL, atomic writes, crash recovery
- ✅ Comprehensive Exception Handling: 5-layer hierarchy
- ✅ Parallel Execution Strategy: 3 waves, clear dependencies
- ✅ Thorough Testing: Each component has QA scenarios

**Potential Concerns**:

1. **Python Version Mismatch**
   - README: Python 3.10+
   - AGENTS.md: Python 3.14+ (targets future version)
   - Recommendation: Standardize on 3.10+

2. **File Structure Alignment**
   - Plan: `src/madousho/flow/tasks/`
   - Action: Verify this doesn't conflict with existing patterns

3. **Label Scope Clarification**
   - Plan mentions: "not unique", "only meaningful within current flow"
   - Action: Add explicit scoping rules documentation

**Recommendations**:
- ✅ Verify current codebase structure (DONE - no conflicts)
- ⚠️ Address Python version (defer to project maintainers)
- ✅ Consider async context manager for FlowStorage (good to have)
- ✅ Ensure documentation integration (covered in Task 9)

---

### Consolidated Action Items (Before Wave 1)

**Must Fix** (Blockers):

1. **Add Directory Initialization to Task 4**
   ```python
   # FlowStorage.__init__
   self.base_dir = base_dir or Path("data/flow")
   self.base_dir.mkdir(parents=True, exist_ok=True)
   ```

2. **Add Async Wrapper to Task 5**
   ```python
   # FlowBase
   async def run_async(self, **kwargs) -> Any:
       """Default implementation wraps sync run()"""
       return self.run(**kwargs)
   
   @abstractmethod
   def run(self, **kwargs) -> Any:
       pass
   ```

**Should Fix** (Important):

3. **Add Task 4C: TypeHint Integration**
   - Create `src/madousho/flow/tasks/typehints.py`
   - Implement `TaskTypeHintValidator` class
   - Similar to existing `TypeHintValidator` but for task-specific configs

**Nice to Have** (Defer):

4. Python version standardization (3.10 vs 3.14+) - project-wide decision
5. Async context manager for FlowStorage - can add later

---

### Revised Effort Estimate

| Wave | Original | Revised | Change |
|------|----------|---------|--------|
| Wave 1 | 5 tasks | 6 tasks (add 4C) | +20% |
| Wave 2 | 4 tasks | 4 tasks | 0% |
| Wave 3 | 4 tasks | 4 tasks | 0% |
| **Total** | **13 tasks** | **14 tasks** | **+8%** |

**Original Estimate**: Medium
**Revised Estimate**: Medium-Large (async complexity adds ~20%)

---

### Risk Mitigation Status

| Risk | Status | Action |
|------|--------|--------|
| TinyDB conflict | ✅ RESOLVED | Not implemented, pure JSON safe |
| Async/sync mixing | ⚠️ MITIGATE | Add `run_async()` wrapper in Task 5 |
| Missing directories | ⚠️ MITIGATE | Add mkdir in FlowStorage init |
| TypeHint validation gap | ⚠️ MITIGATE | Add Task 4C |
| Python version | 🟡 DEFER | Project-wide decision needed |

---

### Go/No-Go Decision

**Status**: ✅ **GO** (with modifications)

**Conditions**:
1. ✅ TinyDB conflict resolved (not implemented)
2. ⚠️ Add directory initialization to Task 4 (before implementation)
3. ⚠️ Add `run_async()` wrapper to Task 5 (before implementation)
4. ⚠️ Add Task 4C for TypeHint integration (before Wave 2)

**Execution Approach**:
1. ✅ Start with Wave 1 - All tasks independent and low-risk
2. ⚠️ Pause before Wave 2 - Verify modifications are in place
3. ✅ Proceed with Wave 2 - After adding fixes
4. ✅ Complete Wave 3 - Example + tests validate everything

---

**Summary**: The plan is **98% ready for execution**. The 2% missing pieces are:
1. Directory initialization (Task 4)
2. Async wrapper (Task 5)
3. TypeHint integration (Task 4C)

Once these are added, the plan can be executed immediately with high confidence.


---

## Gap Analysis Resolution (2026-03-04)

### Metis Gap Analysis Summary (ses_345d69ff6ffeid71xm8kldBZbv)

**CRITICAL Issues (3 items)**:

1. **C1: Per-File Locking Strategy Undefined**
   - Missing: Locking primitive, lock scope, timeout behavior, deadlock prevention
   - Resolution: Use `asyncio.Lock` with per-file granularity, lock keys = `meta:{flow_uuid}` + `flows_jsonl`
   - Guard: Lock acquisition timeout = 30s, deadlock prevention via ordered lock acquisition

2. **C2: Corruption Recovery Incomplete**
   - Missing: Handling for corrupted meta.json, flows.jsonl, individual task files
   - Resolution: Add quarantine folder for corrupted files, rebuild meta.json from task files if needed
   - Guard: Checksum validation on read, backup before write

3. **C3: Error Propagation Semantics Unclear**
   - Missing: Exception behavior for wait_for_task, run_parallel, retry_until
   - Resolution: Define error contract document (see Oracle recommendations)
   - Guard: All task exceptions wrapped in TaskError with context preservation

**HIGH Issues (7 items)**:

4. **H1: Label Mechanism Edge Cases**
   - Resolution: `label=None` → auto-generate unique ID, `label=""` → reject with ValueError
   - `wait_for_task(label)` → return list of all matching tasks

5. **H2: Task State Machine Not Defined**
   - Resolution: Define valid transitions: `pending→running→completed|failed`
   - Add `can_transition_to()` validation method

6. **H3: flows.jsonl Write Semantics**
   - Resolution: Append-only log with flow lifecycle events
   - Add `event` field: `flow_start`, `flow_complete`

7. **H4: Timeout Behavior in wait_for_task**
   - Resolution: Polling interval = 500ms, timeout exception = `TaskTimeoutError`
   - Timeout does NOT change task state (task may complete later)

8. **H5: Atomic Write Implementation**
   - Resolution: temp-file-rename pattern with fsync
   - UTF-8 encoding, compact JSON (no pretty-print)

9. **H6: Task Result Size and Memory**
   - Resolution: Soft limit 10MB (warning log), 100MB (suggest external storage)
   - Add optional `result_path` field for external storage reference

10. **H7: Testing Async Code with File I/O**
    - Resolution: pytest-asyncio, temp directories, mock file I/O for unit tests
    - Stress test: 100 concurrent tasks with random delays

**MEDIUM Issues (6 items)**:

11. **M1: Flow UUID Generation** → FlowStorage.create_flow() generates UUID v4
12. **M2: Task UUID Generation** → TaskBase generates UUID v4 in __init__
13. **M3: Context/Dependency Injection** → Add `self.context` and `self.global_config` to TaskBase
14. **M4: Backward Compatibility** → Add `schema_version` field to all JSON files
15. **M5: Logging and Observability** → Use existing Loguru logger, define log levels
16. **M6: Memory Management for Polling** → Max iterations = timeout / polling_interval

---

### Oracle Architectural Guidance Summary (ses_345d61e76ffetX0Tq20MZKYwOr)

**1. Concurrency Patterns**:
- ✅ Per-file locking sufficient with atomic writes
- ✅ Use read-write lock for meta.json (multiple readers, exclusive writer)
- ✅ Reference: aiofiles + fcntl.flock for Unix

**2. State Machine Design**:
```python
VALID_TRANSITIONS = {
    "pending": ["running", "failed"],
    "running": ["completed", "failed", "cancelling"],
    "cancelling": ["cancelled", "failed"],
    "completed": [],
    "failed": [],
    "cancelled": []
}
```

**3. Error Propagation**:
- Wrap all exceptions in TaskError with `from e` (context preservation)
- retry_until supports `retry_on=(Exception,)` parameter
- Exponential backoff: `await asyncio.sleep(2 ** attempt)`

**4. Crash Recovery Completeness**:
- Orphaned `running` tasks → mark as `failed` (planned)
- Corrupted meta.json → rebuild from task files
- Corrupted flows.jsonl → rebuild from flow directories
- Partial writes → atomic write + checksum validation

**5. Label Mechanism Edge Cases**:
- `None` and `""` treated as equivalent (unlabeled)
- No wildcards initially (keep API simple)
- Performance optimization: label_index in meta.json

**6. Testing Strategy**:
- pytest-asyncio for async tests
- StorageBackend interface for mocking
- In-memory and file-based backends for testing

**7. Future-Proofing**:
- Define `TaskStorageProtocol` now (even if not implemented)
- Dependency injection in FlowBase: `def __init__(self, storage: TaskStorageProtocol)`
- Migration path: JSON → SQLite when needed

**8. OpenAI Message Format**:
- Use Pydantic models for validation
- Allow `extra="allow"` for extensibility
- Provide helper methods for common operations

---

### Decisions Required Before Implementation

**CRITICAL (Must Decide Now)**:

| # | Decision | Options | Recommendation |
|---|----------|---------|----------------|
| 1 | Lock primitive | asyncio.Lock vs fcntl.flock | **asyncio.Lock** (simpler, cross-platform) |
| 2 | State transitions | Enforce vs document | **Enforce** (add validation method) |
| 3 | Error wrapping | Always wrap vs pass-through | **Always wrap** in TaskError |
| 4 | Label=None handling | Auto-generate vs reject | **Auto-generate** unique ID |
| 5 | Corruption recovery | Quarantine vs delete | **Quarantine** (backup for debugging) |

**HIGH (Should Decide)**:

| # | Decision | Options | Recommendation |
|---|----------|---------|----------------|
| 6 | max_retries limit | 10 vs 20 | **10** (reasonable default) |
| 7 | task_timeout limit | 300s vs 600s | **300s** (5 minutes) |
| 8 | File size warning | 10MB vs 100MB | **10MB** (early warning) |
| 9 | Schema versioning | v1.0 only vs semver | **semver** ("1.0.0") |
| 10 | Storage protocol | Define now vs later | **Define now** (for future migration) |

**MEDIUM (Can Decide Later)**:

| # | Decision | Options | Recommendation |
|---|----------|---------|----------------|
| 11 | Polling interval | 100ms vs 500ms | **500ms** (balance latency/CPU) |
| 12 | Log format | Text vs JSON | **Text** (use existing Loguru) |
| 13 | Cleanup API | Auto vs manual | **Manual** (add cleanup method, no auto-delete) |

---

### Recommended Guardrails (Add to Plan)

**Explicit Boundaries**:

1. **Single-Process Only**: Task System does not support cross-process execution
2. **No Database Queries**: FlowStorage supports only CRUD by UUID/label
3. **No Task Cancellation**: Once started, tasks run to completion
4. **No Result Size Limit**: But results >10MB trigger warning log
5. **No Schema Evolution**: Schema version 1.0.0 fixed for this wave
6. **No External Storage**: All data stored as JSON files
7. **No Real-Time Monitoring**: No SSE/websocket progress updates

---

### Missing Acceptance Criteria (Add to Plan)

**Wave 1 Acceptance**:
- [ ] All storage operations are atomic (no partial writes)
- [ ] Concurrent task updates don't corrupt data (test with 10+ parallel tasks)
- [ ] Crash recovery marks all `running` tasks as `failed` within 5 seconds
- [ ] Corrupted JSON files are detected and quarantined

**Wave 2 Acceptance**:
- [ ] `wait_for_task()` raises `TaskTimeoutError` after timeout
- [ ] `run_parallel()` completes all tasks even if some fail
- [ ] `retry_until()` retries exactly N times before raising `TaskRetryExhaustedError`
- [ ] `get_tasks(label)` returns tasks in creation order

**Wave 3 Acceptance**:
- [ ] Example flow demonstrates all Task System features
- [ ] Test coverage ≥90% (enforced by CI)
- [ ] All async tests pass with pytest-asyncio
- [ ] No race conditions in stress test (100 concurrent tasks)

---

### Edge Cases to Address

**Task Execution**:
1. Task raises exception in `__init__` (before `run()`)
2. Task never calls `_save_state()` (state not persisted)
3. Task completes but `_save_state()` fails (result lost)
4. Two tasks with same label complete at exact same time
5. `wait_for_task()` called before task is registered
6. `run_parallel()` with empty task list
7. `retry_until()` condition always returns False

**Storage**:
1. Disk full during write
2. File permission errors
3. Concurrent flow creation with same UUID
4. Index file grows to GB+ (no cleanup)
5. Task JSON file manually edited by user

**Crash Recovery**:
1. Crash during `flows.jsonl` write
2. Crash during task state update
3. Crash during flow completion
4. Multiple crashes in rapid succession

---

### Final Recommendations

**Immediate Actions (Before Wave 1)**:
1. ✅ Write Error Handling Contract (1 page doc)
2. ✅ Define Locking Strategy document
3. ✅ Specify Corruption Recovery flowchart
4. ✅ Add State Machine Diagram

**Plan Adjustments**:
1. Add Task 4C: Corruption detection and recovery
2. Add Task 5B: Context/dependency injection for tasks
3. Add Acceptance Criteria section to each wave
4. Add Guardrails section to prevent scope creep

**Testing Strategy**:
1. Create pytest fixtures for temp directories, mock time, mock UUID
2. Add stress test: 100 concurrent tasks with random delays
3. Add corruption tests: Deliberately break JSON files
4. Add crash simulation: Kill process mid-write, verify recovery

---

**Effort Impact**: Addressing these gaps adds **2-3 days** to planning but prevents **1-2 weeks** of rework during implementation.

