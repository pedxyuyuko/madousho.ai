# SQLite WAL 配置 & Flow/Task 数据库设计

## TL;DR

> **Quick Summary**: 为 Madousho.ai 添加 SQLite WAL 模式配置支持，并设计 Flow 和 Task 两个核心数据表。
> 
> **Deliverables**:
> - Pydantic 配置模型扩展（SqliteConfig, DatabaseConfig）
> - config/madousho.yaml 添加 database 配置段
> - database/connection.py 支持 WAL PRAGMA 配置
> - models/flow.py 和 models/task.py 数据模型
> - Alembic 迁移脚本创建 flows 和 tasks 表
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: NO - sequential (config → connection → models → migration)
> **Critical Path**: Config models → Connection update → Model definitions → Migration

---

## Context

### Original Request
用户需要设计 Flow 和 Task 两个数据库表，用于存储 AI 任务流程数据。关键需求：
- 个人项目 + 低并发（10-20 个同时 tasks）
- Task 运行时实时写入 AI 对话内容（几秒一次）
- WebUI 支持 SSE 推送进度
- Docker 部署
- 单用户使用

### Interview Summary
**Key Discussions**:
- **数据库选择**: SQLite WAL 模式（而非 PostgreSQL）- 对场景完全够用且简单
- **配置方式**: 只用 YAML 配置，不支持环境变量
- **配置方案**: 方案 A（完整 WAL 配置，所有参数可调）
- **默认值**: 使用性能优化的默认值，无需调整
- **配置位置**: 加到现有 config/madousho.yaml

**Research Findings**:
- 项目使用 SQLAlchemy 2.0 + Alembic
- 现有配置通过 Pydantic 模型验证
- 数据库连接使用单例模式
- 当前 alembic/versions/ 为空（首次创建表）

### Metis Review
**Identified Gaps** (addressed):
- **配置向后兼容**: database 字段设为可选，避免破坏现有配置
- **WAL 模式检测**: 添加日志确认 WAL 是否成功启用
- **Docker 数据持久化**: 数据库文件放在 ./data/ 目录而非根目录

---

## Work Objectives

### Core Objective
为 Madousho.ai 添加完整的 SQLite WAL 配置支持，并设计 Flow 和 Task 数据模型。

### Concrete Deliverables
- `src/madousho/config/models.py` - 扩展 SqliteConfig 和 DatabaseConfig
- `config/madousho.yaml` - 添加 database 配置段
- `src/madousho/database/connection.py` - 应用 WAL PRAGMA 配置
- `src/madousho/models/flow.py` - Flow 模型定义
- `src/madousho/models/task.py` - Task 模型定义
- `src/madousho/models/__init__.py` - 模型导出
- `alembic/versions/{timestamp}_create_flows_and_tasks.py` - 迁移脚本

### Definition of Done
- [x] 配置模型可通过 YAML 加载并验证
- [x] 数据库连接时正确应用 WAL PRAGMA
- [x] Flow 和 Task 模型符合设计（UUID 主键 + JSON 字段）
- [x] Alembic 迁移可成功执行（`alembic upgrade head`）
- [x] 日志输出确认 WAL 模式已启用

### Must Have
- SqliteConfig 包含所有 11 个 WAL 参数
- Flow 和 Task 使用 UUID 作为主键（String(36) 格式）
- Task.messages 和 Task.result 使用 JSON 类型
- Task.flow_uuid 有外键约束（ON DELETE CASCADE）
- 索引覆盖 flow_uuid、state、created_at 字段

### Must NOT Have (Guardrails)
- 不支持环境变量覆盖配置
- 不使用 PostgreSQL 特定类型（保持 SQLite 兼容）
- 不使用 SQLAlchemy Enum 类型（用 String + 应用层验证）
- 不创建额外的配置类或模块（保持简洁）

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest + pytest-asyncio)
- **Automated tests**: Tests-after（先实现，后补测试）
- **Framework**: pytest
- **Agent-Executed QA**: ALWAYS（每个任务执行后直接验证）

### QA Policy
每个任务必须包含 agent-executed QA 场景：
- **配置加载**: 实际加载 YAML 并验证字段值
- **数据库连接**: 实际连接并检查 PRAGMA 值
- **模型创建**: 实际创建表并验证结构
- **迁移执行**: 实际运行 alembic upgrade

---

## Execution Strategy

### Sequential Execution Flow

```
Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6

原因：任务间有强依赖关系
- Task 1 (Config models) 必须先完成，Task 2 (YAML config) 才能验证
- Task 2 (YAML config) 必须先完成，Task 3 (Connection) 才能加载配置
- Task 3 (Connection) 必须先完成，Task 4-5 (Models) 才能使用数据库
- Task 4-5 (Models) 必须先完成，Task 6 (Migration) 才能生成迁移
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|------------|--------|
| 1 | — | 2 |
| 2 | 1 | 3 |
| 3 | 2 | 4, 5 |
| 4 | 3 | 6 |
| 5 | 3 | 6 |
| 6 | 4, 5 | — |

### Agent Dispatch Summary

- **Task 1**: quick (Pydantic 模型扩展)
- **Task 2**: quick (YAML 配置更新)
- **Task 3**: unspecified-high (数据库连接逻辑复杂)
- **Task 4**: quick (Flow 模型定义)
- **Task 5**: quick (Task 模型定义)
- **Task 6**: unspecified-high (Alembic 迁移生成)

---

## TODOs

- [x] 1. 扩展 Pydantic 配置模型

  **What to do**:
  - 在 `src/madousho/config/models.py` 中添加 `SqliteConfig` 类（11 个字段）
  - 添加 `DatabaseConfig` 类（url + sqlite 字段）
  - 在 `Config` 类中添加 `database` 字段（可选，有默认值）
  - 确保所有字段有合理的默认值
  
  **Must NOT do**:
  - 不要添加环境变量支持
  - 不要修改现有配置字段（api, provider, default_model_group, model_groups）
  - 不要使用复杂的验证逻辑（保持简单）

  **Recommended Agent Profile**:
  - **Category**: quick
  - **Skills**: []
  - **Reason**: 纯 Pydantic 模型定义，模式固定

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 1)
  - **Blocks**: Task 2
  - **Blocked By**: None

  **References**:
  - `src/madousho/config/models.py` - 现有 Pydantic 模型结构
  - `src/madousho/config/loader.py` - 配置加载逻辑（了解如何被使用）

  **Acceptance Criteria**:
  - [x] SqliteConfig 类有 11 个字段（wal_enabled, synchronous, cache_size, temp_store, mmap_size, journal_size_limit, pool_size, pool_timeout, pool_recycle, busy_timeout, foreign_keys）
  - [x] DatabaseConfig 类有 url 和 sqlite 字段
  - [x] Config 类有 database 字段（default_factory=DatabaseConfig）
  - [x] 所有字段有正确的类型注解和默认值
  - [x] pytest 可导入模块无错误

  **QA Scenarios**:
  ```
  Scenario: 验证 SqliteConfig 默认值
    Tool: Bash (Python REPL)
    Preconditions: 在虚拟环境中
    Steps:
      1. 运行：python -c "from src.madousho.config.models import SqliteConfig; c = SqliteConfig(); print(c.wal_enabled, c.synchronous, c.cache_size)"
      2. 断言输出包含：True NORMAL -64000
    Expected Result: 默认值正确输出
    Evidence: .sisyphus/evidence/task-1-default-values.txt
  ```

  **Commit**: YES (groups with 2)
  - Message: `feat(config): add SQLite WAL configuration models`
  - Files: `src/madousho/config/models.py`
  - Pre-commit: `pytest tests/test_config.py -v`

---

- [x] 2. 更新 config/madousho.yaml 示例

  **What to do**:
  - 在 `config/madousho.yaml` 中添加 `database` 配置段
  - 在 `config/madousho.example.yaml` 中添加完整注释的配置示例
  - 包含所有 SQLite WAL 参数的注释说明
  
  **Must NOT do**:
  - 不要修改现有 api 和 provider 配置
  - 不要添加环境变量说明
  - 不要改变文件结构

  **Recommended Agent Profile**:
  - **Category**: quick
  - **Skills**: []
  - **Reason**: YAML 文件编辑，模式固定

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 2)
  - **Blocks**: Task 3
  - **Blocked By**: Task 1

  **References**:
  - `config/madousho.yaml` - 当前配置文件
  - `config/madousho.example.yaml` - 示例配置文件
  - Task 1 输出 - SqliteConfig 字段列表

  **Acceptance Criteria**:
  - [x] madousho.yaml 包含 database.url 和 database.sqlite 配置
  - [x] madousho.example.yaml 包含所有 11 个 SQLite 参数的注释
  - [x] YAML 语法正确（可被 yaml.safe_load 解析）
  - [x] 配置可通过 Pydantic 模型验证

  **QA Scenarios**:
  ```
  Scenario: 验证 YAML 配置可加载
    Tool: Bash (Python)
    Preconditions: 在虚拟环境中
    Steps:
      1. 运行：python -c "from src.madousho.config.loader import init_config; c = init_config(); print(c.database.url, c.database.sqlite.wal_enabled)"
      2. 断言输出包含：sqlite:/// True
    Expected Result: 配置成功加载，无验证错误
    Evidence: .sisyphus/evidence/task-2-yaml-load.txt
  ```

  **Commit**: YES (groups with 1)
  - Message: `feat(config): add SQLite WAL configuration models`
  - Files: `src/madousho/config/models.py, config/madousho.yaml, config/madousho.example.yaml`
  - Pre-commit: `pytest tests/test_config.py -v`

---

- [x] 3. 更新 database/connection.py 应用 WAL 配置

  **What to do**:
  - 修改 `Database.init()` 方法，接受 `sqlite_config` 参数
  - 添加 SQLite PRAGMA 配置逻辑（在连接时执行）
  - 使用 SQLAlchemy event.listens_for 在 connect 时设置 PRAGMA
  - 添加日志输出确认 WAL 模式已启用
  - 应用连接池配置（pool_size, pool_timeout, pool_recycle）
  
  **Must NOT do**:
  - 不要改变单例模式结构
  - 不要移除现有的 session 方法
  - 不要添加 PostgreSQL 特定逻辑

  **Recommended Agent Profile**:
  - **Category**: unspecified-high
  - **Skills**: []
  - **Reason**: 数据库连接逻辑复杂，需要理解 SQLAlchemy event 系统

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 3)
  - **Blocks**: Task 4, Task 5
  - **Blocked By**: Task 2

  **References**:
  - `src/madousho/database/connection.py` - 现有连接实现
  - `src/madousho/database/base_model.py` - Base 模型
  - SQLAlchemy docs: https://docs.sqlalchemy.org/en/20/core/events.html

  **Acceptance Criteria**:
  - [x] Database.init() 接受 sqlite_config 参数（Optional[dict]）
  - [x] 当 database_url 以 sqlite 开头时，应用 WAL PRAGMA
  - [x] 日志输出 "SQLite WAL mode enabled"
  - [x] 连接池配置正确应用
  - [x] 非 SQLite 数据库不受影响

  **QA Scenarios**:
  ```
  Scenario: 验证 WAL 模式启用
    Tool: Bash (Python)
    Preconditions: 数据库未初始化
    Steps:
      1. 运行 Python 脚本初始化数据库（带 sqlite_config）
      2. 执行：PRAGMA journal_mode 查询
      3. 断言结果为：wal
    Expected Result: WAL 模式已启用
    Evidence: .sisyphus/evidence/task-3-wal-enabled.txt
  ```

  **Commit**: YES
  - Message: `feat(database): apply SQLite WAL configuration on connection`
  - Files: `src/madousho/database/connection.py`
  - Pre-commit: `pytest tests/test_database.py -v`

---

- [x] 4. 创建 Flow 模型

  **What to do**:
  - 创建 `src/madousho/models/flow.py`
  - 定义 Flow 类继承 BaseModel
  - 字段：uuid (主键), name, description, plugin, tasks (JSON), created_at, updated_at
  - 使用 String(36) 存储 UUID（跨数据库兼容）
  - tasks 字段使用 JSON 类型存储任务 UUID 列表
  
  **Must NOT do**:
  - 不使用 UUID 类型（保持 SQLite 兼容）
  - 不创建与 Task 的双向关系（单向即可）
  - 不添加业务逻辑方法（保持纯数据模型）

  **Recommended Agent Profile**:
  - **Category**: quick
  - **Skills**: []
  - **Reason**: 标准 SQLAlchemy 模型定义

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 5)
  - **Parallel Group**: Wave 2 (with Task 5)
  - **Blocks**: Task 6
  - **Blocked By**: Task 3

  **References**:
  - `src/madousho/database/base_model.py` - BaseModel 基类
  - `src/madousho/config/models.py` - Pydantic 模型参考（字段命名）
  - SQLAlchemy docs: https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html

  **Acceptance Criteria**:
  - [x] Flow 类继承 BaseModel
  - [x] uuid 字段为 String(36) 主键
  - [x] name 字段为 String(255) 非空
  - [x] description 字段为 Text 可选
  - [x] plugin 字段为 String(255) 非空
  - [x] tasks 字段为 JSON 类型（存储 UUID 列表）
  - [x] created_at 和 updated_at 继承自 BaseModel
  - [x] __tablename__ = "flows"

  **QA Scenarios**:
  ```
  Scenario: 验证 Flow 表结构
    Tool: Bash (Python)
    Preconditions: 数据库已初始化
    Steps:
      1. 导入 Flow 模型
      2. 执行：Flow.__table__.columns.keys()
      3. 断言包含：uuid, name, description, plugin, tasks, created_at, updated_at
    Expected Result: 所有字段存在
    Evidence: .sisyphus/evidence/task-4-flow-columns.txt
  ```

  **Commit**: YES (groups with 5)
  - Message: `feat(models): add Flow and Task SQLAlchemy models`
  - Files: `src/madousho/models/flow.py, src/madousho/models/task.py, src/madousho/models/__init__.py`
  - Pre-commit: `python -c "from src.madousho.models import Flow, Task"`

---

- [x] 5. 创建 Task 模型

  **What to do**:
  - 创建 `src/madousho/models/task.py`
  - 定义 Task 类继承 BaseModel
  - 字段：uuid (主键), flow_uuid (外键), label, state, timeout, messages (JSON), result (JSON), error (JSON), created_at, started_at, completed_at, updated_at
  - state 字段用 String(20)，应用层验证枚举值
  - flow_uuid 有外键约束指向 Flow.uuid (ON DELETE CASCADE)
  - 添加索引：flow_uuid, state, created_at
  
  **Must NOT do**:
  - 不使用 SQLAlchemy Enum 类型
  - 不创建复杂的双向关系
  - 不添加业务逻辑方法

  **Recommended Agent Profile**:
  - **Category**: quick
  - **Skills**: []
  - **Reason**: 标准 SQLAlchemy 模型定义

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 4)
  - **Parallel Group**: Wave 2 (with Task 4)
  - **Blocks**: Task 6
  - **Blocked By**: Task 3

  **References**:
  - `src/madousho/database/base_model.py` - BaseModel 基类
  - Task 4 输出 - Flow 模型结构
  - SQLAlchemy docs: https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html

  **Acceptance Criteria**:
  - [x] Task 类继承 BaseModel
  - [x] uuid 字段为 String(36) 主键
  - [x] flow_uuid 字段为 String(36) 外键（ON DELETE CASCADE）
  - [x] label 字段为 String(255) 非空
  - [x] state 字段为 String(20) 非空
  - [x] timeout 字段为 Float 可选
  - [x] messages/result/error 字段为 JSON 类型
  - [x] started_at 和 completed_at 为 DateTime 可选
  - [x] 索引：idx_task_flow_uuid, idx_task_state, idx_task_created_at
  - [x] __tablename__ = "tasks"

  **QA Scenarios**:
  ```
  Scenario: 验证 Task 表结构和索引
    Tool: Bash (Python)
    Preconditions: 数据库已初始化
    Steps:
      1. 导入 Task 模型
      2. 执行：Task.__table__.columns.keys() 和 Task.__table__.indexes
      3. 断言字段和索引存在
    Expected Result: 所有字段和索引正确
    Evidence: .sisyphus/evidence/task-5-task-columns.txt
  ```

  **Commit**: YES (groups with 4)
  - Message: `feat(models): add Flow and Task SQLAlchemy models`
  - Files: `src/madousho/models/flow.py, src/madousho/models/task.py, src/madousho/models/__init__.py`
  - Pre-commit: `python -c "from src.madousho.models import Flow, Task"`

---

- [x] 6. 创建 Alembic 迁移脚本

  **What to do**:
  - 运行 `alembic revision --autogenerate -m "create flows and tasks tables"`
  - 检查生成的迁移文件确保：
    - flows 表结构正确（uuid, name, description, plugin, tasks, timestamps）
    - tasks 表结构正确（uuid, flow_uuid FK, label, state, timeout, JSON fields, timestamps）
    - 索引正确创建
    - 外键约束正确（ON DELETE CASCADE）
  - 手动调整迁移文件（如需要）
  - 运行 `alembic upgrade head` 应用迁移
  - 验证表已创建
  
  **Must NOT do**:
  - 不要手动编写 SQL（用 Alembic op.* API）
  - 不要修改现有迁移（versions/ 为空）
  - 不要跳过验证步骤

  **Recommended Agent Profile**:
  - **Category**: unspecified-high
  - **Skills**: []
  - **Reason**: Alembic 迁移需要验证表结构正确性

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 6)
  - **Blocks**: None (final task)
  - **Blocked By**: Task 4, Task 5

  **References**:
  - `alembic/env.py` - Alembic 环境配置
  - `alembic.ini` - Alembic 配置文件
  - `src/madousho/models/` - 模型定义目录
  - Alembic docs: https://alembic.sqlalchemy.org/en/latest/autogenerate.html

  **Acceptance Criteria**:
  - [x] alembic/versions/ 下有新的迁移文件
  - [x] 迁移文件包含 create_table('flows', ...) 和 create_table('tasks', ...)
  - [x] 外键约束包含 ondelete='CASCADE'
  - [x] 索引正确创建（create_index）
  - [x] alembic upgrade head 成功执行
  - [x] 数据库中 flows 和 tasks 表存在

  **QA Scenarios**:
  ```
  Scenario: 验证迁移执行成功
    Tool: Bash (alembic + sqlite3)
    Preconditions: 数据库文件不存在或为空
    Steps:
      1. 删除旧的数据库文件（如果存在）
      2. 运行：alembic upgrade head
      3. 运行：sqlite3 madousho.db ".tables"
      4. 断言输出包含：flows, tasks, alembic_version
    Expected Result: 表成功创建
    Evidence: .sisyphus/evidence/task-6-migration-success.txt
  
  Scenario: 验证表结构正确
    Tool: Bash (sqlite3)
    Preconditions: 迁移已执行
    Steps:
      1. 运行：sqlite3 madousho.db ".schema flows"
      2. 运行：sqlite3 madousho.db ".schema tasks"
      3. 断言 schema 包含所有字段和索引
    Expected Result: 表结构与设计一致
    Evidence: .sisyphus/evidence/task-6-schema-verify.txt
  ```

  **Commit**: YES
  - Message: `feat(database): create flows and tasks tables via Alembic`
  - Files: `alembic/versions/*.py`
  - Pre-commit: `alembic current` (验证迁移状态)

---

## Final Verification Wave

> 4 review agents run in PARALLEL. ALL must APPROVE.

- [x] F1. **Plan Compliance Audit** — oracle
  验证所有 Must Have 已实现，Must NOT Have 未出现。

- [x] F2. **Code Quality Review** — unspecified-high
  运行 tsc（如有 TS）、pytest、ruff/flake8 检查代码质量。

- [x] F3. **Real Manual QA** — unspecified-high
  实际加载配置、连接数据库、创建表、验证 WAL 模式。

- [x] F4. **Scope Fidelity Check** — deep
  检查每个任务是否按 spec 实现，无范围蔓延。

---

## Commit Strategy

- **1-2**: `feat(config): add SQLite WAL configuration models`
  - Files: `src/madousho/config/models.py, config/madousho.yaml, config/madousho.example.yaml`
  - Pre-commit: `pytest tests/test_config.py -v`

- **3**: `feat(database): apply SQLite WAL configuration on connection`
  - Files: `src/madousho/database/connection.py`
  - Pre-commit: `pytest tests/test_database.py -v`

- **4-5**: `feat(models): add Flow and Task SQLAlchemy models`
  - Files: `src/madousho/models/flow.py, src/madousho/models/task.py, src/madousho/models/__init__.py`
  - Pre-commit: `python -c "from src.madousho.models import Flow, Task"`

- **6**: `feat(database): create flows and tasks tables via Alembic`
  - Files: `alembic/versions/*.py`
  - Pre-commit: `alembic current`

---

## Success Criteria

### Verification Commands
```bash
# 验证配置加载
python -c "from src.madousho.config.loader import init_config; c = init_config(); print(c.database.sqlite.wal_enabled)"  # Expected: True

# 验证 WAL 模式
python -c "from src.madousho.database.connection import Database; db = Database.get_instance(); db.init('sqlite:///./test.db', {'wal_enabled': True}); import sqlite3; conn = sqlite3.connect('test.db'); print(conn.execute('PRAGMA journal_mode').fetchone()[0])"  # Expected: wal

# 验证模型导入
python -c "from src.madousho.models import Flow, Task; print('OK')"  # Expected: OK

# 验证迁移
alembic upgrade head && alembic current  # Expected: 显示最新迁移版本

# 验证表结构
sqlite3 madousho.db ".schema flows" && sqlite3 madousho.db ".schema tasks"  # Expected: 完整 schema 输出
```

### Final Checklist
- [x] 所有 "Must Have" 已实现
- [x] 所有 "Must NOT Have" 未出现
- [x] 所有测试通过（pytest）
- [x] WAL 模式成功启用（PRAGMA journal_mode = wal）
- [x] flows 和 tasks 表创建成功
- [x] 外键和索引正确创建
