# API 服务器脚手架计划

## TL;DR

> **Quick Summary**: 为 madousho_ai 创建 FastAPI 服务器脚手架，在 `madousho run` 命令中启动，提供 /api/v1/health 健康检查端点。
> 
> **Deliverables**: 
> - FastAPI 应用模块 (`src/madousho/api/`)
> - Token 认证中间件
> - 健康检查端点
> - 集成到 `madousho run` 命令
> - 完整测试覆盖（90%+）
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: 依赖添加 → API 模块创建 → 认证中间件 → 健康检查端点 → run 命令集成 → 测试

---

## Context

### Original Request
为 API 服务器建立脚手架，然后在 run 命令里面启动 API 服务器。

### Interview Summary
**Key Discussions**:
- **框架选择**: FastAPI + uvicorn.run() 启动
- **路由前缀**: /api/v1
- **认证方式**: Token 认证（使用配置中的 api.token 字段）
- **端点范围**: 最小化 - 仅健康检查
- **健康检查内容**: 返回状态 + 版本信息
- **测试策略**: TDD with pytest（90% 覆盖率要求）

**Research Findings**:
- 项目已有 APIConfig 模型（host, port, token）
- 当前无任何 API 代码
- 测试框架：pytest + pytest-cov，90% 覆盖率强制要求
- 项目使用 Pydantic v2、Typer CLI、loguru 日志

### Metis Review
**Identified Gaps** (addressed):
- **启动控制**: 确认在 `run_cmd` 中阻塞式启动
- **依赖管理**: FastAPI + uvicorn 添加到主依赖
- **日志集成**: 使用现有 loguru logger
- **边缘情况**: 端口冲突、信号处理、token 可选性

---

## Work Objectives

### Core Objective
创建最小化 FastAPI 服务器脚手架，提供健康检查端点，集成到现有 CLI。

### Concrete Deliverables
- `src/madousho/api/__init__.py` - API 模块导出
- `src/madousho/api/app.py` - FastAPI 应用实例
- `src/madousho/api/middleware/auth.py` - Token 认证中间件
- `src/madousho/api/routes/health.py` - 健康检查端点
- `src/madousho/api/routes/__init__.py` - 路由导出
- `pyproject.toml` - 添加 FastAPI 依赖
- `src/madousho/commands/run.py` - 集成 API 启动
- `tests/api/` - 完整测试套件

### Definition of Done
- `madousho run` 启动后，`curl http://localhost:8000/api/v1/health` 返回 200
- 无效 token 返回 401
- 测试覆盖率 ≥90%
- 所有现有测试通过

### Must Have
- FastAPI 应用创建
- /api/v1/health 端点
- Token 认证中间件（token 为空时允许无认证）
- 端口冲突时清晰错误信息 + 退出码 1
- SIGTERM/SIGINT 优雅关闭

### Must NOT Have (Guardrails)
- 其他业务端点（flow 管理、任务控制等）
- CORS 配置
- WebSocket 支持
- 前端 UI / Swagger 自定义
- Docker/部署配置

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest + pytest-cov)
- **Automated tests**: YES (TDD)
- **Framework**: pytest (90% coverage required)
- **If TDD**: Each task follows RED (failing test) → GREEN (minimal impl) → REFACTOR

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **API Endpoints**: Bash (curl) - Send requests, assert status + response fields
- **Middleware**: Bash (curl with headers) - Test auth with/without tokens
- **Integration**: interactive_bash - Run `madousho run`, verify server starts

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - 基础 scaffold + 依赖):
├── Task 1: 添加 FastAPI 依赖到 pyproject.toml [quick]
├── Task 2: 创建 API 模块目录结构 [quick]
├── Task 3: 创建 FastAPI 应用实例 [quick]
└── Task 4: 创建 Token 认证中间件 [quick]

Wave 2 (After Wave 1 - 端点 + 集成 + 测试):
├── Task 5: 创建健康检查端点 [quick]
├── Task 6: 集成 API 启动到 run 命令 [unspecified-high]
├── Task 7: API 模块测试 [deep]
├── Task 8: 中间件测试 [deep]
├── Task 9: 端点测试 [deep]
└── Task 10: 集成测试 [deep]

Critical Path: 1 → 2 → 3 → 4 → 5 → 6 → 7-10
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 4 (Wave 2)
```

### Dependency Matrix

- **1**: — — 2-10, 1
- **2**: 1 — 3-10, 2
- **3**: 2 — 4-6, 3
- **4**: 3 — 5-6, 4
- **5**: 3, 4 — 6, 5
- **6**: 5 — 7-10, 6
- **7-10**: 6 — Final, 7-10

### Agent Dispatch Summary

- **1**: **4** — T1-T4 → `quick`
- **2**: **6** — T5 → `quick`, T6 → `unspecified-high`, T7-T10 → `deep`

---

## TODOs

- [x] 1. 添加 FastAPI 依赖到 pyproject.toml

  **What to do**:
  - 在 `pyproject.toml` 的 `dependencies` 中添加 `fastapi>=0.100.0,<1.0.0`
  - 添加 `uvicorn[standard]>=0.23.0,<1.0.0`
  - 运行 `pip install -e .` 验证依赖安装

  **Must NOT do**:
  - 不要修改其他依赖版本
  - 不要添加可选依赖组

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: 简单的依赖添加任务

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (blocks all other tasks)
  - **Blocks**: Tasks 2-10
  - **Blocked By**: None

  **References**:
  - `pyproject.toml:28-40` - 现有依赖定义格式

  **Acceptance Criteria**:
  - [x] `pip install -e .` 成功安装 fastapi 和 uvicorn
  - [x] `python -c "import fastapi; import uvicorn"` 无错误

  **QA Scenarios**:

  ```
  Scenario: 验证 FastAPI 和 uvicorn 可导入
    Tool: Bash
    Preconditions: 依赖已安装
    Steps:
      1. 运行 python -c "import fastapi; import uvicorn; print('OK')"
      2. 验证输出包含 "OK"
    Expected Result: 无导入错误，输出 "OK"
    Failure Indicators: ImportError 或 ModuleNotFoundError
    Evidence: .sisyphus/evidence/task-1-import-check.txt
  ```

  **Commit**: YES (groups with 2, 3, 4)
  - Message: `feat(api): add FastAPI and uvicorn dependencies`
  - Files: `pyproject.toml`
  - Pre-commit: `python -c "import fastapi; import uvicorn"`

---

- [x] 2. 创建 API 模块目录结构

  **What to do**:
  - 创建 `src/madousho/api/__init__.py` - 导出 FastAPI 应用
  - 创建 `src/madousho/api/routes/__init__.py` - 路由导出
  - 确保目录结构符合项目规范

  **Must NOT do**:
  - 不要创建其他子目录（middleware 单独在 Task 4 创建）
  - 不要添加额外文件

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (depends on Task 1)
  - **Blocks**: Tasks 3-10
  - **Blocked By**: Task 1

  **References**:
  - `src/madousho/commands/__init__.py` - 模块导出模式
  - `src/madousho/flow/__init__.py` - 子包导出模式

  **Acceptance Criteria**:
  - [x] `src/madousho/api/__init__.py` 存在
  - [x] `src/madousho/api/routes/__init__.py` 存在

  **QA Scenarios**:

  ```
  Scenario: 验证 API 模块可导入
    Tool: Bash
    Preconditions: 目录结构已创建
    Steps:
      1. 运行 python -c "from madousho import api; print('OK')"
      2. 验证输出包含 "OK"
    Expected Result: 无导入错误
    Failure Indicators: ImportError
    Evidence: .sisyphus/evidence/task-2-module-import.txt
  ```

  **Commit**: YES (groups with 1, 3, 4)
  - Message: `feat(api): add FastAPI and uvicorn dependencies`
  - Files: `src/madousho/api/__init__.py`, `src/madousho/api/routes/__init__.py`

---

- [x] 3. 创建 FastAPI 应用实例

  **What to do**:
  - 创建 `src/madousho/api/app.py`
  - 初始化 FastAPI 应用，设置 title、version、description
  - 配置 API 路由前缀 `/api/v1`
  - 集成 loguru 日志

  **Must NOT do**:
  - 不要添加任何端点路由（Task 5 负责）
  - 不要添加中间件（Task 4 负责）

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Tasks 4-6
  - **Blocked By**: Task 2

  **References**:
  - `src/madousho/logger.py` - 日志集成模式
  - `src/madousho/__init__.py` - 版本获取方式

  **Acceptance Criteria**:
  - [x] `src/madousho/api/app.py` 存在
  - [x] FastAPI 应用正确初始化
  - [x] 路由前缀配置为 `/api/v1`

  **QA Scenarios**:

  ```
  Scenario: 验证 FastAPI 应用可实例化
    Tool: Bash
    Preconditions: app.py 已创建
    Steps:
      1. 运行 python -c "from madousho.api.app import create_app; app = create_app(); print('OK')"
      2. 验证输出包含 "OK"
    Expected Result: 应用成功创建
    Failure Indicators: ImportError, AttributeError
    Evidence: .sisyphus/evidence/task-3-app-create.txt
  ```

  **Commit**: YES (groups with 1, 2, 4)
  - Message: `feat(api): add FastAPI and uvicorn dependencies`
  - Files: `src/madousho/api/app.py`

---

- [x] 4. 创建 Token 认证中间件

  **What to do**:
  - 创建 `src/madousho/api/middleware/__init__.py`
  - 创建 `src/madousho/api/middleware/auth.py`
  - 实现 Token 认证中间件：
    - 从 `Authorization: Bearer <token>` 头提取 token
    - 与配置的 `api.token` 比较
    - token 为空时允许无认证访问
    - 无效 token 返回 401

  **Must NOT do**:
  - 不要实现 JWT 或 OAuth2
  - 不要添加速率限制等其他中间件

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Tasks 5-6
  - **Blocked By**: Task 3

  **References**:
  - `src/madousho/config/models.py:APIConfig` - Token 配置字段
  - FastAPI 中间件文档：https://fastapi.tiangolo.com/tutorial/middleware/

  **Acceptance Criteria**:
  - [x] 中间件正确提取 Bearer token
  - [x] token 匹配时请求通过
  - [x] token 不匹配时返回 401
  - [x] token 为空时允许无认证

  **QA Scenarios**:

  ```
  Scenario: 有效 token 通过认证
    Tool: Bash (curl)
    Preconditions: 服务器运行，token 配置为 "test-token"
    Steps:
      1. curl -H "Authorization: Bearer test-token" http://localhost:8000/api/v1/health
      2. 验证状态码 200
    Expected Result: 200 OK
    Failure Indicators: 401 Unauthorized
    Evidence: .sisyphus/evidence/task-4-auth-valid.txt

  Scenario: 无效 token 被拒绝
    Tool: Bash (curl)
    Preconditions: 服务器运行，token 配置为 "test-token"
    Steps:
      1. curl -H "Authorization: Bearer wrong-token" http://localhost:8000/api/v1/health
      2. 验证状态码 401
    Expected Result: 401 Unauthorized
    Failure Indicators: 200 OK
    Evidence: .sisyphus/evidence/task-4-auth-invalid.txt

  Scenario: 空 token 配置允许无认证
    Tool: Bash (curl)
    Preconditions: 服务器运行，token 配置为空
    Steps:
      1. curl http://localhost:8000/api/v1/health (无 Authorization 头)
      2. 验证状态码 200
    Expected Result: 200 OK
    Failure Indicators: 401 Unauthorized
    Evidence: .sisyphus/evidence/task-4-auth-none.txt
  ```

  **Commit**: YES (groups with 1, 2, 3)
  - Message: `feat(api): add FastAPI and uvicorn dependencies`
  - Files: `src/madousho/api/middleware/__init__.py`, `src/madousho/api/middleware/auth.py`

---

- [x] 5. 创建健康检查端点

  **What to do**:
  - 创建 `src/madousho/api/routes/health.py`
  - 实现 `GET /api/v1/health` 端点
  - 返回 JSON: `{"status": "ok", "version": "x.x.x"}`
  - 版本从 `madousho._version` 获取

  **Must NOT do**:
  - 不要添加其他端点
  - 不要添加复杂逻辑（数据库检查等）

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 6
  - **Blocked By**: Task 4

  **References**:
  - `src/madousho/_version.py` - 版本获取
  - `src/madousho/__init__.py` - 版本导出

  **Acceptance Criteria**:
  - [x] `GET /api/v1/health` 返回 200
  - [x] 响应包含 `status: "ok"`
  - [x] 响应包含 `version` 字段

  **QA Scenarios**:

  ```
  Scenario: 健康检查返回正确格式
    Tool: Bash (curl)
    Preconditions: 服务器运行
    Steps:
      1. curl http://localhost:8000/api/v1/health
      2. 验证 JSON 包含 status 和 version 字段
      3. 验证 status == "ok"
    Expected Result: {"status": "ok", "version": "0.1.0"}
    Failure Indicators: 缺少字段或 status 不是 "ok"
    Evidence: .sisyphus/evidence/task-5-health-check.json
  ```

  **Commit**: YES (groups with 6)
  - Message: `feat(api): create health check endpoint and integrate with run command`
  - Files: `src/madousho/api/routes/health.py`

---

- [x] 6. 集成 API 启动到 run 命令

  **What to do**:
  - 修改 `src/madousho/commands/run.py`
  - 在加载插件后，启动 API 服务器
  - 使用 `uvicorn.run()` 启动
  - 从配置读取 `api.host` 和 `api.port`
  - 处理端口冲突（退出码 1 + 清晰错误）
  - 处理 SIGTERM/SIGINT 优雅关闭

  **Must NOT do**:
  - 不要阻塞现有的 flow 加载逻辑
  - 不要创建新的命令行参数

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Tasks 7-10
  - **Blocked By**: Task 5

  **References**:
  - `src/madousho/commands/run.py:10-74` - 现有 run 命令逻辑
  - `src/madousho/config/models.py:APIConfig` - 配置字段
  - `src/madousho/cli.py:16-79` - 配置加载逻辑

  **Acceptance Criteria**:
  - [x] `madousho run` 启动后 API 服务器运行
  - [x] 端口被占用时退出码 1 + 错误信息
  - [x] Ctrl+C 优雅关闭

  **QA Scenarios**:

  ```
  Scenario: madousho run 启动 API 服务器
    Tool: interactive_bash (tmux)
    Preconditions: 配置有效
    Steps:
      1. tmux 启动 madousho run
      2. 等待服务器启动消息
      3. curl http://localhost:8000/api/v1/health
      4. 验证返回 200
    Expected Result: 服务器启动成功，健康检查通过
    Failure Indicators: 连接失败或 500 错误
    Evidence: .sisyphus/evidence/task-6-server-start.txt

  Scenario: 端口冲突优雅失败
    Tool: interactive_bash (tmux)
    Preconditions: 端口 8000 已被占用
    Steps:
      1. 启动另一个进程占用 8000 端口
      2. tmux 启动 madousho run
      3. 验证退出码为 1
      4. 验证错误信息包含 "port already in use"
    Expected Result: 清晰错误信息 + 退出码 1
    Failure Indicators: 无错误信息或退出码 0
    Evidence: .sisyphus/evidence/task-6-port-conflict.txt
  ```

  **Commit**: YES (groups with 5)
  - Message: `feat(api): create health check endpoint and integrate with run command`
  - Files: `src/madousho/commands/run.py`

---

- [x] 7. API 模块测试

  **What to do**:
  - 创建 `tests/api/__init__.py`
  - 创建 `tests/api/test_app.py`
  - 测试 FastAPI 应用创建
  - 测试路由前缀配置
  - 遵循项目测试模式（类命名、docstring）

  **Must NOT do**:
  - 不要跳过边界情况测试
  - 不要忽略类型检查

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 8-10)
  - **Blocks**: Final verification
  - **Blocked By**: Task 6

  **References**:
  - `tests/config/test_models.py` - 测试模式
  - `tests/flow/test_base.py` - 测试结构

  **Acceptance Criteria**:
  - [x] `tests/api/test_app.py` 存在
  - [x] 测试覆盖率 ≥90%
  - [x] 所有测试通过

  **QA Scenarios**:

  ```
  Scenario: 运行 API 模块测试
    Tool: Bash
    Preconditions: 测试文件已创建
    Steps:
      1. pytest tests/api/test_app.py -v
      2. 验证所有测试通过
    Expected Result: 0 failures
    Failure Indicators: 任何测试失败
    Evidence: .sisyphus/evidence/task-7-test-output.txt
  ```

  **Commit**: YES (groups with 8, 9, 10)
  - Message: `test(api): add comprehensive test suite for API module`
  - Files: `tests/api/test_app.py`

---

- [x] 8. 中间件测试

  **What to do**:
  - 创建 `tests/api/test_middleware.py`
  - 测试 Token 认证：
    - 有效 token 通过
    - 无效 token 拒绝
    - 空 token 配置允许无认证
  - 测试边缘情况（特殊字符 token、超长 token）

  **Must NOT do**:
  - 不要遗漏边缘情况

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 7, 9, 10)
  - **Blocks**: Final verification
  - **Blocked By**: Task 6

  **References**:
  - `tests/config/test_models.py` - 边缘情况测试模式

  **Acceptance Criteria**:
  - [x] `tests/api/test_middleware.py` 存在
  - [x] 覆盖所有认证场景
  - [x] 所有测试通过

  **QA Scenarios**:

  ```
  Scenario: 运行中间件测试
    Tool: Bash
    Preconditions: 测试文件已创建
    Steps:
      1. pytest tests/api/test_middleware.py -v
      2. 验证所有测试通过
    Expected Result: 0 failures
    Failure Indicators: 任何测试失败
    Evidence: .sisyphus/evidence/task-8-test-output.txt
  ```

  **Commit**: YES (groups with 7, 9, 10)
  - Message: `test(api): add comprehensive test suite for API module`
  - Files: `tests/api/test_middleware.py`

---

- [x] 9. 端点测试

  **What to do**:
  - 创建 `tests/api/test_routes.py`
  - 测试健康检查端点：
    - GET /api/v1/health 返回 200
    - 响应格式正确
    - 版本字段正确
  - 测试 404 未找到路由

  **Must NOT do**:
  - 不要测试不存在的端点

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 7, 8, 10)
  - **Blocks**: Final verification
  - **Blocked By**: Task 6

  **References**:
  - `tests/commands/test_run.py` - 命令测试模式

  **Acceptance Criteria**:
  - [x] `tests/api/test_routes.py` 存在
  - [x] 覆盖所有端点场景
  - [x] 所有测试通过

  **QA Scenarios**:

  ```
  Scenario: 运行端点测试
    Tool: Bash
    Preconditions: 测试文件已创建
    Steps:
      1. pytest tests/api/test_routes.py -v
      2. 验证所有测试通过
    Expected Result: 0 failures
    Failure Indicators: 任何测试失败
    Evidence: .sisyphus/evidence/task-9-test-output.txt
  ```

  **Commit**: YES (groups with 7, 8, 10)
  - Message: `test(api): add comprehensive test suite for API module`
  - Files: `tests/api/test_routes.py`

---

- [x] 10. 集成测试

  **What to do**:
  - 创建 `tests/api/test_integration.py`
  - 测试完整流程：
    - `madousho run` 启动服务器
    - 健康检查端点可访问
    - 认证中间件工作
    - 优雅关闭
  - 使用 TestClient 进行端到端测试

  **Must NOT do**:
  - 不要依赖外部服务

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 7-9)
  - **Blocks**: Final verification
  - **Blocked By**: Task 6

  **References**:
  - `tests/flow/` - 集成测试模式
  - FastAPI TestClient: https://fastapi.tiangolo.com/tutorial/testing/

  **Acceptance Criteria**:
  - [x] `tests/api/test_integration.py` 存在
  - [x] 覆盖完整流程
  - [x] 所有测试通过

  **QA Scenarios**:

  ```
  Scenario: 运行集成测试
    Tool: Bash
    Preconditions: 测试文件已创建
    Steps:
      1. pytest tests/api/test_integration.py -v
      2. 验证所有测试通过
    Expected Result: 0 failures
    Failure Indicators: 任何测试失败
    Evidence: .sisyphus/evidence/task-10-test-output.txt
  ```

  **Commit**: YES (groups with 7, 8, 9)
  - Message: `test(api): add comprehensive test suite for API module`
  - Files: `tests/api/test_integration.py`

---

## Final Verification Wave

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists. For each "Must NOT Have": search codebase for forbidden patterns. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run `tsc --noEmit` + linter + `pytest`. Review all changed files for: `as any`/`@ts-ignore`, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names.
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Execute EVERY QA scenario from EVERY task. Test cross-task integration. Test edge cases: empty state, invalid input, rapid actions. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff. Verify 1:1. Check "Must NOT do" compliance. Detect cross-task contamination. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **1-4**: `feat(api): add FastAPI and uvicorn dependencies` — pyproject.toml, src/madousho/api/__init__.py, src/madousho/api/app.py, src/madousho/api/middleware/auth.py
- **5-6**: `feat(api): create health check endpoint and integrate with run command` — src/madousho/api/routes/health.py, src/madousho/commands/run.py
- **7-10**: `test(api): add comprehensive test suite for API module` — tests/api/test_app.py, tests/api/test_middleware.py, tests/api/test_routes.py, tests/api/test_integration.py

---

## Success Criteria

### Verification Commands
```bash
# 1. 依赖安装
pip install -e . && python -c "import fastapi; import uvicorn; print('OK')"
# Expected: OK

# 2. 模块导入
python -c "from madousho.api.app import create_app; print('OK')"
# Expected: OK

# 3. 启动服务器
madousho run &
sleep 2
curl http://localhost:8000/api/v1/health
# Expected: {"status":"ok","version":"0.1.0"}

# 4. 认证测试（配置 token 时）
curl -H "Authorization: Bearer wrong-token" http://localhost:8000/api/v1/health
# Expected: 401 Unauthorized

# 5. 测试覆盖率
pytest tests/api/ --cov=madousho.api --cov-fail-under=90
# Expected: 90%+ coverage, 0 failures
```

### Final Checklist
- [x] 所有 "Must Have" 实现
- [x] 所有 "Must NOT Have" 不存在
- [x] 所有测试通过（90%+ 覆盖率）
- [x] `madousho run` 启动后 API 可访问
- [x] 认证中间件正常工作
- [x] 优雅关闭正常工作
