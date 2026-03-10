# 数据库管理类实现 - 单例模式

## TL;DR

> **Quick Summary**: 实现一个基于 SQLAlchemy 的 Database 单例类，支持一次初始化、全局访问，提供基础 CRUD 操作和自动表结构创建。
> 
> **Deliverables**: 
> - `src/madousho/database/__init__.py` - 模块导出
> - `src/madousho/database/connection.py` - Database 单例类
> - `src/madousho/database/models.py` - 基础模型定义
> - `alembic/` - Alembic 迁移配置
> 
> **Estimated Effort**: Short (2-3 hours)
> **Parallel Execution**: NO - sequential (small scope)
> **Critical Path**: 目录创建 → Database 类 → 基础模型 → Alembic 配置 → 测试验证

---

## Context

### Original Request
实现一个数据库管理 class，要求是一次 init 到处使用，最好用 class 实现。

### Interview Summary
**Key Discussions**:
- **数据库类型**: SQLite（轻量级，无需额外服务）
- **使用场景**: 数据持久化、缓存层、日志记录
- **功能需求**: 基础 CRUD、自动迁移
- **核心要求**: 单例模式，class 实现

**Research Findings**:
- 项目已安装 SQLAlchemy 2.0+ 和 Alembic
- 当前项目未使用数据库功能
- Python 项目，使用 Typer CLI 框架

### Metis Review
**Identified Gaps** (addressed):
- **范围简化**: 不实现连接池、加密、多数据库支持
- **并发处理**: 使用 SQLAlchemy 线程安全 Session 工厂
- **错误处理**: 基础异常捕获 + 日志记录
- **验收标准**: 明确 5 项核心功能验证

---

## Work Objectives

### Core Objective
实现一个线程安全的 Database 单例类，提供 Session 上下文管理器和自动表结构创建。
实现一个线程安全的 Database 单例类，提供统一的数据库访问接口，支持基础 CRUD 和自动表结构管理。

### Concrete Deliverables
- `src/madousho/database/__init__.py` - 模块导出
- `src/madousho/database/connection.py` - Database 单例类（~150 行）
- `src/madousho/database/models.py` - DeclarativeBase 和基础模型
- `alembic.ini` - Alembic 配置文件
- `alembic/` - 迁移脚本目录

### Definition of Done
- [x] `Database.get_instance()` 返回同一实例（Python 验证）
- [x] `bun run pytest tests/test_database.py` 通过（5+ 测试）
- [x] 自动创建表结构（运行后检查 SQLite 文件）
- [x] 支持上下文管理器 `with db.session() as session`

### Must Have
- 单例模式实现
- 线程安全的 Session 工厂
- Session 上下文管理器 (`with db.session() as session`)
- 自动表结构创建
- 优雅的错误处理
- 单例模式实现
- 线程安全的 Session 工厂
- 自动表结构创建
- 优雅的错误处理

### Must NOT Have (Guardrails)
- ❌ 不实现连接池（SQLite 单连接）
- ❌ 不实现数据库加密
- ❌ 不实现多数据库支持
- ❌ 不实现复杂查询构建器
- ❌ 不实现自动重连逻辑

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO
- **Automated tests**: YES (Tests-after)
- **Framework**: pytest (需安装)
- **Agent-Executed QA**: ALWAYS (mandatory for all tasks)

### QA Policy
每个任务包含 agent-executed QA scenarios：
- **Python 代码**: 使用 Bash 运行 pytest/Python 脚本验证
- **文件创建**: 使用 Bash 检查文件存在性和内容
- **数据库操作**: 使用 Python 脚本验证 CRUD 操作

---

## Execution Strategy

### Sequential Execution (Small Scope)

```
Wave 1 (Start Immediately — all tasks sequential):
├── Task 1: 创建目录结构和 __init__.py [quick]
├── Task 2: 实现 Database 单例类 [unspecified-high]
├── Task 3: 定义基础模型类 [quick]
├── Task 4: 配置 Alembic 自动迁移 [quick]
├── Task 5: 编写测试文件 [unspecified-high]
└── Task 6: 运行测试验证 [quick]

Critical Path: 1 → 2 → 3 → 4 → 5 → 6
Parallel Speedup: N/A (small sequential project)
Max Concurrent: 1
```

### Dependency Matrix

- **1**: — — 2, 3
- **2**: 1 — 4, 5
- **3**: 1 — 5
- **4**: 2 — 6
- **5**: 2, 3 — 6
- **6**: 4, 5 — Done

### Agent Dispatch Summary

- **Wave 1**: 
  - T1 → `quick`
  - T2 → `unspecified-high`
  - T3 → `quick`
  - T4 → `quick`
  - T5 → `unspecified-high`
  - T6 → `quick`

---

## TODOs

- [x] 1. 创建数据库目录结构和模块导出

  **What to do**:
  - 创建 `src/madousho/database/` 目录
  - 创建 `src/madousho/database/__init__.py`，导出 Database 类和 Base/BaseModel
  - 创建 `alembic/` 目录（空目录，后续配置）
  
  **Must NOT do**:
  - 不创建其他文件
  - 不实现任何逻辑

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `[]`
  - **Reason**: 简单的目录和文件创建

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Tasks 2, 3
  - **Blocked By**: None

  **References**:
  - `src/madousho/config/__init__.py` - 参考模块导出模式
  - `src/madousho/` - 参考项目目录结构

  **Acceptance Criteria**:
  - [x] `src/madousho/database/` 目录存在
  - [x] `src/madousho/database/__init__.py` 存在
  - [x] `alembic/` 目录存在

  **QA Scenarios**:

  ```
  Scenario: 验证目录结构
    Tool: Bash
    Preconditions: 无
    Steps:
      1. 运行：ls -la src/madousho/database/
      2. 运行：ls -la alembic/
    Expected Result: 两个目录都存在，__init__.py 存在
    Failure Indicators: 目录或文件不存在
    Evidence: .sisyphus/evidence/task-1-dir-structure.txt
  ```

  **Commit**: YES (groups with 2, 3)
  - Message: `feat(database): add database module structure`
  - Files: `src/madousho/database/__init__.py`, `src/madousho/database/base_model.py`, `alembic/`
  - Pre-commit: `python -c "from src.madousho.database import Database"`

---

- [x] 2. 实现 Database 单例类

  **What to do**:
  - 实现 `Database` 类，使用类属性 `_instance` 实现单例
  - 实现 `get_instance()` 类方法获取唯一实例
  - 实现 `init(database_url: str)` 方法初始化数据库连接
  - 实现 `is_initialized()` 属性检查是否已初始化
  - 实现 `get_engine()` 返回 SQLAlchemy engine
  - 实现 `session()` 上下文管理器，支持 `with` 语句（自动 commit/rollback）
  - 实现 `dispose()` 方法关闭连接（用于测试清理）
  - 实现 `create_all_tables()` 方法自动创建表结构
  - SQLite 配置：`connect_args={"check_same_thread": False}`
  - 添加适当的错误处理：捕获 SQLAlchemyError → 记录日志 → 重新抛出

  **Must NOT do**:
  - 不实现连接池
  - 不实现异步支持
  - 不实现多数据库连接
  - 不实现复杂的查询构建器
  - 不实现通用 CRUD 方法（add/get/update/delete/list）
  - 实现 `Database` 类，使用类属性 `_instance` 实现单例
  - 实现 `get_instance()` 类方法获取唯一实例
  - 实现 `init(database_url: str)` 方法初始化数据库连接
  - 实现 `get_engine()` 返回 SQLAlchemy engine
  - 实现 `get_session_factory()` 返回线程安全的 Session 工厂
  - 实现 `get_session()` 上下文管理器，支持 `with` 语句
  - 实现基础 CRUD 方法：`add()`, `get()`, `update()`, `delete()`, `list()`
  - 实现 `create_all_tables()` 方法自动创建表结构
  - 添加适当的错误处理和日志记录

  **Must NOT do**:
  - 不实现连接池
  - 不实现异步支持
  - 不实现多数据库连接
  - 不实现复杂的查询构建器

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`
  - **Reason**: 核心类实现，需要理解 SQLAlchemy 2.0+ API 和单例模式

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Tasks 4, 5
  - **Blocked By**: Task 1

  **References**:
  - SQLAlchemy 官方文档：https://docs.sqlalchemy.org/en/20/orm/session_basics.html
  - `src/madousho/config/loader.py` - 参考类实现风格
  - Python 单例模式：https://refactoring.guru/design-patterns/singleton/python/example

  **Acceptance Criteria**:
  - [x] `Database.get_instance()` 返回同一实例
  - [x] `db.init("sqlite:///./test.db")` 成功初始化
  - [x] `with db.session() as session:` 支持上下文管理
  - [x] `create_all_tables()` 成功创建表
  - [x] `db.is_initialized()` 返回 True（初始化后）
  - [x] `db.dispose()` 成功关闭连接
  - [x] `Database.get_instance()` 返回同一实例
  - [x] `db.init("sqlite:///./test.db")` 成功初始化
  - [x] `with db.get_session() as session:` 支持上下文管理
  - [x] CRUD 方法可用：add, get, update, delete, list
  - [x] `create_all_tables()` 成功创建表

  ```
  Scenario: 验证单例模式
    Tool: Bash (Python script)
    Preconditions: 无
    Steps:
      1. 运行 Python 脚本：
         from src.madousho.database import Database
         db1 = Database.get_instance()
         db2 = Database.get_instance()
         assert db1 is db2, "不是单例"
         print("✓ 单例验证通过")
    Expected Result: db1 和 db2 是同一实例
    Failure Indicators: assert 失败
    Evidence: .sisyphus/evidence/task-2-singleton-test.txt

  Scenario: 验证 Session 管理器
    Tool: Bash (Python script)
    Preconditions: Database 已初始化
    Steps:
      1. 运行 Python 脚本：
         from src.madousho.database import Database, Base
         db = Database.get_instance()
         db.init("sqlite:///./test.db")
         Base.metadata.create_all(db.get_engine())
         
         with db.session() as session:
             # 验证 session 可用
             assert session is not None
             # 验证自动 commit（无异常即成功）
         
         print("✓ Session 管理器验证通过")
    Expected Result: Session 正常工作，自动 commit/rollback
    Failure Indicators: 抛出异常或 session 为 None
    Evidence: .sisyphus/evidence/task-2-session-test.txt
  ```

  ```
  Scenario: 验证单例模式
    Tool: Bash (Python script)
    Preconditions: 无
    Steps:
      1. 运行 Python 脚本：
         from src.madousho.database import Database
         db1 = Database.get_instance()
         db2 = Database.get_instance()
         assert db1 is db2, "不是单例"
         print("✓ 单例验证通过")
    Expected Result: db1 和 db2 是同一实例
    Failure Indicators: assert 失败
    Evidence: .sisyphus/evidence/task-2-singleton-test.txt

  Scenario: 验证 CRUD 操作
    Tool: Bash (Python script)
    Preconditions: Database 已初始化，有测试模型
    Steps:
      1. 创建测试模型实例
      2. 调用 db.add(session, instance)
      3. 调用 db.get(session, Model, id)
      4. 调用 db.update(session, instance, data)
      5. 调用 db.delete(session, instance)
      6. 验证操作成功
    Expected Result: 所有 CRUD 操作成功，无异常
    Failure Indicators: 抛出异常或数据不正确
    Evidence: .sisyphus/evidence/task-2-crud-test.txt
  ```

  **Evidence to Capture**:
  - [x] Python 脚本输出
  - [x] 测试日志

  **Commit**: YES (groups with 1, 3)
  - Message: `feat(database): implement Database singleton class`
  - Files: `src/madousho/database/connection.py`
  - Pre-commit: `python -c "from src.madousho.database import Database; db = Database.get_instance(); print('OK')"`

---

- [x] 3. 定义基础模型类

  **What to do**:
  - 创建 `src/madousho/database/base_model.py`
  - 创建 `DeclarativeBase` 类（命名为 `Base`）
  - 定义 `BaseModel` 抽象基类（`__abstract__ = True`），包含可选的通用字段：
    - `id`: Integer, primary key, auto-increment (可选)
    - `created_at`: DateTime, default=utcnow (可选)
    - `updated_at`: DateTime, onupdate=utcnow (可选)
  - 注意：`id` 字段不是必需的，用户可以用 UUID 或其他主键
  - 导出 `Base` 和 `BaseModel` 供其他模型继承

  **Must NOT do**:
  - 不强制要求 `id` 字段
  - 不定义具体的业务模型


  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `[]`
  - **Reason**: 简单的模型定义

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 5
  - **Blocked By**: Task 1

  **References**:
  - SQLAlchemy 2.0 风格：https://docs.sqlalchemy.org/en/20/orm/declarative_configurations.html
  - `src/madousho/config/models.py` - 参考 Pydantic 模型定义风格

  **Acceptance Criteria**:
  - [x] `Base` 类可导出
  - [x] `BaseModel` 是抽象基类（`__abstract__ = True`）
  - [x] 可以选择性继承 id/created_at/updated_at 字段
  - [x] 可以继承 `BaseModel` 创建新模型（不强制用 id）

  ```
  Scenario: 验证模型继承
    Tool: Bash (Python script)
    Preconditions: 无
    Steps:
      1. 运行 Python 脚本：
         from src.madousho.database import Base, BaseModel
         
         # 测试 1: 使用 id 的模型
         class ModelWithId(BaseModel):
             __tablename__ = "model_with_id"
             name = Column(String(50))
         
         # 测试 2: 不用 id，用 UUID 的模型
         import uuid
         class ModelWithUuid(Base):
             __tablename__ = "model_with_uuid"
             id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
             name = Column(String(50))
         
         # 验证两种模式都可用
         assert hasattr(ModelWithId, "id")  # 可选
         assert ModelWithUuid.__tablename__ == "model_with_uuid"
         print("✓ 模型继承验证通过")
    Expected Result: 支持 id 和 UUID 两种主键模式
    Failure Indicators: assert 失败或 AttributeError
    Evidence: .sisyphus/evidence/task-3-model-inheritance.txt
  ```

  ```
  Scenario: 验证模型继承
    Tool: Bash (Python script)
    Preconditions: 无
    Steps:
      1. 运行 Python 脚本：
         from src.madousho.database import Base, BaseModel
         class TestModel(BaseModel):
             __tablename__ = "test"
             name = Column(String(50))
         assert TestModel.__tablename__ == "test"
         assert hasattr(TestModel, "id")
         assert hasattr(TestModel, "created_at")
         print("✓ 模型继承验证通过")
    Expected Result: 成功继承 BaseModel，包含所有字段
    Failure Indicators: assert 失败或 AttributeError
    Evidence: .sisyphus/evidence/task-3-model-inheritance.txt
  ```

  **Evidence to Capture**:
  - [x] Python 脚本输出

  **Commit**: YES (groups with 1, 2)
  - Message: `feat(database): add base model definitions`
  - Files: `src/madousho/database/base_model.py`
  - Pre-commit: `python -c "from src.madousho.database import Base, BaseModel; print('OK')"`

---

- [x] 4. 配置 Alembic 自动迁移

  **What to do**:
  - 创建 `alembic.ini` 配置文件
  - 创建 `alembic/env.py` 环境配置
  - 配置 `script.py.mako` 模板
  - 创建第一个迁移脚本（初始表结构）
  - 实现 `db.create_all_tables()` 使用 Alembic 或直接 SQLAlchemy

  **Must NOT do**:
  - 不实现复杂的迁移回滚
  - 不实现多版本管理

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `[]`
  - **Reason**: 标准 Alembic 配置

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 6
  - **Blocked By**: Task 2

  **References**:
  - Alembic 官方文档：https://alembic.sqlalchemy.org/en/latest/tutorial.html
  - `pyproject.toml` - 检查已安装的 Alembic 版本

  **Acceptance Criteria**:
  - [x] `alembic.ini` 存在且配置正确
  - [x] `alembic/env.py` 存在
  - [x] `alembic/versions/` 目录存在
  - [x] `db.create_all_tables()` 成功创建表

  **QA Scenarios**:

  ```
  Scenario: 验证表结构创建
    Tool: Bash (Python script)
    Preconditions: Database 已初始化
    Steps:
      1. 运行 Python 脚本：
         from src.madousho.database import Database, Base
         db = Database.get_instance()
         db.init("sqlite:///./test.db")
         Base.metadata.create_all(db.get_engine())
         # 检查 SQLite 文件
         import os
         assert os.path.exists("./test.db")
         print("✓ 表结构创建验证通过")
    Expected Result: SQLite 文件创建成功
    Failure Indicators: 文件不存在或抛出异常
    Evidence: .sisyphus/evidence/task-4-table-creation.txt
  ```

  **Evidence to Capture**:
  - [x] Python 脚本输出
  - [x] SQLite 文件存在性检查

  **Commit**: YES (单独提交)
  - Message: `feat(database): configure Alembic migrations`
  - Files: `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`
  - Pre-commit: `python -c "import alembic; print('OK')"`

---

- [x] 5. 编写测试文件

  **What to do**:
  - 创建 `tests/test_database.py`
  - 编写单例模式测试
  - 编写 CRUD 操作测试
  - 编写 Session 管理测试
  - 编写表结构创建测试

  **Must NOT do**:
  - 不测试边缘情况（超时、并发等）
  - 不实现性能测试

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`
  - **Reason**: 需要理解 pytest 和 SQLAlchemy 测试模式

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 6
  - **Blocked By**: Tasks 2, 3

  **References**:
  - `tests/` - 检查现有测试目录结构
  - pytest 官方文档：https://docs.pytest.org/en/latest/getting-started.html

  **Acceptance Criteria**:
  - [x] `tests/test_database.py` 存在
  - [x] 包含至少 5 个测试函数
  - [x] 所有测试通过

  **QA Scenarios**:

  ```
  Scenario: 运行测试套件
    Tool: Bash
    Preconditions: pytest 已安装
    Steps:
      1. 运行：pytest tests/test_database.py -v
      2. 验证输出包含 "passed"
    Expected Result: 所有测试通过
    Failure Indicators: 测试失败或错误
    Evidence: .sisyphus/evidence/task-5-pytest-output.txt
  ```

  **Evidence to Capture**:
  - [x] pytest 输出

  **Commit**: YES (单独提交)
  - Message: `test(database): add database unit tests`
  - Files: `tests/test_database.py`
  - Pre-commit: `pytest tests/test_database.py -v`

---

- [x] 6. 运行测试验证

  **What to do**:
  - 安装 pytest（如果未安装）
  - 运行所有测试
  - 验证代码覆盖率（可选）
  - 清理测试文件（test.db）

  **Must NOT do**:
  - 不修改代码（测试失败应返回 Task 5 修复）

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `[]`
  - **Reason**: 简单的命令执行

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: None
  - **Blocked By**: Tasks 4, 5

  **References**:
  - `pyproject.toml` - 检查测试命令配置

  **Acceptance Criteria**:
  - [x] `pytest tests/test_database.py -v` 通过
  - [x] 无测试失败
  - [x] 测试文件清理完成

  **QA Scenarios**:

  ```
  Scenario: 最终验证
    Tool: Bash
    Preconditions: 所有代码已实现
    Steps:
      1. 运行：pytest tests/test_database.py -v --tb=short
      2. 运行：rm -f test.db
      3. 验证输出包含 "passed"
    Expected Result: 所有测试通过，无遗留文件
    Failure Indicators: 测试失败或文件未清理
    Evidence: .sisyphus/evidence/task-6-final-verification.txt
  ```

  **Evidence to Capture**:
  - [x] pytest 完整输出
  - [x] 清理命令输出

  **Commit**: NO (验证任务)

---

## Final Verification Wave

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, curl endpoint, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run `tsc --noEmit` + linter + `bun test`. Review all changed files for: `as any`/`@ts-ignore`, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names (data/result/item/temp).
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration (features working together, not isolation). Test edge cases: empty state, invalid input, rapid actions. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination: Task N touching Task M's files. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **1-3**: `feat(database): add database module structure` — __init__.py, connection.py, models.py
- **4**: `feat(database): configure Alembic migrations` — alembic.ini, alembic/env.py
- **5**: `test(database): add database unit tests` — tests/test_database.py

---

## Success Criteria

### Verification Commands
```bash
# 验证单例模式
python -c "from src.madousho.database import Database; db1 = Database.get_instance(); db2 = Database.get_instance(); assert db1 is db2; print('✓ Singleton OK')"

# 运行测试
pytest tests/test_database.py -v

# 验证表结构创建
python -c "from src.madousho.database import Database, Base; db = Database.get_instance(); db.init('sqlite:///./test.db'); Base.metadata.create_all(db.get_engine()); import os; assert os.path.exists('./test.db'); print('✓ Tables OK')"
```

### Final Checklist
- [x] 所有 "Must Have" 实现完成
- [x] 所有 "Must NOT Have" 未实现
- [x] 所有测试通过
- [x] 证据文件完整
- [x] 代码无 AI slop
