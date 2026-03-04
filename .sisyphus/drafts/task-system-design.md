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
  - `task_{uuid}.json` 每个 task 独立写入，无竞争

## Open Questions
1. 使用 asyncio 还是 threading 实现并行执行？
2. UUID 生成方式（uuid.uuid4() 还是其他）？

## Scope Boundaries
- INCLUDE: Task 基类、Flow 基类扩展、Storage 层、JSON 持久化
- EXCLUDE: 内置 Task 实现（由用户自定义）
