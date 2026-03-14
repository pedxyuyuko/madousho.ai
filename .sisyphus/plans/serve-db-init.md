# Serve 命令数据库初始化（最佳实践版）

## TL;DR

> **Quick Summary**: 为 `madousho serve` 命令添加数据库初始化功能，使用 Alembic 迁移管理 schema、自动创建数据库目录、完善错误处理和配置验证。
> 
> **Deliverables**:
> - 更新 `src/madousho/commands/serve.py` 添加数据库初始化逻辑
> - 使用 Alembic 迁移替代 create_all_tables()
> - 添加数据库目录自动创建
> - 添加配置验证和错误处理
> - 添加连接测试验证
> 
> **Estimated Effort**: Medium (due to Alembic integration)
> **Parallel Execution**: NO - sequential (single task)
> **Critical Path**: Task 1

---

## Context

### Original Request
为 serve 命令加入初始化数据库功能

### Interview Summary
**Key Discussions**:
- **初始化步骤**: 连接 + 自动建表
- **配置来源**: 从 YAML 配置文件读取
- **验证策略**: 连接测试

**Research Findings**:
- `Database` 类已有 `init()` 和 `create_all_tables()` 方法可用
- 配置通过 `get_config().database.url` 和 `get_config().database.sqlite` 获取
- 当前 `serve.py` 仅包含配置加载和日志初始化，无数据库相关逻辑

### Metis Review
**Identified Gaps** (addressed):
- 需要确保数据库初始化在日志配置之后（已解决 - 按正确顺序编写）
- SQLite 配置需要转换为字典格式（已解决 - 使用 `model_dump()`）

---

## Work Objectives

### Core Objective
在 `madousho serve` 命令启动时自动初始化数据库连接、创建表结构并验证连接可用性。

### Concrete Deliverables
- `src/madousho/commands/serve.py` - 添加数据库初始化代码

### Definition of Done
- [x] 运行 `madousho serve` 后能看到数据库初始化成功的日志
- [x] 数据库文件自动创建（如不存在）
- [x] 所有表结构自动创建

### Must Have
- 从 YAML 配置文件读取数据库配置
- 调用 `Database.get_instance().init()` 初始化连接
- **使用 Alembic 迁移管理 schema** (替代 create_all_tables())
- **数据库目录不存在时自动创建**
- **在 Pydantic 模型中添加验证器** (URL 格式、SQLite 配置)
- **完善的错误处理和退出码**
- 执行连接测试验证
- 记录初始化日志

### Must NOT Have (Guardrails)
- 不修改现有的数据库模型文件
- **不使用 create_all_tables() 创建表** (已存在 Alembic)
- 不添加新的配置项
- **不忽略 SQLite 连接池配置问题**
- **不在 serve.py 中重复验证逻辑** (Pydantic 已处理)

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest)
- **Automated tests**: NO (此任务为小改动，使用 Agent-Executed QA)
- **Framework**: pytest (现有)
- **Agent-Executed QA**: ALWAYS (mandatory)

### QA Policy
Every task MUST include agent-executed QA scenarios.

- **CLI/TUI**: Use interactive_bash (tmux) — Run command, validate output

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately):
└── Task 1: 为 serve 命令添加数据库初始化 [quick]

Critical Path: Task 1
Parallel Speedup: N/A (single task)
Max Concurrent: 1
```

### Dependency Matrix

- **1**: — — (none)

### Agent Dispatch Summary

- **1**: **1** — T1 → `quick`

---

## TODOs

- [x] 1. 为 serve 命令添加数据库初始化

  **What to do**:
  
  ## Step 1: 在 Pydantic 模型中添加验证器
  
  - 在 `src/madousho/config/models.py` 中添加 field_validator：
  
  ```python
  from pydantic import BaseModel, Field, field_validator
  
  class DatabaseConfig(BaseModel):
      """Database configuration."""
      
      url: str = Field(default="sqlite:///./madousho.db", description="Database connection URL")
      sqlite: SqliteConfig = Field(default_factory=SqliteConfig, description="SQLite-specific configuration")
      
      @field_validator('url')
      @classmethod
      def validate_url_scheme(cls, v: str) -> str:
          """验证数据库 URL 格式"""
          if not v.startswith(("sqlite://", "postgresql://", "mysql://")):
              raise ValueError(f"Invalid database URL scheme: {v}. Must start with sqlite://, postgresql://, or mysql://")
          return v
  
  class SqliteConfig(BaseModel):
      """Configuration for SQLite WAL mode and performance tuning."""
      
      synchronous: str = Field(default="NORMAL", description="Synchronization mode")
      
      @field_validator('synchronous')
      @classmethod
      def validate_synchronous_mode(cls, v: str) -> str:
          """验证 SQLite 同步模式"""
          valid_modes = ("OFF", "NORMAL", "FULL", "EXTRA")
          if v not in valid_modes:
              raise ValueError(f"Invalid synchronous mode: {v}. Must be one of {valid_modes}")
          return v
  ```
  
  ## Step 2: 在 serve.py 中添加数据库初始化
  
  - 在 `src/madousho/commands/serve.py` 中导入必要模块：
  
  ```python
  from madousho.database.connection import Database
  from madousho.config.loader import get_config
  from alembic.config import Config as AlembicConfig
  from alembic import command as alembic_command
  from sqlalchemy import text
  from sqlalchemy.exc import OperationalError, SQLAlchemyError
  from pydantic import ValidationError
  import sys
  import os
  ```
  
  - 添加数据库初始化函数：
  
  ```python
  def ensure_database_directory(database_url: str) -> None:
      """确保数据库文件所在目录存在"""
      if database_url.startswith("sqlite:///"):
          db_path = database_url.replace("sqlite:///", "")
          db_dir = os.path.dirname(db_path)
          if db_dir and not os.path.exists(db_dir):
              os.makedirs(db_dir, exist_ok=True)
              logger.info(f"Database directory created: {db_dir}")
  
  def run_alembic_migrations() -> None:
      """运行 Alembic 迁移到最新版本"""
      alembic_cfg = AlembicConfig("alembic.ini")
      alembic_command.upgrade(alembic_cfg, "head")
      logger.info("Alembic migrations completed")
  
  def init_database() -> None:
      """初始化数据库连接、运行迁移、验证连接"""
      try:
          config = get_config()
      except ValidationError as e:
          logger.error(f"Configuration validation failed: {e}")
          sys.exit(2)
      except FileNotFoundError as e:
          logger.error(f"Configuration file not found: {e}")
          sys.exit(2)
      
      # 确保数据库目录存在
      ensure_database_directory(config.database.url)
      
      # 初始化数据库连接
      db = Database.get_instance()
      db.init(
          database_url=config.database.url,
          sqlite_config=config.database.sqlite.model_dump()
      )
      logger.info(f"Database connection initialized: {config.database.url}")
      
      # 运行 Alembic 迁移
      run_alembic_migrations()
      
      # 连接测试
      try:
          with db.session() as session:
              session.execute(text("SELECT 1"))
          logger.info("Database connection test passed")
      except OperationalError as e:
          logger.error(f"Database connection test failed: {e}")
          sys.exit(1)
      except SQLAlchemyError as e:
          logger.error(f"Database error: {e}")
          sys.exit(1)
      
      logger.info("Database initialization completed successfully")
  ```
  
  - 在 `serve()` 函数中调用 `init_database()`

  **Must NOT do**:
  - 不修改 `serve` 函数签名
  - 不添加新的命令行参数
  - **不在 serve.py 中重复验证逻辑** (Pydantic 已处理)
  - **不使用 create_all_tables()** (必须用 Alembic 迁移)

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: 单一文件修改，逻辑简单直接，已有清晰的实现方案
  - **Skills**: []
    - Reason: 标准 Python/SQLAlchemy 操作，不需要特殊技能

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: None
  - **Blocked By**: None (can start immediately)

  **References** (CRITICAL - Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `src/madousho/commands/serve.py:1-30` - 当前 serve 命令的完整实现
  - `src/madousho/database/connection.py:40-130` - Database 类的 init 和 create_all_tables 方法
  - `src/madousho/config/loader.py:101` - get_config() 函数使用方式
  - `src/madousho/config/models.py:49` - Config 和 DatabaseConfig 模型定义 (需要添加验证器)

  **API/Type References** (contracts to implement against):
  - `src/madousho/config/models.py:49` - Config 和 DatabaseConfig 模型定义
  - `src/madousho/database/connection.py:23` - Database 单例类定义

  **External References** (libraries and frameworks):
  - Pydantic v2 validators: `https://docs.pydantic.dev/latest/concepts/validators/#field-validators`
  - SQLAlchemy 2.0: `https://docs.sqlalchemy.org/en/20/core/connections.html` - 连接执行模式
  - Alembic: `https://alembic.sqlalchemy.org/en/latest/api/command.html` - 迁移命令

  **WHY Each Reference Matters**:
  - `serve.py`: 需要在此文件中添加初始化代码
  - `connection.py`: 提供 Database 类的 API 和使用模式
  - `models.py`: **需要添加 field_validator 装饰器的验证器**
  - `loader.py`: 了解配置加载流程，理解 ValidationError 抛出时机

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** — No human action permitted.

  **QA Scenarios (MANDATORY — task is INCOMPLETE without these):**

  ```
  Scenario: 数据库初始化成功 - 正常启动
    Tool: interactive_bash (tmux)
    Preconditions: 配置文件存在且有效，数据库文件不存在或已存在
    Steps:
      1. 启动 tmux 会话：new-session -d -s serve-test
      2. 运行命令：send-keys -t serve-test "uv run madousho serve" Enter
      3. 等待 5 秒：sleep 5
      4. 查看输出：capture-pane -t serve-test -p
    Expected Result: 日志包含以下关键信息：
      - "Database directory created: ./data" (如果目录不存在)
      - "Database connection initialized: sqlite:///./data/madousho.db"
      - "Alembic migrations completed"
      - "Database connection test passed"
      - "Database initialization completed successfully"
    Failure Indicators: 出现数据库连接错误、迁移失败、配置验证错误
    Evidence: .sisyphus/evidence/task-1-db-init-success.txt

  Scenario: 数据库初始化成功 - 验证数据库文件和表结构
    Tool: Bash
    Preconditions: serve 命令已执行完成
    Steps:
      1. 检查数据库文件是否存在：ls -la ./data/madousho.db
      2. 使用 sqlite3 验证表结构：sqlite3 ./data/madousho.db ".tables"
      3. 验证 alembic_version 表：sqlite3 ./data/madousho.db "SELECT * FROM alembic_version"
    Expected Result: 
      - 数据库文件存在
      - 包含 flow、task、alembic_version 表
      - alembic_version 表有版本号记录
    Failure Indicators: 数据库文件不存在，或表缺失，或 alembic_version 为空
    Evidence: .sisyphus/evidence/task-1-db-file-verify.txt

  Scenario: 数据库目录自动创建
    Tool: Bash
    Preconditions: 删除 ./data 目录（如果存在）
    Steps:
      1. 删除目录：rm -rf ./data
      2. 运行 serve 命令：uv run madousho serve
      3. 检查目录是否被自动创建：ls -la ./data
    Expected Result: ./data 目录被自动创建，数据库文件在其中
    Failure Indicators: 目录未创建，或命令因目录不存在而失败
    Evidence: .sisyphus/evidence/task-1-db-dir-auto-create.txt

  Scenario: 配置错误 - 无效数据库 URL
    Tool: interactive_bash (tmux)
    Preconditions: 修改配置文件使用无效的 database.url
    Steps:
      1. 备份配置文件：cp config/app.yaml config/app.yaml.bak
      2. 修改配置：sed -i 's|url: "sqlite:.*|url: "invalid://url"|' config/app.yaml
      3. 运行命令：uv run madousho serve
      4. 恢复配置：mv config/app.yaml.bak config/app.yaml
    Expected Result: 
      - 日志包含 "Configuration validation failed:" (Pydantic ValidationError)
      - 命令以退出码 2 退出
    Failure Indicators: 命令未检测到配置错误，或退出码不正确
    Evidence: .sisyphus/evidence/task-1-db-config-error.txt
  ```

  **Evidence to Capture**:
  - [x] serve 启动日志输出（包含数据库初始化信息）
  - [x] 数据库文件存在性验证
  - [x] 数据库表结构验证

  **Commit**: YES
  - Message: `feat(serve): add database initialization with Alembic migrations`
  - Files: `src/madousho/commands/serve.py`, `src/madousho/config/models.py`
  - Pre-commit: `pytest tests/`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, curl endpoint, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run `tsc --noEmit` + linter + `bun test`. Review all changed files for: `as any`/`@ts-ignore`, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names (data/result/item/temp).
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high` (+ `playwright` skill if UI)
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration (features working together, not isolation). Test edge cases: empty state, invalid input, rapid actions. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination: Task N touching Task M's files. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **1**: `feat(serve): add database initialization with Alembic migrations` — src/madousho/commands/serve.py, src/madousho/config/models.py, pytest tests/

---

## Success Criteria

### Verification Commands
```bash
# 1. 正常启动验证
uv run madousho serve
# Expected: 日志包含：
#   - "Database connection initialized"
#   - "Alembic migrations completed"
#   - "Database connection test passed"
#   - "Database initialization completed successfully"

# 2. 数据库文件验证
ls -la ./data/madousho.db
# Expected: 数据库文件存在

# 3. 表结构验证
sqlite3 ./data/madousho.db ".tables"
# Expected: 包含 flow, task, alembic_version 表

# 4. Alembic 版本验证
sqlite3 ./data/madousho.db "SELECT * FROM alembic_version"
# Expected: 有版本号记录

# 5. 数据库目录自动创建验证
rm -rf ./data && uv run madousho serve && ls -la ./data
# Expected: 目录被自动创建
```

### Final Checklist
- [x] 所有 "Must Have" 实现
- [x] 所有 "Must NOT Have" 遵守
- [x] 所有测试通过
- [x] Alembic 迁移正常运行
- [x] 数据库目录自动创建
- [x] 配置验证有效
- [x] 错误处理完善（退出码正确）
