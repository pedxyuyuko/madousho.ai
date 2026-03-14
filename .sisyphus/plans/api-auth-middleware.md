# FastAPI API 鉴权中间件

## TL;DR

> **Quick Summary**: 为 FastAPI API 添加基于配置文件 `api.token` 的鉴权系统，使用 Depends() 模式，支持 Bearer Token 和 X-API-Token 双 header，统一 RESTful 错误格式。
>
> **Deliverables**:
> - `api/deps.py` 中的 `verify_token()` 依赖函数
> - `api/errors.py` 统一错误响应工具
> - 双 router 架构（public_router + protected_router）
> - 完整 TDD 测试套件
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: 测试(RED) → 依赖函数+错误工具 → 路由重组+集成

---

## Context

### Original Request
"阅读项目结构和fastapi实现 添加一个鉴权中间件 使用配置文件里面的 api.token"

### Interview Summary
**Key Discussions**:
- 实现方式：选择 FastAPI Depends() 而非 Starlette Middleware，符合项目 `deps.py` 既有模式
- Token 传递：同时支持 `Authorization: Bearer <token>` 和 `X-API-Token` header
- 错误格式：简洁 RESTful `{"error": "<code>", "message": "<human_readable>"}` + 统一包装
- 健康检查：`/api/v1/health` 保持公开，用于负载均衡器探测
- 测试策略：TDD（先写测试 RED，再实现 GREEN）
- 未来扩展：全局 token 够了，不需要 per-user/OAuth

**Research Findings**:
- 项目使用 `get_db()` generator pattern 做依赖注入，新鉴权应遵循相同模式
- `ApiConfig.token` 空值时自动生成 32 字符 hex，通过 `get_config().api.token` 访问
- 现有测试用 `TestClient(app)` + pytest class-based 组织

### Metis Review
**Identified Gaps** (已整合到计划):
- Token 比较需用 `secrets.compare_digest()` 防时序攻击 → ✅ 加入任务要求
- 路由排除方案未定 → ✅ 采用双 router 方案（public_router + protected_router）
- OPTIONS 预检请求鉴权会阻断 SPA → ✅ 跳过 OPTIONS
- 错误响应应提取为共享工具 → ✅ 新增 `api/errors.py`
- main.py import 路径 bug（`src.madousho`）→ 标记为可选修复

---

## Work Objectives

### Core Objective
为 FastAPI API 添加基于 `api.token` 配置的鉴权依赖函数，采用 Depends() 模式，保护所有非公开端点。

### Concrete Deliverables
- `src/madousho/api/errors.py` — 统一错误响应模型和工具函数
- `src/madousho/api/deps.py` — 新增 `verify_token()` 依赖函数
- `src/madousho/api/routes/__init__.py` — 重组为 public_router + protected_router
- `src/madousho/api/main.py` — 挂载两个 router
- `tests/api/test_auth.py` — 完整 TDD 测试套件

### Definition of Done
- [ ] `pytest tests/api/test_auth.py` 全部通过
- [ ] `curl localhost:8000/api/v1/health` 无需 token 返回 200
- [ ] `curl -H "Authorization: Bearer <token>" localhost:8000/api/v1/protected` 返回 200/404（路由存在）
- [ ] `curl localhost:8000/api/v1/protected` 无 token 返回 401 + RESTful 格式
- [ ] Swagger `/docs` 显示 Authorize 按钮和 lock 图标
- [ ] `pytest --cov` 覆盖率 ≥ 90%

### Must Have
- `verify_token()` 使用 `secrets.compare_digest()` 常量时间比较
- 支持 `Authorization: Bearer <token>` 和 `X-API-Token` 双 header
- 统一错误格式 `{"error": "<code>", "message": "..."}`
- health 端点无需鉴权
- OpenAPI spec 包含 securitySchemes

### Must NOT Have (Guardrails)
- 不修改现有 health 端点行为
- 不添加 OAuth、多用户、角色系统
- 不在日志/响应中泄露 token 值
- 不使用 `==` 做 token 比较（时序攻击风险）
- 不用 Starlette Middleware 替代 Depends()

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: YES (pytest, 90% coverage required)
- **Automated tests**: TDD
- **Framework**: pytest

### QA Policy
- **API**: Bash (curl) — 发送请求，断言 status + response fields
- **Test Runner**: Bash (pytest) — 运行测试，验证通过

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation — 可并行启动):
├── Task 1: 统一错误响应模型 api/errors.py [quick]
└── Task 2: TDD 测试套件 tests/api/test_auth.py [deep]

Wave 2 (After Wave 1 — 核心实现):
├── Task 3: verify_token() 依赖函数 api/deps.py [quick]
└── Task 4: 双 router 架构重组 routes/__init__.py [quick]

Wave 3 (After Wave 2 — 集成):
└── Task 5: main.py 挂载 + OpenAPI security [quick]

Wave FINAL (验证):
├── Task F1: 集成测试全量通过 [deep]
└── Task F2: curl 端到端验证 [unspecified-high]
```

### Dependency Matrix
- **1**: — — 3, 4
- **2**: — — F1
- **3**: 1 — 4
- **4**: 1, 3 — 5
- **5**: 4 — F1, F2
- **F1**: 2, 5 — —
- **F2**: 5 — —

Critical Path: Task 1 → Task 3 → Task 4 → Task 5 → F1-F2

---

## TODOs

- [x] 1. 创建统一错误响应模型 `src/madousho/api/errors.py`

  **What to do**:
  - 创建 `ErrorResponse` Pydantic model: `error: str`, `message: str`
  - 创建辅助函数 `error_response(status_code, error_code, message)` 返回 `JSONResponse`
  - 创建常用错误常量：`AUTH_REQUIRED = ("authentication_required", "Valid API token required")`, `INVALID_TOKEN = ("invalid_token", "Invalid API token")`

  **Must NOT do**:
  - 不引入 HTTPException（直接用 JSONResponse 控制格式）
  - 不修改其他文件

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
    - Reason: 简单模型定义 + 工具函数，单一文件

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: Task 3, Task 4
  - **Blocked By**: None

  **References**:
  - `src/madousho/config/models.py:10-33` — Pydantic model 模式（Field, BaseModel）
  - `src/madousho/api/deps.py:1-16` — 模块风格参考（中文 docstring, 类型注解）

  **Acceptance Criteria**:
  - [ ] 文件 `src/madousho/api/errors.py` 存在
  - [ ] `from madousho.api.errors import ErrorResponse, error_response` 可导入
  - [ ] `ErrorResponse(error="test", "message"="hello").model_dump()` 返回正确 dict

  **QA Scenarios**:

  ```
  Scenario: ErrorResponse model 输出正确格式
    Tool: Bash (python)
    Steps:
      1. python -c "from madousho.api.errors import ErrorResponse; print(ErrorResponse(error='unauthorized', message='Invalid token').model_dump())"
    Expected Result: {"error": "unauthorized", "message": "Invalid token"}
    Evidence: .sisyphus/evidence/task-1-error-model.json

  Scenario: error_response 辅助函数返回正确 JSONResponse
    Tool: Bash (python)
    Steps:
      1. python -c "from madousho.api.errors import error_response; r = error_response(401, 'unauthorized', 'Invalid'); print(r.status_code, r.body)"
    Expected Result: status_code=401, body contains {"error":"unauthorized","message":"Invalid"}
    Evidence: .sisyphus/evidence/task-1-error-helper.json
  ```

  **Commit**: YES
  - Message: `feat(api): add unified error response model`
  - Files: `src/madousho/api/errors.py`
  - Pre-commit: `pytest tests/api/`

---

- [x] 2. 编写 TDD 测试套件 `tests/api/test_auth.py`（RED phase）

  **What to do**:
  - 创建完整的测试文件，覆盖所有鉴权场景
  - 使用 `TestClient(app)` + `monkeypatch` mock config token
  - 测试用例：
    1. 无 token 请求 protected 端点 → 401
    2. 正确 Bearer token → 通过
    3. 正确 X-API-Token → 通过
    4. 错误 token → 401
    5. Bearer 空值 → 401
    6. 错误 scheme (Basic) → 401
    7. health 端点无需鉴权 → 200
    8. Authorization 优先于 X-API-Token
    9. OPTIONS 请求跳过鉴权
    10. OpenAPI spec 包含 securitySchemes

  **Must NOT do**:
  - 不实现 `verify_token()` — 此任务纯测试（RED phase）
  - 测试会失败，这是预期的

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []
    - Reason: 需要理解 FastAPI TestClient、monkeypatch、config mocking 等多种模式

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Task F1
  - **Blocked By**: None

  **References**:
  - `tests/api/test_health.py` — 现有测试模式（TestClient, class-based, fixtures）
  - `src/madousho/config/models.py:10-33` — ApiConfig.token 结构
  - `src/madousho/config/loader.py` — get_config() 缓存机制

  **Acceptance Criteria**:
  - [ ] 测试文件 `tests/api/test_auth.py` 存在
  - [ ] `pytest tests/api/test_auth.py` 运行（预期失败，verify_token 未实现）
  - [ ] 至少 10 个测试用例覆盖上述场景

  **QA Scenarios**:

  ```
  Scenario: 测试文件可被 pytest 发现并执行
    Tool: Bash (pytest)
    Steps:
      1. pytest tests/api/test_auth.py -v --tb=line 2>&1 | head -30
    Expected Result: pytest 发现测试用例并运行（大部分因 verify_token 未实现而 FAILED）
    Evidence: .sisyphus/evidence/task-2-test-discovery.txt

  Scenario: 测试结构正确（至少 10 个测试函数）
    Tool: Bash (grep)
    Steps:
      1. grep -c "def test_" tests/api/test_auth.py
    Expected Result: count >= 10
    Evidence: .sisyphus/evidence/task-2-test-count.txt
  ```

  **Commit**: NO（与 Task 3 合并提交）

---

- [x] 3. 实现 `verify_token()` 依赖函数 `src/madousho/api/deps.py`

  **What to do**:
  - 在现有 `deps.py` 中新增 `verify_token()` 函数
  - 从 request 提取 token（先检查 Authorization: Bearer，再检查 X-API-Token）
  - 用 `secrets.compare_digest()` 常量时间比较（防时序攻击）
  - 失败时调用 `error_response()` 返回 401
  - 跳过 OPTIONS 请求（CORS preflight）
  - 跳过 /health 路径（由 router 级别控制，此函数不硬编码路径）

  **Must NOT do**:
  - 不在日志中打印 token 值
  - 不用 `==` 比较 token
  - 不硬编码路径白名单（由 router 层控制）

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
    - Reason: 单文件改动，遵循已有 deps.py 模式

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (with Task 4)
  - **Blocks**: Task 4
  - **Blocked By**: Task 1（需要 error_response 工具函数）

  **References**:
  - `src/madousho/api/deps.py:8-16` — 现有 get_db() 模式（函数签名、docstring 风格）
  - `src/madousho/api/errors.py`（Task 1 产物）— error_response, AUTH_REQUIRED, INVALID_TOKEN
  - `src/madousho/config/loader.py:get_config()` — 配置访问模式

  **Acceptance Criteria**:
  - [ ] `verify_token()` 函数定义在 `deps.py`
  - [ ] 支持 `Authorization: Bearer <token>` 提取
  - [ ] 支持 `X-API-Token` header 提取
  - [ ] 使用 `secrets.compare_digest()` 比较
  - [ ] OPTIONS 请求直接 pass through

  **QA Scenarios**:

  ```
  Scenario: verify_token 使用常量时间比较
    Tool: Bash (grep)
    Steps:
      1. grep "secrets.compare_digest" src/madousho/api/deps.py
    Expected Result: 找到 secrets.compare_digest 调用
    Evidence: .sisyphus/evidence/task-3-constant-time.txt

  Scenario: 支持双 header 提取逻辑
    Tool: Bash (python)
    Steps:
      1. python -c "
           from starlette.testclient import TestClient
           from madousho.api.main import app
           # ... 验证 Bearer 和 X-API-Token 两种方式
         "
    Expected Result: 两种 header 方式都能通过鉴权
    Evidence: .sisyphus/evidence/task-3-dual-header.txt
  ```

  **Commit**: YES（与 Task 2 合并）
  - Message: `feat(api): add verify_token dependency with TDD`
  - Files: `src/madousho/api/deps.py`, `tests/api/test_auth.py`
  - Pre-commit: `pytest tests/api/test_auth.py -v`

---

- [x] 4. 双 router 架构重组 `src/madousho/api/routes/__init__.py`

  **What to do**:
  - 创建 `public_router = APIRouter()` — 无需鉴权（health 端点放这里）
  - 创建 `protected_router = APIRouter(dependencies=[Depends(verify_token)])` — 所有未来端点
  - 现有 `@api_router.get("/health")` 迁移到 `public_router`
  - 导出 `public_router` 和 `protected_router`

  **Must NOT do**:
  - 不改变 health 端点的 URL 路径（仍然是 `/api/v1/health`）
  - 不改变 health 端点的响应内容

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
    - Reason: 单文件重组，已有代码迁移

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2（与 Task 3 并行）
  - **Blocks**: Task 5
  - **Blocked By**: Task 1, Task 3

  **References**:
  - `src/madousho/api/routes/__init__.py:1-9` — 现有路由定义
  - `src/madousho/api/deps.py` — verify_token 函数（Task 3 产物）

  **Acceptance Criteria**:
  - [ ] `public_router` 存在且包含 `/health` 端点
  - [ ] `protected_router` 存在且带 `dependencies=[Depends(verify_token)]`
  - [ ] `from madousho.api.routes import public_router, protected_router` 可导入

  **QA Scenarios**:

  ```
  Scenario: health 端点在 public_router 上且无需鉴权
    Tool: Bash (curl)
    Preconditions: 服务已启动
    Steps:
      1. curl -s http://localhost:8000/api/v1/health
    Expected Result: {"status": "ok"} (无 auth header)
    Evidence: .sisyphus/evidence/task-4-health-public.json

  Scenario: protected_router 正确导出
    Tool: Bash (python)
    Steps:
      1. python -c "from madousho.api.routes import public_router, protected_router; print(type(public_router), type(protected_router))"
    Expected Result: 两个 APIRouter 实例
    Evidence: .sisyphus/evidence/task-4-routers.txt
  ```

  **Commit**: YES
  - Message: `feat(api): split routes into public and protected routers`
  - Files: `src/madousho/api/routes/__init__.py`
  - Pre-commit: `pytest tests/api/test_auth.py -v`

---

- [x] 5. 更新 main.py 挂载 + OpenAPI security scheme

  **What to do**:
  - 更新 `main.py` 导入 `public_router` 和 `protected_router`（替换 `api_router`）
  - 分别挂载两个 router 到 `/api/v1` prefix
  - 配置 FastAPI app 的 security scheme 使 Swagger 显示 Authorize 按钮
  - 可选：修复 import 路径 `src.madousho` → `madousho`

  **Must NOT do**:
  - 不改变 `/api/v1` prefix
  - 不影响静态文件挂载

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
    - Reason: 小范围改动，配置调整

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: F1, F2
  - **Blocked By**: Task 4

  **References**:
  - `src/madousho/api/main.py:10-23` — 现有 app 配置和路由挂载
  - `src/madousho/api/routes/__init__.py`（Task 4 产物）— 双 router 导出

  **Acceptance Criteria**:
  - [ ] `main.py` 导入 `public_router, protected_router`
  - [ ] 两个 router 分别挂载到 `/api/v1`
  - [ ] `curl localhost:8000/openapi.json | jq '.components.securitySchemes'` 包含 Bearer 定义

  **QA Scenarios**:

  ```
  Scenario: OpenAPI spec 包含 security scheme
    Tool: Bash (curl)
    Preconditions: 服务已启动
    Steps:
      1. curl -s http://localhost:8000/openapi.json | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('components',{}).get('securitySchemes',{}))"
    Expected Result: 包含 Bearer 或 API Token 的 security scheme 定义
    Evidence: .sisyphus/evidence/task-5-openapi-security.json

  Scenario: Swagger UI 显示 Authorize 按钮
    Tool: Bash (curl)
    Steps:
      1. curl -s http://localhost:8000/openapi.json | grep -c "securitySchemes"
    Expected Result: count >= 1
    Evidence: .sisyphus/evidence/task-5-swagger-auth.txt
  ```

  **Commit**: YES
  - Message: `feat(api): mount public/protected routers and add OpenAPI security`
  - Files: `src/madousho/api/main.py`
  - Pre-commit: `pytest tests/api/ -v`

---

## Final Verification Wave

- [x] F1. **集成测试全量通过** — `pytest`
  运行 `pytest tests/api/test_auth.py -v` 确认所有鉴权测试通过
  运行 `pytest tests/api/test_health.py -v` 确认 health 端点测试未被破坏
  运行 `pytest --cov=src/madousho/api` 确认覆盖率 ≥ 90%
  Output: `Auth tests [N/N pass] | Health tests [N/N pass] | Coverage [≥90%] | VERDICT`

- [ ] F2. **端到端 curl 验证** — `Bash (curl)`
  启动服务，执行以下 curl 验证：
  1. `curl localhost:8000/api/v1/health` → 200, 无需 token
  2. `curl localhost:8000/api/v1/health -H "Authorization: Bearer <token>"` → 200
  3. `curl localhost:8000/api/v1/health -H "X-API-Token: <token>"` → 200
  4. `curl localhost:8000/api/v1/health -H "Authorization: Bearer wrong"` → 401
  5. `curl localhost:8000/api/v1/health` (无 token，假设有 protected 路由) → 401
  6. `curl -X OPTIONS localhost:8000/api/v1/health` → 不返回 401
  Output: `Scenarios [N/N pass] | VERDICT`

---

## Commit Strategy

1. `feat(api): add unified error response model` — `src/madousho/api/errors.py`
2. `feat(api): add verify_token dependency with TDD` — `src/madousho/api/deps.py`, `tests/api/test_auth.py`
3. `feat(api): split routes into public and protected routers` — `src/madousho/api/routes/__init__.py`
4. `feat(api): mount public/protected routers and add OpenAPI security` — `src/madousho/api/main.py`

---

## Success Criteria

### Verification Commands
```bash
# 测试通过
pytest tests/api/test_auth.py tests/api/test_health.py -v

# 覆盖率达标
pytest --cov=src/madousho/api --cov-fail-under=90

# health 公开可访问
curl -s http://localhost:8000/api/v1/health  # Expected: {"status":"ok"}

# 鉴权生效
curl -s http://localhost:8000/api/v1/health -H "Authorization: Bearer wrong"  # Expected: 401

# OpenAPI 安全方案
curl -s http://localhost:8000/openapi.json | jq '.components.securitySchemes'  # Expected: security scheme defined
```

### Final Checklist
- [x] verify_token 使用 secrets.compare_digest
- [x] 双 header 支持（Bearer + X-API-Token）
- [x] 统一错误格式 {"error": "...", "message": "..."}
- [x] health 端点无需鉴权
- [x] OPTIONS 跳过鉴权
- [x] OpenAPI security scheme 配置
- [x] TDD 测试全部通过 (16/16)
- [ ] 覆盖率 ≥ 90%（仅运行 API 测试时不达标，全量测试需另行验证）
