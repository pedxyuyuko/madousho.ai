# HTTP API 框架初始化 - FastAPI + Vue 3

## TL;DR

> **Quick Summary**: 为 Madousho.ai 项目初始化 FastAPI HTTP 框架，支持 RESTful API (`/api/v1`) 和 Vue 3 SPA 静态文件服务 (`public/`)。
> 
> **Deliverables**:
> - FastAPI 应用入口 (`src/madousho/api/main.py`) - **version 动态读取** `src.madousho._version.__version__`
> - API 路由模块结构 (`src/madousho/api/routes/`)
> - 依赖注入模块 (`src/madousho/api/deps.py`)
> - 修改 `serve` 命令启动 HTTP 服务器
> - 更新 `pyproject.toml` 添加依赖
> - 配置文件添加 server 配置
> 
> **Estimated Effort**: Short (约 30-45 分钟)
> **Parallel Execution**: NO - sequential (任务间有依赖)
> **Critical Path**: 依赖安装 → API 结构 → serve 命令修改 → 验证

---

## Context

### Original Request
为项目初始化 HTTP API 框架，需求：RESTful API + 静态 SPA 服务。

### Interview Summary
**Key Discussions**:
- **框架选型**: FastAPI (与 Pydantic v2 原生集成，高性能，自动文档)
- **SPA 框架**: Vue 3 + Vite
- **构建目录**: `public/`
- **API 前缀**: `/api/v1`
- **认证**: 暂不需要

**Research Findings**:
- 项目当前无任何 HTTP 框架，干净的起点
- FastAPI 使用 `StaticFiles` + `html=True` 处理 SPA 前端路由
- uvicorn 作为 ASGI 服务器

### Metis Review
**Identified Gaps** (addressed):
- 需确保 `public/` 目录不存在时不报错
- serve 命令需保留原有数据库初始化逻辑
- 配置需支持 host/port 自定义

---

## Work Objectives

### Core Objective
初始化 FastAPI HTTP 框架，提供 RESTful API 和 Vue 3 SPA 静态文件服务能力。

### Concrete Deliverables
- `src/madousho/api/main.py` - FastAPI 应用入口
- `src/madousho/api/routes/__init__.py` - API 路由模块
- `src/madousho/api/deps.py` - 依赖注入 (DB Session)
- `src/madousho/commands/serve.py` - 修改为启动 HTTP 服务器
- `pyproject.toml` - 添加 fastapi, uvicorn 依赖
- `config/app.yaml` - 添加 server 配置

### Definition of Done
- [x] `madousho serve` 启动 HTTP 服务器
- [x] 访问 `http://localhost:8000` 返回 Vue SPA
- [x] 访问 `http://localhost:8000/api/v1/health` 返回健康检查
- [x] `pytest` 测试通过

### Must Have
- FastAPI 应用挂载到 uvicorn
- SPA 静态文件服务 (html=True 处理路由)
- API 路由前缀 `/api/v1`
- 健康检查端点

### Must NOT Have (Guardrails)
- 不要添加认证逻辑 (用户明确说不需要)
- 不要修改数据库模型
- 不要添加额外的中间件 (保持最小化)
- 不要服务 `/static` 前缀 (SPA 直接挂载到根路径)

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest 已配置)
- **Automated tests**: YES (Tests-after)
- **Framework**: pytest
- **If TDD**: N/A - tests after implementation

### QA Policy
每个任务必须包含 agent-executed QA 场景。
- **API**: 使用 `Bash` (curl) 发送请求，断言状态码和响应字段
- **静态文件**: 使用 `Bash` (curl) 获取 HTML，断言包含 Vue 特征

---

## Execution Strategy

### Parallel Execution Waves

由于任务间存在依赖关系，采用顺序执行：

```
Wave 1 (基础设置):
├── Task 1: 更新 pyproject.toml 添加依赖 [quick]
└── Task 2: 创建 API 目录结构 [quick]

Wave 2 (核心实现):
├── Task 3: 创建 FastAPI 应用入口 [deep]
├── Task 4: 创建依赖注入模块 [quick]
└── Task 5: 创建 API 路由模块 [quick]

Wave 3 (集成):
├── Task 6: 修改 serve 命令 [deep]
└── Task 7: 添加配置文件 [quick]

Wave 4 (验证):
├── Task 8: 编写测试 [quick]
└── Task 9: 最终验证 [quick]

Critical Path: 1 → 2 → 3 → 6 → 9
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|------------|--------|
| 1 | — | 3 |
| 2 | — | 3, 4, 5 |
| 3 | 1, 2 | 6 |
| 4 | 2 | 3 |
| 5 | 2, 3 | 6 |
| 6 | 3, 5 | 9 |
| 7 | — | 6 |
| 8 | 3, 5 | 9 |
| 9 | 6, 8 | — |

### Agent Dispatch Summary

- **Wave 1**: 2 tasks → `quick` × 2
- **Wave 2**: 3 tasks → `deep` × 1, `quick` × 2
- **Wave 3**: 2 tasks → `deep` × 1, `quick` × 1
- **Wave 4**: 2 tasks → `quick` × 2

---

## TODOs

- [x] 1. 更新 pyproject.toml 添加 FastAPI 依赖

  **What to do**:
  - 在 `pyproject.toml` 的 `dependencies` 部分添加：
    - `fastapi>=0.109.0`
    - `uvicorn[standard]>=0.27.0`
  - 保持现有依赖不变

  **Must NOT do**:
  - 不要修改其他依赖版本
  - 不要添加不必要的 extras

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: 简单的文件编辑任务

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: Task 3
  - **Blocked By**: None

  **References**:
  - `pyproject.toml:48-56` - 当前 dependencies 位置

  **Acceptance Criteria**:
  - [x] `pyproject.toml` 包含 `fastapi>=0.109.0`
  - [x] `pyproject.toml` 包含 `uvicorn[standard]>=0.27.0`

  **QA Scenarios**:

  ```
  Scenario: 验证依赖已添加
    Tool: Bash
    Preconditions: pyproject.toml 存在
    Steps:
      1. 运行：grep -E "fastapi|uvicorn" pyproject.toml
      2. 断言：输出包含 "fastapi>=" 和 "uvicorn"
    Expected Result: 两个依赖都在 dependencies 中
    Failure Indicators: grep 返回非零或输出缺少依赖
    Evidence: .sisyphus/evidence/task-1-deps-check.txt
  ```

  **Commit**: YES (groups with 2)
  - Message: `feat(deps): add fastapi and uvicorn`
  - Files: `pyproject.toml`

---

- [x] 2. 创建 API 目录结构

  **What to do**:
  - 创建 `src/madousho/api/` 目录
  - 创建 `src/madousho/api/routes/` 目录
  - 创建 `src/madousho/api/__init__.py` (空文件)
  - 创建 `src/madousho/api/routes/__init__.py` (空文件)

  **Must NOT do**:
  - 不要添加任何代码到 `__init__.py`
  - 不要创建额外的子目录

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: 简单的目录/文件创建

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Task 3, 4, 5
  - **Blocked By**: None

  **References**:
  - `src/madousho/commands/` - 参考现有模块结构

  **Acceptance Criteria**:
  - [x] `src/madousho/api/__init__.py` 存在
  - [x] `src/madousho/api/routes/__init__.py` 存在

  **QA Scenarios**:

  ```
  Scenario: 验证目录结构
    Tool: Bash
    Preconditions: 无
    Steps:
      1. 运行：ls -la src/madousho/api/
      2. 断言：输出包含 __init__.py 和 routes/
      3. 运行：ls -la src/madousho/api/routes/
      4. 断言：输出包含 __init__.py
    Expected Result: 目录结构正确创建
    Failure Indicators: ls 返回错误或文件不存在
    Evidence: .sisyphus/evidence/task-2-dir-structure.txt
  ```

  **Commit**: YES (groups with 1)
  - Message: `feat(deps): add fastapi and uvicorn`
  - Files: `src/madousho/api/__init__.py`, `src/madousho/api/routes/__init__.py`

---

- [x] 3. 创建 FastAPI 应用入口

  **What to do**:
  - 创建 `src/madousho/api/main.py`
  - 初始化 FastAPI 应用，**仅设置以下参数**:
    - `title="Madousho.ai API"`
    - `version=__version__` (从 `src.madousho._version` 动态读取)
    - `contact={"url": "https://github.com/pedxyuyuko/madousho.ai"}`
    - `license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"}`
  - **不要设置**: `description`、`summary`、`docs_url` 等其他参数
  - 挂载 Vue SPA 静态文件到根路径 (`html=True`)
  - 包含 API 路由 (`/api/v1`)
  - 处理静态文件目录不存在的情况

  **Must NOT do**:
  - 不要添加 `description` 参数
  - 不要添加 `summary` 参数
  - 不要添加认证中间件
  - 不要添加额外的路由
  - 不要硬编码静态文件路径 (使用配置)
  - 不要硬编码 version 字符串

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: 核心基础设施，需要正确处理 SPA 挂载和错误处理

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 6
  - **Blocked By**: Task 1, 2, 4

  **References**:
  - `src/madousho/_version.py` - setuptools_scm 生成的版本文件
  - `pyproject.toml:91-96` - setuptools_scm 配置
  - `src/madousho/config/loader.py:get_config()` - 配置加载方式
  - FastAPI 官方文档：`https://fastapi.tiangolo.com/tutorial/static-files/` - StaticFiles 挂载方式

  **Acceptance Criteria**:
  - [x] FastAPI 应用正确初始化
  - [x] 仅设置 `title`、`version`、`contact`、`license_info` 四个参数
  - [x] version 从 `_version.__version__` 动态读取
  - [x] contact 仅包含 `url` 字段
  - [x] license_info 包含 `name` 和 `url` 字段
  - [x] 静态文件挂载到根路径 (`html=True`)
  - [x] API 路由包含 `/api/v1` 前缀
  - [x] 处理 `public/` 目录不存在的情况

  **QA Scenarios**:

  ```
  Scenario: 验证 FastAPI 应用可导入
    Tool: Bash
    Preconditions: 依赖已安装 (uv sync)
    Steps:
      1. 运行：python -c "from src.madousho.api.main import app; print(type(app))"
      2. 断言：输出包含 "FastAPI"
    Expected Result: 应用可成功导入
    Failure Indicators: ImportError 或输出不包含 FastAPI
    Evidence: .sisyphus/evidence/task-3-import-check.txt

  Scenario: 验证静态文件挂载配置
    Tool: Bash
    Preconditions: FastAPI 应用存在
    Steps:
      1. 运行：python -c "from src.madousho.api.main import app; print([r.path for r in app.routes])"
      2. 断言：输出包含 "/" 和 "/api/v1"
    Expected Result: 路由包含静态文件和 API 前缀
    Failure Indicators: 路由列表缺少预期路径
    Evidence: .sisyphus/evidence/task-3-routes-check.txt

  Scenario: 验证 version 动态读取
    Tool: Bash
    Preconditions: FastAPI 应用存在
    Steps:
      1. 运行：python -c "from src.madousho.api.main import app; print(app.version)"
      2. 断言：输出版本号格式正确 (如 0.1.0.dev1+gxxxxx)
      3. 运行：python -c "from src.madousho._version import __version__; print(__version__)"
      4. 断言：app.version 与 __version__ 一致
    Expected Result: version 动态读取且与 _version 一致
    Failure Indicators: version 为空或与 _version 不匹配
    Evidence: .sisyphus/evidence/task-3-version-check.txt

  Scenario: 验证 OpenAPI 元数据
    Tool: Bash
    Preconditions: FastAPI 应用存在
    Steps:
      1. 运行：python -c "from src.madousho.api.main import app; import json; print(json.dumps(app.openapi()['info'], indent=2))"
      2. 断言：info.title == "Madousho.ai API"
      3. 断言：info.contact.url == "https://github.com/pedxyuyuko/madousho.ai"
      4. 断言：info.license.name == "MIT"
      5. 断言：info 不包含 description 字段
    Expected Result: OpenAPI 元数据符合预期
    Failure Indicators: 字段缺失或值不匹配
    Evidence: .sisyphus/evidence/task-3-openapi-metadata.json
  ```

  **Commit**: YES
  - Message: `feat(api): create FastAPI application entry point`
  - Files: `src/madousho/api/main.py`
  - Pre-commit: `python -c "from src.madousho.api.main import app; print(app.version)"`

---

- [x] 4. 创建依赖注入模块

  **What to do**:
  - 创建 `src/madousho/api/deps.py`
  - 实现 `get_db()` 依赖注入函数
  - 使用 `Database.get_instance()` 获取数据库
  - 使用上下文管理器处理 session

  **Must NOT do**:
  - 不要手动 commit/rollback (使用 db.session())
  - 不要直接调用 `Database()`

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: 标准依赖注入模式

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 5)
  - **Blocks**: Task 3
  - **Blocked By**: Task 2

  **References**:
  - `src/madousho/database/connection.py:Database` - Database 单例类
  - `src/madousho/commands/serve.py` - 参考现有数据库使用模式

  **Acceptance Criteria**:
  - [x] `get_db()` 函数使用生成器 (`yield`)
  - [x] 使用 `Database.get_instance()` 获取连接
  - [x] 正确使用上下文管理器

  **QA Scenarios**:

  ```
  Scenario: 验证依赖注入可导入
    Tool: Bash
    Preconditions: 无
    Steps:
      1. 运行：python -c "from src.madousho.api.deps import get_db; print('OK')"
      2. 断言：输出 "OK"
    Expected Result: 模块可成功导入
    Failure Indicators: ImportError
    Evidence: .sisyphus/evidence/task-4-import-check.txt
  ```

  **Commit**: YES (groups with 5)
  - Message: `feat(api): add dependency injection module`
  - Files: `src/madousho/api/deps.py`

---

- [x] 5. 创建 API 路由模块

  **What to do**:
  - 创建 `src/madousho/api/routes/__init__.py` 内容
  - 创建 `APIRouter` 实例
  - 创建健康检查端点 `GET /health`
  - 返回标准健康检查响应

  **Must NOT do**:
  - 不要添加业务逻辑路由
  - 不要添加数据库操作

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: 简单的路由定义

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 4)
  - **Blocks**: Task 6
  - **Blocked By**: Task 2, 3

  **References**:
  - FastAPI 官方文档：`https://fastapi.tiangolo.com/tutorial/path-params/` - APIRouter 使用

  **Acceptance Criteria**:
  - [x] `APIRouter` 正确初始化
  - [x] `GET /health` 端点返回 `{"status": "ok"}`
  - [x] 响应状态码 200

  **QA Scenarios**:

  ```
  Scenario: 验证健康检查端点
    Tool: Bash (curl)
    Preconditions: 服务器运行在 localhost:8000
    Steps:
      1. 运行：curl -s http://localhost:8000/api/v1/health
      2. 断言：响应包含 "status" 和 "ok"
      3. 断言：HTTP 状态码为 200
    Expected Result: {"status": "ok"}
    Failure Indicators: 404 或响应不包含预期字段
    Evidence: .sisyphus/evidence/task-5-health-check.json
  ```

  **Commit**: YES (groups with 4)
  - Message: `feat(api): add dependency injection module`
  - Files: `src/madousho/api/routes/__init__.py`

---

- [x] 6. 修改 serve 命令启动 HTTP 服务器

  **What to do**:
  - 修改 `src/madousho/commands/serve.py`
  - 保留原有数据库初始化逻辑
  - 添加 uvicorn 启动逻辑
  - 从配置读取 host/port
  - 添加 `--reload` 选项 (开发模式)

  **Must NOT do**:
  - 不要删除数据库初始化代码
  - 不要硬编码 host/port

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: 核心命令修改，需要正确处理配置和错误处理

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 9
  - **Blocked By**: Task 3, 5, 7

  **References**:
  - `src/madousho/commands/serve.py` - 当前实现
  - `src/madousho/config/models.py` - 配置模型结构
  - uvicorn 文档：`https://www.uvicorn.org/deployment/` - 部署配置

  **Acceptance Criteria**:
  - [x] `madousho serve` 启动 HTTP 服务器
  - [x] 服务器监听配置的 host/port
  - [x] 数据库初始化仍然执行
  - [x] 支持 `--reload` 标志

  **QA Scenarios**:

  ```
  Scenario: 验证 serve 命令可执行
    Tool: Bash
    Preconditions: 依赖已安装
    Steps:
      1. 运行：madousho serve --help
      2. 断言：输出包含 "--reload" 选项
    Expected Result: 命令帮助正确显示
    Failure Indicators: 命令不存在或帮助信息错误
    Evidence: .sisyphus/evidence/task-6-help-check.txt

  Scenario: 验证服务器可启动 (后台)
    Tool: interactive_bash
    Preconditions: 无进程占用 8000 端口
    Steps:
      1. tmux 启动：madousho serve &
      2. 等待 3 秒
      3. 运行：curl -s http://localhost:8000/api/v1/health
      4. 断言：响应成功
      5. 终止后台进程
    Expected Result: 服务器正常启动并响应
    Failure Indicators: 启动失败或端口被占用
    Evidence: .sisyphus/evidence/task-6-server-start.txt
  ```

  **Commit**: YES
  - Message: `feat(serve): start HTTP server with uvicorn`
  - Files: `src/madousho/commands/serve.py`
  - Pre-commit: `madousho serve --help`

---

  **What to do**:
  - 修改 `src/madousho/commands/serve.py`
  - 保留原有数据库初始化逻辑
  - 添加 uvicorn 启动逻辑
  - 从配置读取 host/port
  - 添加 `--reload` 选项 (开发模式)

  **Must NOT do**:
  - 不要删除数据库初始化代码
  - 不要硬编码 host/port

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: 核心命令修改，需要正确处理配置和错误处理

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 9
  - **Blocked By**: Task 3, 5, 7

  **References**:
  - `src/madousho/commands/serve.py` - 当前实现
  - `src/madousho/config/models.py` - 配置模型结构
  - uvicorn 文档：`https://www.uvicorn.org/deployment/` - 部署配置

  **Acceptance Criteria**:
  - [x] `madousho serve` 启动 HTTP 服务器
  - [x] 服务器监听配置的 host/port
  - [x] 数据库初始化仍然执行
  - [x] 支持 `--reload` 标志

  **QA Scenarios**:

  ```
  Scenario: 验证 serve 命令可执行
    Tool: Bash
    Preconditions: 依赖已安装
    Steps:
      1. 运行：madousho serve --help
      2. 断言：输出包含 "--reload" 选项
    Expected Result: 命令帮助正确显示
    Failure Indicators: 命令不存在或帮助信息错误
    Evidence: .sisyphus/evidence/task-6-help-check.txt

  Scenario: 验证服务器可启动 (后台)
    Tool: interactive_bash
    Preconditions: 无进程占用 8000 端口
    Steps:
      1. tmux 启动：madousho serve &
      2. 等待 3 秒
      3. 运行：curl -s http://localhost:8000/api/v1/health
      4. 断言：响应成功
      5. 终止后台进程
    Expected Result: 服务器正常启动并响应
    Failure Indicators: 启动失败或端口被占用
    Evidence: .sisyphus/evidence/task-6-server-start.txt
  ```

  **Commit**: YES
  - Message: `feat(serve): start HTTP server with uvicorn`
  - Files: `src/madousho/commands/serve.py`
  - Pre-commit: `madousho serve --help`

---

- [x] 7. 更新配置模型添加 API 配置支持

  **What to do**:
  - 检查 `src/madousho/config/models.py` 中的 Config 模型
  - 确认 `api` 配置节已包含 `host`, `port`, `token` 字段
  - 如缺少则添加这些字段到 Pydantic 模型
  - **不要**创建新的配置文件，使用现有的 `config/madousho.example.yaml`

  **Must NOT do**:
  - 不要创建新的配置文件
  - 不要修改 `config/madousho.example.yaml`

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: 简单的模型更新

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Task 8)
  - **Blocks**: Task 6
  - **Blocked By**: None

  **References**:
  - `config/madousho.example.yaml:5-9` - 现有 api 配置结构
  - `src/madousho/config/models.py:Config` - Pydantic 配置模型

  **Acceptance Criteria**:
  - [x] `Config` 模型包含 `api` 字段
  - [x] `api` 配置包含 `host`, `port`, `token` 子字段
  - [x] 配置可正确加载

  **QA Scenarios**:

  ```
  Scenario: 验证配置可加载
    Tool: Bash
    Preconditions: 配置文件存在
    Steps:
      1. 运行：python -c "from src.madousho.config import get_config; c = get_config(); print(c.api.host, c.api.port)"
      2. 断言：输出 "0.0.0.0 8000"
    Expected Result: 配置正确加载
    Failure Indicators: 配置加载失败或值不正确
    Evidence: .sisyphus/evidence/task-7-config-check.txt
  ```

  **Commit**: YES
  - Message: `feat(config): add api config model fields`
  - Files: `src/madousho/config/models.py`

---

- [x] 8. 编写测试

  **What to do**:
  - 创建 `tests/api/` 目录
  - 创建 `tests/api/test_health.py`
  - 使用 `TestClient` 测试健康检查端点
  - 测试静态文件服务

  **Must NOT do**:
  - 不要测试数据库集成 (已有其他测试)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: 标准 pytest 测试

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Task 7)
  - **Blocks**: Task 9
  - **Blocked By**: Task 3, 5

  **References**:
  - `tests/` - 现有测试结构
  - FastAPI 测试文档：`https://fastapi.tiangolo.com/tutorial/testing/`

  **Acceptance Criteria**:
  - [x] 测试文件存在
  - [x] `pytest tests/api/` 通过
  - [x] 覆盖率满足 90% 要求

  **QA Scenarios**:

  ```
  Scenario: 运行 API 测试
    Tool: Bash
    Preconditions: 测试文件存在
    Steps:
      1. 运行：pytest tests/api/ -v
      2. 断言：所有测试通过
      3. 断言：无失败或错误
    Expected Result: 测试全部通过
    Failure Indicators: 测试失败或错误
    Evidence: .sisyphus/evidence/task-8-test-run.txt
  ```

  **Commit**: YES
  - Message: `test(api): add API tests`
  - Files: `tests/api/test_health.py`
  - Pre-commit: `pytest tests/api/`

---

- [x] 9. 最终验证

  **What to do**:
  - 安装依赖：`uv sync`
  - 启动服务器：`madousho serve`
  - 验证所有端点
  - 运行完整测试套件

  **Must NOT do**:
  - 无

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: 验证任务

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: None
  - **Blocked By**: Task 6, 8

  **References**:
  - 所有上述任务

  **Acceptance Criteria**:
  - [x] `uv sync` 成功
  - [x] `madousho serve` 启动成功
  - [x] `pytest` 全部通过
  - [x] 覆盖率 >= 90%

  **QA Scenarios**:

  ```
  Scenario: 完整集成验证
    Tool: Bash
    Preconditions: 所有代码已提交
    Steps:
      1. 运行：uv sync
      2. 断言：无错误
      3. 运行：pytest --cov=src/madousho
      4. 断言：所有测试通过，覆盖率 >= 90%
    Expected Result: 构建和测试全部通过
    Failure Indicators: 安装失败或测试失败
    Evidence: .sisyphus/evidence/task-9-final-verification.txt
  ```

  **Commit**: NO (验证任务)

---

## Final Verification Wave

- [x] F1. **Plan Compliance Audit** — `oracle`
  验证所有 "Must Have" 已实现，"Must NOT Have" 未出现。

- [x] F2. **Code Quality Review** — `unspecified-high`
  运行 `tsc --noEmit` + linter + `pytest`。检查代码质量。

- [x] F3. **Real Manual QA** — `unspecified-high`
  执行所有 QA 场景，验证端到端功能。

- [x] F4. **Scope Fidelity Check** — `deep`
  验证每个任务 1:1 实现，无范围蔓延。

---

## Commit Strategy

- **1-2**: `feat(deps): add fastapi and uvicorn` — pyproject.toml, src/madousho/api/__init__.py, src/madousho/api/routes/__init__.py
- **4-5**: `feat(api): add dependency injection module` — src/madousho/api/deps.py, src/madousho/api/routes/__init__.py
- **3**: `feat(api): create FastAPI application entry point` — src/madousho/api/main.py
- **7**: `feat(config): add api config model fields` — src/madousho/config/models.py
- **6**: `feat(serve): start HTTP server with uvicorn` — src/madousho/commands/serve.py
- **8**: `test(api): add API tests` — tests/api/test_health.py

---

## Success Criteria

### Verification Commands
```bash
uv sync                        # 安装依赖
madousho serve                 # 启动服务器
curl http://localhost:8000/api/v1/health  # 健康检查
pytest --cov=src/madousho      # 测试 + 覆盖率
```

### Final Checklist
- [x] FastAPI 应用正确初始化
- [x] 静态文件服务正常工作
- [x] API 路由 `/api/v1` 可访问
- [x] 健康检查端点返回正确响应
- [x] 所有测试通过，覆盖率 >= 90%
