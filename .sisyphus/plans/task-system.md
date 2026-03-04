# Task System Implementation

## TL;DR

> **Quick Summary**: 为 Madousho.ai 实现 Task 系统，支持类 API 实例化任务、JSON 持久化跟踪状态、label 机制实现 task 间数据传递、并行执行和条件重试。
> 
> **Deliverables**:
> - `src/madousho/flow/tasks/base.py` - TaskBase 抽象类
> - `src/madousho/flow/storage.py` - FlowStorage 存储层（JSON + JSONL）
> - `src/madousho/flow/base.py` - 扩展 FlowBase 添加 task 管理方法
> - `src/madousho/db/models.py` - 删除（不使用 SQLite）
> - 示例 Flow 和 Task 实现
> - 单元测试
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: TaskBase → FlowStorage → FlowBase 扩展 → 示例 → 测试

---

## Context

### Original Request
为 Madousho.ai 实现 Task 系统，要求：
- 类风格方法（class-based API）
- Flow 实例化时传入 UUID、名字、简介、上下文
- JSON 持久化（1+N 文件结构）
- Label 机制（不唯一，支持多个同 label task）
- 并行执行 + 条件重试
- 单用户开源项目，负载不大

### Interview Summary
**Key Discussions**:
- **存储方案**: 纯 JSON 文件（零依赖，直观）
- **全局索引**: JSON Lines（flows.jsonl，支持懒加载分页）
- **Flow Meta**: `data/flow/{flow_uuid}/meta.json`
- **Task State**: `data/flow/{flow_uuid}/{task_uuid}.json`
- **原子写入**: tempfile + os.replace + fsync
- **并行执行**: asyncio（IO 密集型）
- **Task 方法**: `async def run()`
- **实时更新**: LLM 每次对话后保存状态

**Research Findings**:
- JSON Lines 支持逐行读取，无需全量加载
- 单用户 1,000 flows → flows.jsonl ~300KB → 懒加载无压力
- 原子写入用标准库即可，无需第三方依赖

### Metis Review
**Identified Gaps** (addressed):
- ✅ 懒加载方案：JSON Lines 逐行读取
- ✅ 分页支持：offset+limit，提前退出优化
- ✅ 原子写入：临时文件 + fsync + 原子替换
- ✅ 并发安全：asyncio.Lock 保护写操作

### Metis Review
**Identified Gaps** (addressed):
- ✅ 懒加载方案：JSON Lines 逐行读取
- ✅ 分页支持：offset+limit，提前退出优化
- ✅ 原子写入：临时文件 + fsync + 原子替换
- ✅ 并发安全：asyncio.Lock 保护写操作

### Design Specifications

#### Exception Hierarchy (5 Layers)

```python
class MadoushoError(Exception):
    """Base exception for all Madousho errors."""
    def __init__(self, message: str, cause: Optional[Exception] = None): ...

class TaskError(MadoushoError):
    """Base exception for task-related errors."""
    def __init__(self, message: str, task_uuid: Optional[UUID] = None, cause: Optional[Exception] = None): ...

class StorageError(MadoushoError):
    """Base exception for storage-related errors."""
    def __init__(self, message: str, storage_key: Optional[str] = None, cause: Optional[Exception] = None): ...

class TaskTimeoutError(TaskError):
    """Task exceeded timeout limit."""
    def __init__(self, task_uuid: UUID, timeout_seconds: float, cause: Exception = None): ...

class TaskRetryExhaustedError(TaskError):
    """Task exhausted all retry attempts."""
    def __init__(self, task_uuid: UUID, max_retries: int, cause: Exception = None): ...

class CorruptedDataTaskError(TaskError):
    """Task data is corrupted or invalid."""
    def __init__(self, task_uuid: UUID, field: str, cause: Exception = None): ...

class CorruptedDataStorageError(StorageError):
    """Stored data is corrupted or invalid."""
    def __init__(self, storage_key: str, field: str, cause: Exception = None): ...
```

#### TaskState Pydantic Model

```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class OpenAIMessage(BaseModel):
    role: str = Field(..., pattern=r"^(system|user|assistant|function)$")
    content: str
    name: Optional[str] = None

class TaskState(BaseModel):
    task_uuid: UUID
    label: str = Field(..., min_length=1, max_length=255, pattern=r'^[a-zA-Z0-9_-]+$')
    status: TaskStatus = TaskStatus.PENDING
    messages: List[OpenAIMessage] = []
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def is_completed(self) -> bool: ...
    def is_failed(self) -> bool: ...
    def mark_running(self) -> None: ...
    def mark_completed(self, result: Any) -> None: ...
    def mark_failed(self, error_msg: str) -> None: ...
    def add_message(self, message: OpenAIMessage) -> None: ...
    def to_dict(self) -> Dict: ...
    @classmethod
    def from_dict(cls, data: Dict) -> 'TaskState': ...
```

#### Label Validation

```python
class LabelValidator:
    MIN_LENGTH = 1
    MAX_LENGTH = 255
    ALLOWED_CHARS_PATTERN = r'^[a-zA-Z0-9_-]+$'
    
    @staticmethod
    def validate(label: str) -> Tuple[bool, str]:
        """Returns (is_valid, error_message)"""
        if not isinstance(label, str): return False, "Label must be a string"
        if len(label) < 1: return False, "Label must be at least 1 character"
        if len(label) > 255: return False, "Label must be no more than 255 characters"
        if not re.match(ALLOWED_CHARS_PATTERN, label):
            return False, "Only alphanumeric, underscores, and hyphens allowed"
        return True, ""
```

#### UUID Generation

```python
class UUIDGenerationStrategy:
    @staticmethod
    def generate_task_uuid() -> UUID:
        """Generate UUID4 (random) for task identifiers"""
        return uuid.uuid4()
    
    @staticmethod
    def format_for_storage(task_uuid: UUID) -> str:
        return str(task_uuid)
    
    @staticmethod
    def parse_from_storage(uuid_string: str) -> Optional[UUID]:
        try: return uuid.UUID(uuid_string)
        except: return None
```

---

## Work Objectives
---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest)
- **Automated tests**: YES (TDD)
- **Framework**: pytest + asyncio
- **TDD**: 每个 task 遵循 RED → GREEN → REFACTOR

### QA Policy
每个 task 必须包含 agent-executed QA scenarios：
- **Frontend/UI**: N/A（无 UI）
- **CLI**: interactive_bash 运行示例 flow
- **API**: N/A（无 API）
- **Library**: pytest 运行单元测试

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - 基础设施):
├── Task 1: TaskBase 抽象类 [quick]
├── Task 2: AtomicJsonWriter 原子写入 [quick]
├── Task 3: FlowIndex JSONL 索引 [quick]
├── Task 4: FlowStorage 存储层 [quick]
└── Task 4B: 崩溃恢复机制 [quick]

Wave 2 (After Wave 1 - FlowBase 扩展):
├── Task 5: FlowBase 扩展 - register_task/get_tasks/run_task [deep]
├── Task 6: FlowBase 扩展 - run_parallel [deep]
└── Task 7: FlowBase 扩展 - retry_until [quick]

Wave 3 (After Wave 2 - 示例 + 测试):
├── Task 8: 示例 Flow 和 Task 实现 [visual-engineering]
├── Task 9: 单元测试 - TaskBase [deep]
├── Task 10: 单元测试 - FlowStorage [deep]
└── Task 11: 单元测试 - FlowBase 扩展 [deep]

Wave FINAL (After ALL tasks - 验证):
├── F1: Plan Compliance Audit (oracle)
├── F2: Code Quality Review (unspecified-high)
├── F3: Real Manual QA (unspecified-high)
└── F4: Scope Fidelity Check (deep)

Critical Path: Task 1 → Task 4 → Task 5 → Task 8 → Task 9-11 → F1-F4
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 5 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|------------|--------|
| 1-4, 4B | — | 5-7 |
| 5-7 | 1-4, 4B | 8-11 |
| 8-11 | 5-7 | F1-F4 |
| F1-F4 | 9-12 | — |

### Agent Dispatch Summary

- **Wave 1**: 5 tasks → `quick` (基础工具类 + 崩溃恢复)
- **Wave 2**: 3 tasks → `deep`/`quick` (FlowBase 扩展)
- **Wave 3**: 4 tasks → `deep`/`visual-engineering` (示例 + 测试)
- **FINAL**: 4 tasks → 并行 review

---

## TODOs

- [ ] 1. TaskBase 抽象类

  **What to do**:
  - 创建 `src/madousho/flow/tasks/__init__.py`（包初始化）
  - 创建 `src/madousho/flow/tasks/base.py`
  - 实现 `TaskBase` 抽象类：
    - `__init__(self, flow_uuid: str, label: str = None, **kwargs)`
    - `@abstractmethod def run(self) -> Any` - **同步方法**
    - `_save_state(self)` - 保存到 JSON（内部方法）
    - `get_flow(self)` - 获取 Flow 实例
  - Task State 格式：OpenAI 风格 messages + result 字段

  **Must NOT do**:
  - 不实现具体 Task（由用户自定义）
  - 不启动其他 Task（违反单一职责）

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: 简单抽象类，无复杂逻辑

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2-4)
  - **Blocks**: Tasks 5-8
  - **Blocked By**: None

  **References**:
  - `src/madousho/flow/base.py:43-54` - FlowBase 抽象方法定义模式
  - 设计文档：Task State JSON 格式

  **Acceptance Criteria**:
  - [ ] `src/madousho/flow/tasks/base.py` 存在
  - [ ] `TaskBase` 是抽象类（继承 ABC）
  - [ ] `run()` 是抽象方法（`@abstractmethod`）
  - [ ] `run()` 是**同步方法**（`def run`，不是 `async def`）
  - [ ] `python -c "from madousho.flow.tasks.base import TaskBase"` → 无错误

  **QA Scenarios**:
  ```
  Scenario: 导入 TaskBase 成功
    Tool: Bash
    Steps:
      1. 运行：python -c "from madousho.flow.tasks.base import TaskBase; print('OK')"
    Expected Result: 输出 "OK"，退出码 0
    Evidence: .sisyphus/evidence/task-1-import.txt

  Scenario: TaskBase 是抽象类
    Tool: Bash
    Steps:
      1. 运行：python -c "from madousho.flow.tasks.base import TaskBase; import inspect; print(inspect.isabstract(TaskBase))"
    Expected Result: 输出 "True"
    Evidence: .sisyphus/evidence/task-1-abstract.txt
  ```

  **Commit**: YES (groups with 2-4)
  - Message: `feat(flow): add TaskBase abstract class`
  - Files: `src/madousho/flow/tasks/base.py`, `src/madousho/flow/tasks/__init__.py`

---

- [ ] 2. AtomicJsonWriter 原子写入

  **What to do**:
  - 在 `src/madousho/flow/storage.py` 中实现 `AtomicJsonWriter` 类
  - 实现 `async write(path: Path, data: dict)` 方法
  - 使用 `tempfile.mkstemp()` 创建临时文件
  - 使用 `os.fsync()` 确保数据落盘
  - 使用 `os.replace()` 原子替换目标文件
  - 异常时清理临时文件

  **Must NOT do**:
  - 不使用第三方库（仅标准库）
  - 不直接写入目标文件（必须原子）

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3-4)
  - **Blocks**: Tasks 5-8
  - **Blocked By**: None

  **References**:
  - 设计文档：原子写入方案（tempfile + os.replace + fsync）

  **Acceptance Criteria**:
  - [ ] `AtomicJsonWriter.write()` 是异步方法
  - [ ] 使用临时文件 + 原子替换
  - [ ] 异常时清理临时文件
  - [ ] 单元测试验证原子性

  **QA Scenarios**:
  ```
  Scenario: 原子写入成功
    Tool: Bash
    Steps:
      1. 创建测试脚本写入 JSON
      2. 验证文件存在且内容正确
    Expected Result: 文件内容匹配，无 .tmp 残留
    Evidence: .sisyphus/evidence/task-2-write-test.json

  Scenario: 异常时清理临时文件
    Tool: Bash
    Steps:
      1. 模拟写入异常（如权限问题）
      2. 验证无 .tmp 文件残留
    Expected Result: 无临时文件
    Evidence: .sisyphus/evidence/task-2-cleanup.txt
  ```

  **Commit**: YES (groups with 1, 3-4)

---

- [ ] 3. FlowIndex JSONL 全局索引

  **What to do**:
  - 在 `src/madousho/flow/storage.py` 中实现 `FlowIndex` 类
  - 实现 `async append_flow(flow_info: dict)` - 追加 flow 到索引
  - 实现 `async list_flows(limit=20, offset=0)` - 分页查询（懒加载）
  - 实现 `async update_flow(flow_uuid: str, updates: dict)` - 更新 flow
  - 实现 `async update_flow(flow_uuid: str, updates: dict)` - 更新 flow
  - JSONL 格式：每行一个 JSON 对象
  - 懒加载：逐行读取，达到 limit 提前退出

  **Must NOT do**:
  - 不一次性加载整个文件（必须懒加载）
  - 不使用 SQLite

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-2, 4)
  - **Blocks**: Tasks 5-8
  - **Blocked By**: None

  **References**:
  - 设计文档：JSON Lines 懒加载策略

  **Acceptance Criteria**:
  - [ ] `list_flows()` 支持分页（offset, limit）
  - [ ] 懒加载：逐行读取，不一次性加载全文件
  - [ ] 达到 limit 后提前退出
  - [ ] 追加写入高效（无需重写整个文件）


  **QA Scenarios**:
  ```
  Scenario: 分页查询 flows
    Tool: Bash
    Steps:
      1. 添加 50 个 flows 到索引
      2. 查询第 1 页（limit=20, offset=0）
      3. 查询第 2 页（limit=20, offset=20）
    Expected Result: 第 1 页 20 个，第 2 页 20 个，第 3 页 10 个
    Evidence: .sisyphus/evidence/task-3-pagination.json

  Scenario: 懒加载验证
    Tool: Bash
    Steps:
      1. 添加 100 个 flows
      2. 查询 limit=5，记录读取行数
    Expected Result: 只读取前 5-10 行（提前退出）
    Evidence: .sisyphus/evidence/task-3-lazy-load.txt
  ```

  **Commit**: YES (groups with 1-2, 4)

---

- [ ] 4. FlowStorage 存储层

  **What to do**:
  - 在 `src/madousho/flow/storage.py` 中实现 `FlowStorage` 类
  - 实现 `__init__(self, base_dir: Path = None)` - 初始化并创建 `data/flow/` 目录
  - 实现 `async create_flow(uuid: str, name: str, description: str, context: Dict)` - 初始化 flow
  - 实现 `async register_task(task_id: str, label: str)` - 注册 task 到 meta.json
  - 实现 `async update_task_state(task_id: str, state: Dict)` - 实时更新 task 状态
  - 实现 `async get_tasks(label: str) -> List[Dict]` - 获取所有匹配 label 的 tasks（按注册顺序）

  **Must NOT do**:
  - 不直接写文件（用 AtomicJsonWriter）
  - 不修改其他 flow 的文件

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-3)
  - **Blocks**: Tasks 5-8
  - **Blocked By**: None

  **References**:
  - `src/madousho/flow/storage.py` - AtomicJsonWriter, FlowIndex
  - 设计文档：Flow Meta 和 Task State 格式

  - [ ] `__init__()` 创建 `data/flow/` 目录（如果不存在）
  - [ ] `create_flow()` 创建 flow 目录和 meta.json
  - [ ] `register_task()` 更新 meta.json 的 tasks 列表
  - [ ] `update_task_state()` 实时更新 task 文件 + meta.json 状态
  - [ ] `get_tasks()` 从 meta.json 索引 + 按需加载 task 文件
  - [ ] 所有写操作使用 AtomicJsonWriter

  **QA Scenarios**:
  ```
  Scenario: 初始化 flow 并注册 task
    Tool: Bash
    Steps:
      1. 调用 init_flow("test_flow")
      2. 调用 register_task("task-001", "search")
      3. 验证 meta.json 存在且 tasks 列表正确
    Expected Result: meta.json 包含 1 个 task 索引
    Evidence: .sisyphus/evidence/task-4-init-meta.json

  Scenario: 保存 task 状态
    Tool: Bash
    Steps:
      1. 调用 save_task_state("task-001", {"status": "completed", "messages": [...]})
      2. 验证 task 文件存在且内容正确
      3. 验证 meta.json 中 task 状态已更新
    Expected Result: task 文件和 meta.json 都更新
    Evidence: .sisyphus/evidence/task-4-save-state.json
  ```

  **Commit**: YES (groups with 1-3)

---

---

- [ ] 4B. 崩溃恢复机制

  **What to do**:
  - 在 `src/madousho/flow/storage.py` 中实现 `recover_orphaned_tasks()` 方法
  - 启动时扫描所有 `data/flow/*/meta.json` 文件
  - 查找状态为 `running` 的 tasks
  - 将这些 tasks 标记为 `failed`，error 设为 "Process crashed or was killed"
  - 更新 `completed_at` 时间戳
  - 在应用启动时调用（CLI 或 Web 服务初始化）

  **Must NOT do**:
  - 不扫描 `completed`/`failed` 状态的 tasks（只处理孤儿）
  - 不删除 flow 目录（只更新状态）

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-4)
  - **Blocks**: Tasks 5-8
  - **Blocked By**: None

  **References**:
  - 设计文档：崩溃恢复机制（自动检测孤儿 task）
  - `src/madousho/flow/storage.py` - FlowStorage 类

  **Acceptance Criteria**:
  - [ ] `recover_orphaned_tasks()` 方法存在
  - [ ] 扫描所有 flow 目录的 meta.json
  - [ ] 将 `running` 状态的 tasks 标记为 `failed`
  - [ ] 更新 meta.json 中的 task 状态
  - [ ] 应用启动时自动调用

  **QA Scenarios**:
  ```
  Scenario: 恢复孤儿 tasks
    Tool: Bash
    Steps:
      1. 手动创建 flow 目录和 meta.json
      2. 在 meta.json 中添加一个 status="running" 的 task
      3. 调用 recover_orphaned_tasks()
      4. 验证该 task 状态变为 "failed"
    Expected Result: task 状态更新为 "failed"，error 字段有值
    Evidence: .sisyphus/evidence/task-4b-recovery.json

  Scenario: 正常 tasks 不受影响
    Tool: Bash
    Steps:
      1. 创建 flow 目录，包含 completed 和 pending 状态的 tasks
      2. 调用 recover_orphaned_tasks()
      3. 验证这些 tasks 状态不变
    Expected Result: completed/pending 状态保持不变
    Evidence: .sisyphus/evidence/task-4b-no-change.json
  ```

  **Commit**: YES (groups with 1-4)
  - Message: `feat(flow): add crash recovery mechanism`
  - Files: `src/madousho/flow/storage.py`

---

- [ ] 5. FlowBase 扩展 - register_task/get_tasks/run_task

  **What to do**:
  - 扩展 `src/madousho/flow/base.py` 中的 `FlowBase` 类
  - 添加 `__init__` 参数：`flow_uuid`, `name`, `description`, `context`
  - 添加 `storage: FlowStorage` 属性
  - 实现 `register_task(task: TaskBase, timeout: float = 30.0) -> str` - 注册 task 并返回 uuid（创建 task.json，记录元数据）
  - 实现 `get_tasks(label: str) -> List[Dict]` - 获取所有匹配 label 的 tasks（按注册顺序，label 只在当前 flow 内有意义）
  - 实现 `run_task(task: TaskBase, timeout: float = 30.0) -> Any` - **框架内置方法**：注册 + 执行 + 等待 + 返回结果

  **run_task 内部流程**:
  1. 调用 `register_task()` 注册 task（创建 task.json，记录元数据）
  2. 调用 `task.run()` 执行 task
  3. 保存结果到 task.json
  4. 返回结果
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6-8)
  - **Blocks**: Tasks 9-12
  - **Blocked By**: Tasks 1-4, 4B

  **References**:
  - `src/madousho/flow/base.py` - 现有 FlowBase 类
  - `src/madousho/flow/storage.py` - FlowStorage 类

  **Acceptance Criteria**:
  - [ ] FlowBase 可实例化（传入 uuid, name, description）
  - [ ] `register_task()` 返回 task uuid，创建 task.json 文件
  - [ ] `get_tasks()` 返回所有匹配的 tasks（label 不唯一，Flow 内唯一）
  - [ ] `run_task()` 执行完整流程：注册 → 执行 → 保存结果 → 返回
  **QA Scenarios**:
  ```
  Scenario: FlowBase 实例化
    Tool: Bash
    Steps:
      1. 实例化 FlowBase(uuid="test-123", name="test", description="...")
      2. 验证 storage 属性存在
    Expected Result: FlowBase 实例创建成功，storage 初始化
    Evidence: .sisyphus/evidence/task-5-flow-init.txt

  Scenario: 注册并查询 task
    Tool: Bash
    Steps:
      1. 创建 TestTask 实例
      2. 调用 flow.register_task(task)
      3. 调用 flow.get_tasks("test_label")
      4. 验证返回的 tasks 列表包含刚注册的 task
    Expected Result: tasks 列表长度为 1，包含刚注册的 task
    Evidence: .sisyphus/evidence/task-5-register-query.json

  Scenario: run_task 执行完整流程
    Tool: Bash
    Steps:
      1. 创建 TestTask 实例
      2. 调用 flow.run_task(task, timeout=30.0)
      3. 验证 task.json 文件创建且包含结果
      4. 验证 meta.json 中 task 状态更新为 completed
    Expected Result: task 执行成功，结果保存到 JSON
    Evidence: .sisyphus/evidence/task-5-run-task.json

  **Commit**: YES (groups with 6-8)

---

- [ ] 6. FlowBase 扩展 - run_parallel

  **What to do**:
  - 实现 `run_parallel(*tasks: TaskBase, timeout: float = 30.0) -> List[Any]` - **同步方法**
  - 内部使用 `asyncio.gather()` 并发执行所有 tasks
  - 使用 `asyncio.run()` 包装异步执行
  - 对每个 task 调用 `run_task()` 方法
  - 返回所有 task 的结果列表
  - **阻塞等待所有 tasks 完成**

  **Must NOT do**:
  - 不串行执行（必须并发）
  - 不捕获异常（让调用者处理）

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 7)
  - **Blocks**: Tasks 8-11
  - **Blocked By**: Tasks 1-4

  **References**:
  - `src/madousho/flow/tasks/base.py` - TaskBase.run()
  - Python asyncio.gather() 文档

  **Acceptance Criteria**:
  - [ ] 所有 tasks 并发执行（非串行）
  - [ ] 返回结果列表（按输入顺序）
  - [ ] 异常时抛出（不静默失败）

  **QA Scenarios**:
  ```
  Scenario: 并行执行 tasks
    Tool: Bash
    Steps:
      1. 创建 3 个 tasks（每个模拟 1 秒延迟）
      2. 调用 run_parallel(*tasks)
      3. 记录总耗时
    Expected Result: 总耗时 ~1 秒（非 3 秒）
    Evidence: .sisyphus/evidence/task-6-parallel-timing.txt

  Scenario: 异常传播
    Tool: Bash
    Steps:
      1. 创建 1 个会抛出异常的 task
      2. 调用 run_parallel(task)
      3. 验证异常被抛出
    Expected Result: 异常传播到调用者
    Evidence: .sisyphus/evidence/task-6-exception.txt
  ```

  **Commit**: YES (groups with 5, 7)

---

- [ ] 7. FlowBase 扩展 - retry_until

  **What to do**:
  - 实现 `retry_until(task_factory: Callable[[], TaskBase], condition: Callable[[Dict], bool], max_retries: int = 3) -> Any` - **同步方法**
  - 重试逻辑：执行 task → 检查 condition → 不满足则重试
  - 达到 max_retries 后抛出异常
  - 返回最后一次 task 的 result

  **Must NOT do**:
  - 不无限重试（必须 max_retries 限制）
  - 不修改 task 内部逻辑

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5-6)
  - **Blocks**: Tasks 8-11
  - **Blocked By**: Tasks 1-4

  **References**:
  - 设计文档：重试策略

  **Acceptance Criteria**:
  - [ ] 支持自定义 condition 函数
  - [ ] 达到 max_retries 后停止
  - [ ] 返回最后一次 result

  **QA Scenarios**:
  ```
  Scenario: 条件满足，一次成功
    Tool: Bash
    Steps:
      1. 创建 task_factory 返回成功 task
      2. 创建 condition 始终返回 True
      3. 调用 retry_until
    Expected Result: 一次成功，返回 result
    Evidence: .sisyphus/evidence/task-7-success.json

  Scenario: 重试后成功
    Tool: Bash
    Steps:
      1. 创建 task_factory 前 2 次失败，第 3 次成功
      2. 创建 condition 检查 result["success"] == True
      3. 调用 retry_until(max_retries=3)
    Expected Result: 第 3 次成功
    Evidence: .sisyphus/evidence/task-7-retry.json

  Scenario: 达到最大重试次数
    Tool: Bash
    Steps:
      1. 创建 task_factory 始终失败
      2. 调用 retry_until(max_retries=3)
      3. 验证抛出异常
    Expected Result: 3 次重试后抛出异常
    Evidence: .sisyphus/evidence/task-7-max-retry.txt
  ```

  **Commit**: YES (groups with 5-6)

---

- [ ] 8. 示例 Flow 和 Task 实现

  **What to do**:
  - 创建 `examples/task_flow/` 目录
  - 创建 `examples/task_flow/src/main.py` - 示例 Flow
  - 创建 `examples/task_flow/config.yaml` - Flow 配置
  - 创建 `examples/task_flow/pyproject.toml` - 插件元数据
  - 实现 `SearchTask(TaskBase)` - 模拟搜索任务
  - 实现 `SummarizeTask(TaskBase)` - 模拟总结任务
  - 实现 `ExampleFlow(FlowBase)` - 演示串行 + 并行执行

  **Must NOT do**:
  - 不调用真实 LLM API（用模拟数据）
  - 不依赖外部服务

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (sequential after Waves 1-2)
  - **Blocks**: Tasks 9-11
  - **Blocked By**: Tasks 5-7

  **References**:
  - `examples/example_flows/` - 现有示例 flow 结构
  - `src/madousho/flow/tasks/base.py` - TaskBase
  - `src/madousho/flow/base.py` - FlowBase

  **Acceptance Criteria**:
  - [ ] SearchTask 模拟搜索（返回假数据）
  - [ ] SummarizeTask 模拟总结
  - [ ] ExampleFlow 演示 register_task, get_tasks, run_parallel
  - [ ] 可运行：`madousho run --file examples/task_flow`

  **QA Scenarios**:
  ```
  Scenario: 运行示例 flow
    Tool: interactive_bash
    Steps:
      1. 激活虚拟环境
      2. 运行：madousho run --file examples/task_flow
      3. 验证输出包含 "Flow completed"
    Expected Result: Flow 成功完成，无错误
    Evidence: .sisyphus/evidence/task-8-run-flow.txt

  Scenario: 验证 JSON 文件生成
    Tool: Bash
    Steps:
      1. 检查 data/flow/ 目录下生成 flows.jsonl
      2. 检查 flow_{uuid}/meta.json 存在
      3. 检查 task_{uuid}.json 存在
    Expected Result: 所有文件存在且格式正确
    Evidence: .sisyphus/evidence/task-8-files.json
  ```

  **Commit**: YES (groups with 9-11)

---

- [ ] 9. 单元测试 - TaskBase

  **What to do**:
  - 创建 `tests/flow/test_tasks.py`
  - 测试 TaskBase 抽象类
  - 测试 `save_state()` 方法
  - 测试 `get_flow()` 方法
  - 使用 pytest + asyncio

  **Must NOT do**:
  - 不测试具体 Task 实现（由用户自定义）
  - 不依赖外部服务

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 10-11)
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 5-8

  **References**:
  - `tests/flow/test_base.py` - 现有 Flow 测试模式
  - `src/madousho/flow/tasks/base.py` - TaskBase 实现

  **Acceptance Criteria**:
  - [ ] 测试覆盖 TaskBase 所有公共方法
  - [ ] 使用 pytest-asyncio 运行异步测试
  - [ ] 测试通过：`python -m pytest tests/flow/test_tasks.py`

  **QA Scenarios**:
  ```
  Scenario: 运行 TaskBase 测试
    Tool: Bash
    Steps:
      1. 运行：python -m pytest tests/flow/test_tasks.py -v
      2. 验证所有测试通过
    Expected Result: 0 失败，0 错误
    Evidence: .sisyphus/evidence/task-9-pytest-output.txt
  ```

  **Commit**: YES (groups with 8, 10-11)

---

- [ ] 10. 单元测试 - FlowStorage

  **What to do**:
  - 在 `tests/flow/test_storage.py` 中添加测试
  - 测试 AtomicJsonWriter 原子性
  - 测试 FlowIndex 懒加载
  - 测试 FlowStorage 所有方法
  - 使用临时目录（pytest tmp_path）

  **Must NOT do**:
  - 不修改全局 data/ 目录（用临时目录）
  - 不依赖外部文件

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 9, 11)
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 1-8

  **References**:
  - `tests/flow/test_base.py` - 现有测试模式
  - `src/madousho/flow/storage.py` - FlowStorage 实现

  **Acceptance Criteria**:
  - [ ] 测试覆盖所有存储方法
  - [ ] 使用临时目录（不污染全局）
  - [ ] 测试通过：`python -m pytest tests/flow/test_storage.py`

  **QA Scenarios**:
  ```
  Scenario: 运行 FlowStorage 测试
    Tool: Bash
    Steps:
      1. 运行：python -m pytest tests/flow/test_storage.py -v
      2. 验证所有测试通过
    Expected Result: 0 失败，0 错误
    Evidence: .sisyphus/evidence/task-10-pytest-output.txt
  ```

  **Commit**: YES (groups with 8-9, 11)

---

- [ ] 11. 单元测试 - FlowBase 扩展

  **What to do**:
  - 在 `tests/flow/test_base.py` 中添加测试
  - 测试 FlowBase 扩展方法
  - 测试 register_task, get_tasks
  - 测试 run_parallel 并发执行
  - 测试 retry_until 重试逻辑

  **Must NOT do**:
  - 不修改现有测试（只添加）
  - 不依赖外部服务

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 9-10)
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 5-8

  **References**:
  - `tests/flow/test_base.py` - 现有 Flow 测试
  - `src/madousho/flow/base.py` - FlowBase 扩展

  **Acceptance Criteria**:
  - [ ] 测试覆盖所有扩展方法
  - [ ] 测试通过：`python -m pytest tests/flow/test_base.py`

  **QA Scenarios**:
  ```
  Scenario: 运行 FlowBase 扩展测试
    Tool: Bash
    Steps:
      1. 运行：python -m pytest tests/flow/test_base.py -v
      2. 验证所有测试通过
    Expected Result: 0 失败，0 错误
    Evidence: .sisyphus/evidence/task-11-pytest-output.txt
  ```

  **Commit**: YES (groups with 8-10)

---

## Final Verification Wave

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `python -m pytest` + 检查代码质量。Review all changed files for: unused imports, generic names, excessive comments. Check AI slop patterns.
  Output: `Build [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Execute example flow: `madousho run --file examples/task_flow`. Verify JSON files generated correctly. Test label querying, parallel execution.
  Output: `Example Flow [PASS/FAIL] | JSON Files [N/N] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff. Verify 1:1 — everything in spec was built, nothing beyond spec. Check "Must NOT do" compliance.
  Output: `Tasks [N/N compliant] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `feat(flow): add TaskBase and storage layer` — tasks/base.py, storage.py
  - Classes: `TaskBase`, `AtomicJsonWriter`, `FlowIndex`, `FlowStorage`
  - Methods: `create_flow()`, `append_flow()`, `register_task()`, `update_task_state()`, `get_tasks()`

- **Wave 2**: `feat(flow): extend FlowBase with task management` — flow/base.py
  - Methods: `register_task()`, `get_tasks()`, `run_task()`, `run_parallel()`, `retry_until()`

- **Wave 3**: `feat(examples): add task_flow example` — examples/task_flow/



---

## Success Criteria

### Verification Commands
```bash
python -m pytest tests/flow/test_tasks.py tests/flow/test_storage.py tests/flow/test_base.py -v  # Expected: 0 failures
madousho run --file examples/task_flow  # Expected: Flow completed successfully
ls data/flow/  # Expected: flows.jsonl + flow_{uuid}/ directory
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass
- [ ] Example flow runs successfully
- [ ] JSON files generated correctly
