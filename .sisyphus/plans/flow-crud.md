# Flow CRUD API Implementation Plan

## TL;DR

> **Quick Summary**: 为 Flow 模型实现一套只读+创建的 CRUD 操作，通过 FastAPI RESTful API 暴露，所有端点需要认证，支持分页和过滤。
>
> **Deliverables**:
> - Pydantic schemas (FlowCreate, FlowResponse, FlowListResponse)
> - API 路由端点 (GET /flows, GET /flows/{uuid}, POST /flows)
> - TDD 测试套件 (先写测试，再实现)
> - Agent QA 验证场景
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Schemas → Tests → Routes

---

## Context

### Original Request
用户要求为 Flow 模型实现 CRUD 操作，通过 FastAPI RESTful API 暴露。

### Interview Summary
**Key Discussions**:
- **CRUD 范围**: 只读 + 创建（GET 列表、GET 详情、POST 创建）- 不需要更新和删除
- **认证策略**: 所有端点都需要 Bearer token 认证（使用 protected_router）
- **分页**: 支持 offset/limit 分页 + 过滤条件
- **过滤条件**: status, plugin, name 搜索
- **排序**: created_at 降序（最新在前）
- **创建响应**: 只返回 uuid，不返回完整对象
- **错误处理**: 使用现有 `errors.py` 的 ErrorResponse 模块
- **测试策略**: TDD - 先写测试再实现
- **输入验证**: Pydantic schemas (FlowCreate, FlowResponse 等)

### Research Findings
- Flow 模型已有完整定义（uuid, name, description, plugin, tasks, status, flow_template, created_at）
- 项目使用 `protected_router` 和 `public_router` 分离认证
- 数据库通过 `Depends(get_db)` 注入，使用上下文管理器自动 commit/rollback
- 现有测试模式：TestClient + MockConfig + pytest fixtures

---

## Work Objectives

### Core Objective
实现 Flow 模型的 RESTful CRUD API：列表查询（分页+过滤）、详情查询、创建操作。

### Concrete Deliverables
- `src/madousho/api/schemas/flow.py` - Pydantic schemas
- `src/madousho/api/routes/flow.py` - API 路由实现
- `tests/api/test_flow_crud.py` - TDD 测试套件

### Definition of Done
- [ ] GET /api/v1/flows 返回分页列表，支持 status/plugin/name 过滤
- [ ] GET /api/v1/flows/{uuid} 返回单个 Flow 详情
- [ ] POST /api/v1/flows 创建 Flow 并返回 uuid
- [ ] 所有端点需要认证（401 无 token）
- [ ] pytest 测试全部通过
- [ ] Agent QA 场景验证通过

### Must Have
- Pydantic schemas 进行输入验证
- 分页参数（offset, limit）
- 过滤参数（status, plugin, name）
- 使用现有 ErrorResponse 错误格式
- TDD 测试覆盖

### Must NOT Have (Guardrails)
- 不实现 PUT /flows/{uuid}（更新）
- 不实现 DELETE /flows/{uuid}（删除）
- 不绕过认证
- 不使用 autoincrement ID（必须用 UUID）
- 不直接调用 `Database()` - 必须用 `Database.get_instance()`

---

## Verification Strategy (MANDATORY)

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: TDD
- **Framework**: pytest
- **TDD workflow**: RED (failing tests) → GREEN (minimal impl) → REFACTOR

### QA Policy
每个任务包含 Agent-Executed QA 场景：
- **API**: Bash (curl) - 发送请求，断言状态码 + 响应字段
- **Evidence**: `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation):
├── Task 1: Pydantic schemas (FlowCreate, FlowResponse, FlowListResponse)
└── Task 2: TDD tests for all 3 endpoints

Wave 2 (Implementation - depends on Wave 1):
├── Task 3: Flow list endpoint (GET /flows) with pagination & filtering
├── Task 4: Flow detail endpoint (GET /flows/{uuid})
└── Task 5: Flow create endpoint (POST /flows)

Wave 3 (Integration):
└── Task 6: Wire routes into protected_router + Agent QA

Wave FINAL (Verification):
├── Task F1: Plan Compliance Audit (oracle)
├── Task F2: Code Quality Review (pytest + lint)
└── Task F3: Real Manual QA (curl all endpoints)
```

### Dependency Matrix
- **Task 1 (schemas)**: None → Tasks 3, 4, 5
- **Task 2 (tests)**: Task 1 → Task 3, 4, 5 (RED phase)
- **Task 3 (list)**: Tasks 1, 2 → Task 6
- **Task 4 (detail)**: Tasks 1, 2 → Task 6
- **Task 5 (create)**: Tasks 1, 2 → Task 6
- **Task 6 (wire)**: Tasks 3, 4, 5 → F1, F2, F3

---

## TODOs

- [x] 1. Create Pydantic schemas for Flow CRUD

  **What to do**:
  - Create `src/madousho/api/schemas/__init__.py` (empty module marker)
  - Create `src/madousho/api/schemas/flow.py` with:
    - `FlowCreate`: name (required), description (optional), plugin (required), flow_template (required)
      - **不包含 tasks** - tasks 在创建 Flow 后通过其他接口管理
    - `FlowResponse`: uuid, name, description, plugin, tasks, status, flow_template, created_at
    - `FlowListResponse`: items (list[FlowResponse]), total (int), offset (int), limit (int)
  - Use Pydantic v2 syntax (field validators, Field descriptions)
  - Follow existing patterns in `src/madousho/config/models.py`

  **Must NOT do**:
  - 不要创建 PUT/DELETE 相关的 schema
  - 不要在 FlowCreate 中包含 tasks（tasks 通过其他接口管理）
  - 不要在 schema 中包含 status 作为创建参数（使用默认值 "created"）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 单一文件创建，遵循现有 Pydantic 模式
  - **Skills**: []
    - No special skills needed for schema definition

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: Tasks 3, 4, 5
  - **Blocked By**: None (can start immediately)

  **References**:
  **Pattern References**:
  - `src/madousho/config/models.py` - Pydantic model 定义模式（Field, validator）

  **API/Type References**:
  - `src/madousho/models/flow.py` - Flow 模型字段定义，确保 schema 匹配

  **WHY Each Reference Matters**:
  - `config/models.py`: 参考 Pydantic v2 语法（model_config, Field 使用方式）
  - `models/flow.py`: 确保 schema 字段与 ORM 模型一一对应

  **Acceptance Criteria**:
  - [ ] `src/madousho/api/schemas/__init__.py` 创建
  - [ ] `src/madousho/api/schemas/flow.py` 创建，包含 3 个 schema 类
  - [ ] `from madousho.api.schemas.flow import FlowCreate, FlowResponse, FlowListResponse` 导入成功

  **QA Scenarios**:

  ```
  Scenario: Schema imports successfully
    Tool: Bash (python REPL)
    Preconditions: None
    Steps:
      1. Run `python -c "from madousho.api.schemas.flow import FlowCreate, FlowResponse, FlowListResponse; print('OK')"`
    Expected Result: 输出 "OK"，无 ImportError
    Failure Indicators: ImportError 或 ModuleNotFoundError
    Evidence: .sisyphus/evidence/task-1-schema-import.txt

  Scenario: FlowCreate validates required fields
    Tool: Bash (python REPL)
    Preconditions: None
    Steps:
      1. Run python -c 验证 FlowCreate 缺少必填字段时抛出 ValidationError
      2. Run python -c 验证 FlowCreate 接受有效数据
    Expected Result: 缺少 name/plugin 时 ValidationError，有效数据时成功
    Failure Indicators: 应该报错时没报错，或有效数据被拒绝
    Evidence: .sisyphus/evidence/task-1-validation.txt
  ```

  **Commit**: YES
  - Message: `feat(api): add Flow CRUD Pydantic schemas`
  - Files: `src/madousho/api/schemas/__init__.py`, `src/madousho/api/schemas/flow.py`
  - Pre-commit: `python -c "from madousho.api.schemas.flow import FlowCreate, FlowResponse, FlowListResponse"`

---

- [x] 2. Write TDD tests for Flow CRUD endpoints (RED phase)

  **What to do**:
  - Create `tests/api/test_flow_crud.py` with comprehensive tests:
    - `TestFlowListEndpoint`: GET /api/v1/flows
      - 返回 200 和分页数据
      - offset/limit 分页参数生效
      - status 过滤
      - plugin 过滤
      - name 搜索（模糊匹配）
      - created_at 降序排序
      - 空列表返回正确格式
    - `TestFlowDetailEndpoint`: GET /api/v1/flows/{uuid}
      - 存在的 uuid 返回 200 和完整数据
      - 不存在的 uuid 返回 404
    - `TestFlowCreateEndpoint`: POST /api/v1/flows
      - 有效数据返回 201 和 uuid
      - 缺少必填字段返回 422
      - 无效数据返回 422
    - `TestFlowAuthRequired`: 所有端点无 token 返回 401
  - 使用现有 fixtures 模式（MockConfig, TestClient, reset_singleton）
  - 使用 in-memory SQLite 数据库

  **Must NOT do**:
  - 不要测试 PUT/DELETE 端点
  - 不要使用真实数据库或文件数据库

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 测试文件创建，遵循现有测试模式
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Tasks 3, 4, 5 (RED phase - tests should fail)
  - **Blocked By**: None

  **References**:
  **Pattern References**:
  - `tests/api/test_auth.py` - 测试结构、MockConfig 模式、fixtures
  - `tests/test_flow_model.py` - Database singleton reset 模式

  **Test References**:
  - `tests/api/test_health.py:TestHealthEndpoint` - TestClient 使用模式

  **WHY Each Reference Matters**:
  - `test_auth.py`: 学习认证测试模式（MockConfig, monkeypatch）
  - `test_flow_model.py`: 学习 in-memory 数据库 fixture 模式
  - `test_health.py`: 学习基本 TestClient 断言模式

  **Acceptance Criteria**:
  - [ ] `tests/api/test_flow_crud.py` 创建
  - [ ] 至少 15 个测试用例
  - [ ] 运行 `pytest tests/api/test_flow_crud.py` 时所有测试 FAIL（RED phase）

  **QA Scenarios**:

  ```
  Scenario: Tests exist and are discoverable
    Tool: Bash (pytest collect)
    Preconditions: None
    Steps:
      1. Run `pytest tests/api/test_flow_crud.py --collect-only`
    Expected Result: 收集到至少 15 个测试用例
    Failure Indicators: 无测试收集或数量不足
    Evidence: .sisyphus/evidence/task-2-collect.txt

  Scenario: All tests fail (RED phase)
    Tool: Bash (pytest)
    Preconditions: Routes not yet implemented
    Steps:
      1. Run `pytest tests/api/test_flow_crud.py -v`
    Expected Result: 所有测试 FAIL（因为端点尚未实现）
    Failure Indicators: 测试意外通过
    Evidence: .sisyphus/evidence/task-2-red-phase.txt
  ```

  **Commit**: YES
  - Message: `test(api): add Flow CRUD endpoint tests (RED phase)`
  - Files: `tests/api/test_flow_crud.py`
  - Pre-commit: `pytest tests/api/test_flow_crud.py --collect-only`

---

- [x] 3. Implement Flow list endpoint (GET /api/v1/flows)

  **What to do**:
  - Create `src/madousho/api/routes/flow.py`
  - Implement `GET /flows` endpoint:
    - Query parameters: offset (default 0), limit (default 20, max 100)
    - Filter parameters: status, plugin, name (optional)
    - Return `FlowListResponse` with items, total, offset, limit
    - Order by created_at DESC
    - Use `Depends(get_db)` for database session
  - Handle edge cases: invalid offset/limit, empty results

  **Must NOT do**:
  - 不要直接在端点中编写 SQL
  - 不要绕过 Pydantic schema 返回

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 需要数据库查询逻辑和参数处理
  - **Skills**: []
    - Standard Python/FastAPI knowledge sufficient

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4, 5)
  - **Blocks**: Task 6
  - **Blocked By**: Tasks 1, 2

  **References**:
  **Pattern References**:
  - `src/madousho/api/routes/__init__.py` - 路由定义模式

  **API/Type References**:
  - `src/madousho/api/schemas/flow.py` (Task 1) - FlowListResponse schema
  - `src/madousho/models/flow.py` - Flow ORM 模型

  **Test References**:
  - `tests/api/test_flow_crud.py:TestFlowListEndpoint` (Task 2) - 预期行为

  **WHY Each Reference Matters**:
  - `routes/__init__.py`: 参考 router 装饰器和依赖注入模式
  - `schemas/flow.py`: 确保返回格式匹配 FlowListResponse
  - `models/flow.py`: 确保查询字段正确

  **Acceptance Criteria**:
  - [ ] GET /api/v1/flows 返回 200 和分页数据
  - [ ] offset/limit 参数正常工作
  - [ ] status/plugin/name 过滤生效
  - [ ] TestFlowListEndpoint 测试通过

  **QA Scenarios**:

  ```
  Scenario: List flows returns paginated data
    Tool: Bash (curl)
    Preconditions: API server running, valid auth token
    Steps:
      1. curl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/flows
    Expected Result: 200, JSON with items (array), total (int), offset (int), limit (int)
    Failure Indicators: 非 200 状态码，缺少分页字段
    Evidence: .sisyphus/evidence/task-3-list-basic.txt

  Scenario: List with filters
    Tool: Bash (curl)
    Preconditions: API server with some Flows, valid token
    Steps:
      1. curl -H "Authorization: Bearer {token}" "http://localhost:8000/api/v1/flows?status=created&limit=5"
    Expected Result: 200, 只返回 status="created" 的 Flow，最多 5 条
    Failure Indicators: 返回了其他状态的 Flow 或超过 5 条
    Evidence: .sisyphus/evidence/task-3-list-filtered.txt
  ```

  **Commit**: YES (group with Tasks 4, 5)
  - Message: `feat(api): implement Flow list endpoint with pagination`
  - Files: `src/madousho/api/routes/flow.py`
  - Pre-commit: `pytest tests/api/test_flow_crud.py::TestFlowListEndpoint -v`

---

- [x] 4. Implement Flow detail endpoint (GET /api/v1/flows/{uuid})

  **What to do**:
  - In `src/madousho/api/routes/flow.py`, implement `GET /flows/{uuid}`:
    - Path parameter: uuid (Flow 的主键)
    - Return `FlowResponse` with full Flow data
    - Return 404 with ErrorResponse if not found
    - Use `Depends(get_db)` for database session

  **Must NOT do**:
  - 不要返回 500 当 Flow 不存在时（必须返回 404）
  - 不要泄露内部错误信息

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单的单记录查询
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 3, 5)
  - **Blocks**: Task 6
  - **Blocked By**: Tasks 1, 2

  **References**:
  **API/Type References**:
  - `src/madousho/api/schemas/flow.py` (Task 1) - FlowResponse schema
  - `src/madousho/api/errors.py` - ErrorResponse 和 error_response 函数

  **WHY Each Reference Matters**:
  - `schemas/flow.py`: 确保返回格式匹配 FlowResponse
  - `errors.py`: 使用统一的错误响应格式

  **Acceptance Criteria**:
  - [ ] GET /api/v1/flows/{uuid} 返回 200 和完整 Flow 数据
  - [ ] 不存在的 uuid 返回 404 和 ErrorResponse
  - [ ] TestFlowDetailEndpoint 测试通过

  **QA Scenarios**:

  ```
  Scenario: Get existing flow by uuid
    Tool: Bash (curl)
    Preconditions: 已创建一个 Flow，知道其 uuid
    Steps:
      1. curl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/flows/{uuid}
    Expected Result: 200, JSON 包含 uuid, name, description, plugin, status, created_at
    Failure Indicators: 非 200 或缺少字段
    Evidence: .sisyphus/evidence/task-4-detail-found.txt

  Scenario: Get non-existent flow returns 404
    Tool: Bash (curl)
    Preconditions: 使用不存在的 uuid（如 "00000000-0000-0000-0000-000000000000"）
    Steps:
      1. curl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/flows/00000000-0000-0000-0000-000000000000
    Expected Result: 404, JSON with error and message fields
    Failure Indicators: 非 404 或缺少错误字段
    Evidence: .sisyphus/evidence/task-4-detail-notfound.txt
  ```

  **Commit**: YES (group with Tasks 3, 5)
  - Message: `feat(api): implement Flow detail endpoint`
  - Files: `src/madousho/api/routes/flow.py`
  - Pre-commit: `pytest tests/api/test_flow_crud.py::TestFlowDetailEndpoint -v`

---

- [x] 5. Implement Flow create endpoint (POST /api/v1/flows)

  **What to do**:
  - In `src/madousho/api/routes/flow.py`, implement `POST /flows`:
    - Request body: `FlowCreate` schema
    - Create Flow in database with default status="created"
    - Return 201 with `{"uuid": "..."}` (只返回 uuid)
    - Handle validation errors with 422
    - Use `Depends(get_db)` for database session
    - Generate UUID automatically

  **Must NOT do**:
  - 不要允许客户端设置 uuid（自动生成）
  - 不要允许客户端设置 status（默认 "created"）
  - 不要接受 tasks 参数（tasks 通过其他接口管理）
  - 不要返回完整对象（只返回 uuid）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单的创建操作
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 3, 4)
  - **Blocks**: Task 6
  - **Blocked By**: Tasks 1, 2

  **References**:
  **Pattern References**:
  - `src/madousho/models/flow.py:Flow` - 模型创建模式

  **API/Type References**:
  - `src/madousho/api/schemas/flow.py` (Task 1) - FlowCreate schema

  **WHY Each Reference Matters**:
  - `flow.py`: 确保创建时使用正确的字段和默认值

  **Acceptance Criteria**:
  - [ ] POST /api/v1/flows 返回 201 和 {"uuid": "..."}
  - [ ] 缺少必填字段返回 422
  - [ ] uuid 和 status 自动生成（不接受客户端设置）
  - [ ] TestFlowCreateEndpoint 测试通过

  **QA Scenarios**:

  ```
  Scenario: Create flow with valid data
    Tool: Bash (curl)
    Preconditions: API server running, valid auth token
    Steps:
      1. curl -X POST -H "Authorization: Bearer {token}" -H "Content-Type: application/json" -d '{"name":"Test Flow","plugin":"test-plugin","flow-template":"my-template"}' http://localhost:8000/api/v1/flows
    Expected Result: 201, JSON with uuid field (valid UUID format)
    Failure Indicators: 非 201，或响应中没有 uuid
    Evidence: .sisyphus/evidence/task-5-create-success.txt

  Scenario: Create flow with missing required fields
    Tool: Bash (curl)
    Preconditions: API server running, valid auth token
    Steps:
      1. curl -X POST -H "Authorization: Bearer {token}" -H "Content-Type: application/json" -d '{"description":"missing name and plugin"}' http://localhost:8000/api/v1/flows
    Expected Result: 422, validation error details
    Failure Indicators: 非 422 或接受了无效数据
    Evidence: .sisyphus/evidence/task-5-create-validation.txt
  ```

  **Commit**: YES (group with Tasks 3, 4)
  - Message: `feat(api): implement Flow create endpoint`
  - Files: `src/madousho/api/routes/flow.py`
  - Pre-commit: `pytest tests/api/test_flow_crud.py::TestFlowCreateEndpoint -v`

---

- [x] 6. Wire Flow routes into protected_router and run Agent QA

  **What to do**:
  - In `src/madousho/api/routes/__init__.py`, import and include flow_router:
    - `from madousho.api.routes.flow import flow_router`
    - `protected_router.include_router(flow_router, prefix="/flows", tags=["flows"])`
  - Verify all endpoints are accessible under `/api/v1/flows`
  - Run all pytest tests to ensure GREEN phase
  - Execute all QA scenarios from Tasks 3, 4, 5

  **Must NOT do**:
  - 不要将 flow_router 挂载到 public_router
  - 不要修改现有的 public_router 或 protected_router 逻辑

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 路由注册和测试验证
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (depends on Tasks 3, 4, 5)
  - **Blocks**: F1, F2, F3
  - **Blocked By**: Tasks 3, 4, 5

  **References**:
  **Pattern References**:
  - `src/madousho/api/routes/__init__.py` - router 注册模式

  **WHY Each Reference Matters**:
  - 参考现有 router 注册方式，确保一致

  **Acceptance Criteria**:
  - [ ] flow_router 已注册到 protected_router
  - [ ] `pytest tests/api/test_flow_crud.py` 全部通过（GREEN phase）
  - [ ] 所有 QA 场景验证通过

  **QA Scenarios**:

  ```
  Scenario: All tests pass (GREEN phase)
    Tool: Bash (pytest)
    Preconditions: All implementations complete
    Steps:
      1. Run `pytest tests/api/test_flow_crud.py -v`
    Expected Result: 所有测试 PASS
    Failure Indicators: 任何测试 FAIL
    Evidence: .sisyphus/evidence/task-6-green-phase.txt

  Scenario: Auth enforcement verified
    Tool: Bash (curl)
    Preconditions: API server running
    Steps:
      1. curl http://localhost:8000/api/v1/flows (no auth)
      2. curl http://localhost:8000/api/v1/flows/{uuid} (no auth)
      3. curl -X POST http://localhost:8000/api/v1/flows (no auth)
    Expected Result: 所有请求返回 401
    Failure Indicators: 任何端点返回非 401
    Evidence: .sisyphus/evidence/task-6-auth-enforcement.txt
  ```

  **Commit**: YES
  - Message: `feat(api): wire Flow routes to protected_router`
  - Files: `src/madousho/api/routes/__init__.py`
  - Pre-commit: `pytest tests/api/test_flow_crud.py -v`

---

## Final Verification Wave (MANDATORY)

- [x] F1. **Plan Compliance Audit** - `oracle`
  Must Have [6/6] | Must NOT Have [5/5] | VERDICT: APPROVE
  - GET /api/v1/flows exists with pagination + filtering ✓
  - GET /api/v1/flows/{uuid} returns FlowResponse ✓
  - POST /api/v1/flows returns {uuid} only (201) ✓
  - All endpoints require auth (protected_router) ✓
  - No PUT/DELETE endpoints ✓
  - ErrorResponse format for errors ✓

- [x] F2. **Code Quality Review** - `unspecified-high`
  Tests [103/103 PASS] | Files [3 clean/0 issues] | VERDICT: APPROVE

- [x] F3. **Real Manual QA** - `unspecified-high`
  Scenarios [9/9 pass] | VERDICT: APPROVE
  - Create → List → Detail flow works
  - Filtering by plugin works
  - 404 returns ErrorResponse
  - 422 for missing required fields
  - 401 without auth
  - 405 for PUT/DELETE (correctly not implemented)

---

## Commit Strategy

- **1-2**: `feat(api): add schemas + test` - schemas + tests
- **3-5**: `feat(api): implement CRUD endpoints` - all 3 endpoints
- **6**: `feat(api): wire routes` - router registration

---

## Success Criteria

### Verification Commands
```bash
# Run all tests
pytest tests/api/test_flow_crud.py -v

# Test list endpoint
curl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/flows

# Test detail endpoint
curl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/flows/{uuid}

# Test create endpoint
curl -X POST -H "Authorization: Bearer {token}" -H "Content-Type: application/json" \
  -d '{"name":"Test","plugin":"test-plugin"}' http://localhost:8000/api/v1/flows
```

### Final Checklist
- [ ] GET /api/v1/flows 分页+过滤
- [ ] GET /api/v1/flows/{uuid} 详情
- [ ] POST /api/v1/flows 创建返回 uuid
- [ ] 所有端点认证
- [ ] 无 PUT/DELETE 端点
- [ ] pytest 全部通过
