# Login Page with Multi-Backend Support

## TL;DR

> **Quick Summary**: Build a login page with 70/30 split layout (gradient left, inputs right), supporting multiple backend credentials with a top-bar switcher. Auth via `/api/v1/protected` endpoint. Pinia store drives reactive API client baseURL. TDD with vitest.
>
> **Deliverables**:
> - Auth Pinia store (multi-backend credentials, current selection)
> - Login page view (`/login`)
> - Top-bar backend switcher component
> - Route guard (redirect to `/login` on 401/unauth)
> - Dynamic API client (baseURL from store)
> - MSW mocks for `/protected` endpoint
> - Vitest tests (TDD)
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Auth Store → API Client Update → Login Page → Route Guard → Top Bar

---

## Context

### Original Request
用户要求创建登录页面：左边 70% 渐变占位图，右边 30% 输入框（API base URL + token）。通过 `/protected` 端点验证鉴权。支持多后端凭证切换。未来其他页面 API 请求返回鉴权错误时跳转到登录页。

### Interview Summary
**Key Discussions**:
- Base URL 输入：用户输入 host+port（如 `http://localhost:8000`），前端自动拼接 `/api/v1`
- 后端切换 UI：放在 App.vue 顶栏，登录后始终可见
- API Client 动态 baseURL：Pinia auth store 响应式驱动，Axios interceptor 从 store 读取
- 凭证存储：数组格式 `[{baseUrl, name?, token}]` + `currentBackendIndex` 存 localStorage
- 路由结构：仅 `/login`，本次不做 Dashboard 骨架
- 测试策略：TDD，使用 vitest
- 登录页图片：渐变占位图

### Research Findings
- 后端已有 `/api/v1/protected` 端点（`routes/__init__.py:24`），返回 `{"message": "authenticated"}`
- 前端 API client（`src/api/client.ts`）Axios 实例 baseURL 写死 `/api/v1`，token 从 `localStorage.getItem('authToken')` 读取
- 路由（`src/router/index.ts`）为空
- 无现有 auth store
- 401/403 拦截器仅 `console.error`，无跳转逻辑

---

## Work Objectives

### Core Objective
实现完整的前端鉴权基础设施：登录页面 + 多后端凭证管理 + 路由守卫 + 动态 API client

### Concrete Deliverables
1. `frontend/src/stores/auth.store.ts` — Auth Pinia store（多后端凭证、当前选择、登录/登出/切换）
2. `frontend/src/views/LoginView.vue` — 登录页面（70/30 布局）
3. `frontend/src/views/HomeView.vue` — 最小占位页（「已连接」状态 + 后端切换器）
4. `frontend/src/components/BackendSwitcher.vue` — 顶栏后端切换器
5. `frontend/src/router/index.ts` — 路由（/login, /）+ beforeEach 守卫
6. `frontend/src/api/client.ts` — 改为从 auth store 读 baseURL
7. `frontend/src/mocks/handlers.ts` — MSW mock for `/protected`
8. `frontend/src/App.vue` — 更新为包含 BackendSwitcher + RouterView
9. 测试文件：auth store tests + login form tests + API client tests

### Definition of Done
- [ ] 访问 `/login` 显示登录页面（70% 渐变 + 30% 输入框）
- [ ] 输入 base URL + token，点击登录 → 调用 `/api/v1/protected` 验证
- [ ] 验证成功 → 凭证保存到 localStorage，跳转 `/`（最小占位页）
- [ ] `/` 显示「已连接」状态 + 后端切换器
- [ ] App.vue 顶栏显示后端切换下拉
- [ ] 切换后端 → auth store 更新 → API client baseURL 自动切换
- [ ] 未鉴权访问 `/` → 重定向到 `/login`
- [ ] 已鉴权访问 `/login` → 重定向到 `/`
- [ ] vitest 测试全部通过

### Must Have
- 多后端凭证持久化（localStorage）
- API client baseURL 响应式切换
- 路由守卫
- TDD 测试覆盖

### Must NOT Have (Guardrails)
- 不修改后端代码
- 不创建 Dashboard 页面
- 不过度工程化（不做 encryption、refresh token 等）
- AI slop 避免：不加多余注释、不过度抽象

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (vitest + jsdom)
- **Automated tests**: TDD
- **Framework**: vitest
- **TDD approach**: RED (failing test) → GREEN (minimal impl) → REFACTOR

### QA Policy
Every task includes agent-executed QA scenarios.
- **Frontend/UI**: Playwright — 表单填写、按钮点击、DOM 断言、截图
- **Store/Logic**: vitest — 状态变更、getter 计算、action 调用
- **API client**: vitest + MSW — 拦截器行为、baseURL 动态切换

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation — no dependencies):
├── Task 1: Auth Pinia store (types, state, actions, localStorage persistence)
├── Task 2: LoginView.vue (70/30 layout, form, gradient)
├── Task 3: HomeView.vue (minimal placeholder — connected status)
├── Task 4: MSW mock handlers (/protected endpoint)
├── Task 5: Auth store vitest tests (TDD - write tests first)
└── Task 6: LoginView vitest tests (TDD - write tests first)

Wave 2 (Core integration — depends on Wave 1):
├── Task 7: Update API client (dynamic baseURL from auth store)
├── Task 8: Update router (/login, / routes + beforeEach guard)
├── Task 9: API client vitest tests (TDD)
└── Task 10: Router guard vitest tests (TDD)

Wave 3 (UI integration — depends on Wave 2):
├── Task 11: BackendSwitcher.vue component (top bar dropdown)
├── Task 12: Update App.vue (add BackendSwitcher + clean up boilerplate)
├── Task 13: BackendSwitcher vitest tests (TDD)
└── Task 14: E2E Playwright QA (full login flow, backend switching)

Wave FINAL (Verification — after ALL tasks):
├── F1: Plan compliance audit (oracle)
├── F2: Code quality review (vitest + lint)
├── F3: Real manual QA (Playwright)
└── F4: Scope fidelity check (deep)
```

### Dependency Matrix
- **T1** (auth store): None → T5, T7, T8, T11
- **T2** (login view): None → T6
- **T3** (home view): None
- **T4** (MSW mocks): None → T14
- **T5** (auth store tests): T1
- **T6** (login tests): T2
- **T7** (API client update): T1 → T9
- **T8** (router update): T1, T2, T3 → T10, T11
- **T9** (API client tests): T7
- **T10** (router guard tests): T8
- **T11** (switcher): T1, T8 → T12, T13
- **T12** (App.vue update): T11
- **T13** (switcher tests): T11
- **T14** (E2E QA): T4, T12

---

## TODOs

### Wave 1

- [x] 1. Auth Pinia Store

  **What to do**:
  - Create `frontend/src/stores/auth.store.ts`
  - Define types: `Backend { baseUrl: string; token: string; name?: string }`
  - State: `backends: Backend[]`, `currentBackendIndex: number`, `isAuthenticated: boolean`, `loading: boolean`
  - Getters: `currentBackend`, `currentBaseUrl`, `currentToken`, `backendOptions` (for dropdown)
  - Actions:
    - `login(baseUrl, token)`: Call `/api/v1/protected` with temp client → if 200, add/update backend, set current, persist
    - `logout()`: Clear current (keep saved backends), reset auth state
    - `switchBackend(index)`: Switch current index, persist
    - `removeBackend(index)`: Remove from list, adjust current index
    - `loadFromStorage()`: Hydrate from localStorage on app init
    - `persist()`: Save `backends` array + `currentBackendIndex` to localStorage key `madousho_backends`
  - Auto-load from localStorage on store creation
  - Base URL normalization: strip trailing `/`, append nothing (API client adds `/api/v1`)

  **Must NOT do**:
  - Do not hardcode `/api/v1` in the store — that belongs to the API client
  - Do not create the API client instance here — import from `@/api/client`

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Pinia store boilerplate, straightforward state management
  - **Skills**: []
    - No specialized skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with T2, T3, T4, T5)
  - **Blocks**: T4, T6, T7, T10
  - **Blocked By**: None

  **References**:
  - `frontend/src/stores/modules/example.store.ts` — Pinia store pattern (defineStore, state/getters/actions)
  - `frontend/src/stores/index.ts` — Central re-export pattern
  - `frontend/src/api/client.ts` — Existing API client (import for login verification call)

  **Acceptance Criteria**:
  - [ ] Store created with all types, state, getters, actions
  - [ ] `login()` creates temp Axios call to `{baseUrl}/api/v1/protected` with Bearer token
  - [ ] `persist()` saves to `localStorage.madousho_backends` as JSON
  - [ ] `loadFromStorage()` hydrates state on store init
  - [ ] Re-exported in `frontend/src/stores/index.ts`

  **QA Scenarios**:

  ```
  Scenario: Login with valid credentials saves backend
    Tool: vitest
    Preconditions: Mock axios to return 200 from /protected
    Steps:
      1. Create auth store instance
      2. Call login('http://localhost:8000', 'test-token')
      3. Assert isAuthenticated === true
      4. Assert backends.length === 1
      5. Assert currentBackendIndex === 0
      6. Assert localStorage contains saved backend
    Expected Result: Backend saved, state authenticated
    Evidence: .sisyphus/evidence/task-1-login-success.txt

  Scenario: Login with invalid token rejects
    Tool: vitest
    Preconditions: Mock axios to return 401 from /protected
    Steps:
      1. Create auth store instance
      2. Call login('http://localhost:8000', 'bad-token')
      3. Assert isAuthenticated === false
      4. Assert backends.length === 0
    Expected Result: Auth state unchanged, error thrown/returned
    Evidence: .sisyphus/evidence/task-1-login-fail.txt
  ```

  **Commit**: YES (group with T4)
  - Message: `feat(auth): add auth store with multi-backend support`
  - Files: `frontend/src/stores/auth.store.ts`, `frontend/src/stores/index.ts`

---

- [x] 2. LoginView.vue

  **What to do**:
  - Create `frontend/src/views/LoginView.vue`
  - Layout: CSS flexbox/grid — left 70% gradient background, right 30% login form
  - Form fields: Base URL (text input), Token (password input)
  - Login button: calls `authStore.login(baseUrl, token)`
  - Loading state during login attempt
  - Error display on auth failure (Naive UI `NAlert`)
  - On success: redirect via `router.push('/')`
  - Gradient: CSS linear-gradient (dark purple/blue tones matching project aesthetic)
  - Responsive: on mobile (<768px), stack vertically (form on top, image below)

  **Must NOT do**:
  - Do not hardcode backend URLs
  - Do not manage auth logic outside the store — call `authStore.login()`

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: UI layout, CSS, form design
  - **Skills**: []
    - No specialized skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with T1, T3, T4, T5)
  - **Blocks**: T5
  - **Blocked By**: None

  **References**:
  - `frontend/src/views/HomeView.vue` — View component pattern (script setup + template + scoped style)
  - `frontend/package.json` — Naive UI is installed globally (no import needed)
  - `frontend/src/assets/main.css` — Existing CSS variables for colors

  **Acceptance Criteria**:
  - [ ] Page renders 70/30 split layout
  - [ ] Left side shows gradient background
  - [ ] Right side has Base URL input, Token input, Login button
  - [ ] Form validates inputs (non-empty) before submission
  - [ ] Loading spinner during login
  - [ ] Error alert on auth failure
  - [ ] Redirect on success

  **QA Scenarios**:

  ```
  Scenario: Render login page with correct layout
    Tool: vitest (jsdom)
    Preconditions: Mount component with router + pinia
    Steps:
      1. Mount LoginView
      2. Assert left panel exists with gradient class
      3. Assert right panel contains form
      4. Assert Base URL input exists
      5. Assert Token input exists (type=password)
      6. Assert Login button exists
    Expected Result: All elements present, 70/30 layout via CSS
    Evidence: .sisyphus/evidence/task-2-render.txt

  Scenario: Submit login with empty fields shows validation
    Tool: vitest (jsdom)
    Preconditions: Mount component
    Steps:
      1. Click Login button without filling inputs
      2. Assert validation error shown
      3. Assert no API call made
    Expected Result: Form validation blocks submission
    Evidence: .sisyphus/evidence/task-2-validation.txt
  ```

  **Commit**: YES (group with T5)
  - Message: `feat(auth): add login page with 70/30 layout`
  - Files: `frontend/src/views/LoginView.vue`

---

- [x] 3. HomeView.vue (Minimal Placeholder)

  **What to do**:
  - Modify existing `frontend/src/views/HomeView.vue`
  - Minimal page: centered content showing "已连接" (Connected) status
  - Display current backend URL from `authStore.currentBaseUrl`
  - Include `BackendSwitcher` component inline (not just in top bar)
  - Simple layout: welcome text + connection info + backend selector
  - No complex functionality — pure placeholder for future features

  **Must NOT do**:
  - Do not add any feature logic (flows, tasks, etc.)
  - Do not make it complex — this is a stub

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple placeholder page, minimal template
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with T1, T2, T4, T5, T6)
  - **Blocks**: T8 (router needs this component)
  - **Blocked By**: None

  **References**:
  - `frontend/src/views/HomeView.vue` — Existing file to modify
  - `frontend/src/stores/auth.store.ts` — `currentBaseUrl` getter

  **Acceptance Criteria**:
  - [ ] Page displays "已连接" or similar status text
  - [ ] Shows current backend URL
  - [ ] Includes backend switcher or link to switch
  - [ ] Simple, clean layout

  **Commit**: YES
  - Message: `feat(auth): add minimal home placeholder page`
  - Files: `frontend/src/views/HomeView.vue`

---

- [x] 4. MSW Mock Handlers

  **What to do**:
  - Update `frontend/src/mocks/handlers.ts`
  - Add handler: `GET /api/v1/protected` — check Authorization header, return 200 or 401
  - Handler accepts any baseURL path (since frontend may connect to different hosts)
  - Valid tokens: return `{"message": "authenticated"}`
  - Missing/invalid tokens: return 401 `{"error": "invalid_token", "message": "..."}`

  **Must NOT do**:
  - Do not mock other endpoints yet (only `/protected`)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple MSW handler setup
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: T13
  - **Blocked By**: None

  **References**:
  - `frontend/src/mocks/handlers.ts` — Current (empty) handlers array
  - `src/madousho/api/auth.py` — Backend auth logic (token validation)
  - `src/madousho/api/errors.py` — Error format constants

  **Acceptance Criteria**:
  - [ ] GET /api/v1/protected with valid Bearer → 200 + `{"message": "authenticated"}`
  - [ ] GET /api/v1/protected without token → 401
  - [ ] GET /api/v1/protected with wrong token → 401

  **QA Scenarios**:

  ```
  Scenario: MSW returns 200 for valid token
    Tool: vitest + MSW
    Preconditions: MSW worker started
    Steps:
      1. Fetch /api/v1/protected with Authorization: Bearer valid
      2. Assert response status 200
      3. Assert body contains message: "authenticated"
    Expected Result: 200 response
    Evidence: .sisyphus/evidence/task-3-msw-valid.txt

  Scenario: MSW returns 401 for missing token
    Tool: vitest + MSW
    Preconditions: MSW worker started
    Steps:
      1. Fetch /api/v1/protected without Authorization header
      2. Assert response status 401
    Expected Result: 401 response
    Evidence: .sisyphus/evidence/task-3-msw-invalid.txt
  ```

  **Commit**: YES
  - Message: `test(auth): add MSW mock for /protected endpoint`
  - Files: `frontend/src/mocks/handlers.ts`

---

- [x] 4. Auth Store Tests (TDD)

  **What to do**:
  - Create `frontend/src/stores/__tests__/auth.store.test.ts`
  - Tests (write BEFORE implementation — TDD):
    - `login()` with valid credentials → sets isAuthenticated, saves backend
    - `login()` with invalid credentials → throws error, state unchanged
    - `logout()` → clears isAuthenticated, keeps saved backends
    - `switchBackend(index)` → updates currentBackendIndex
    - `removeBackend(index)` → removes backend, adjusts index
    - `loadFromStorage()` → hydrates from localStorage
    - `persist()` → saves correct format to localStorage
    - `currentBackend` getter → returns correct backend
    - Multiple backends → can add and switch between them

  **Must NOT do**:
  - Do not test the API client integration here (that's T8)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Unit test boilerplate
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: None (verifies T1)
  - **Blocked By**: T1 (tests validate T1 implementation)

  **References**:
  - `frontend/src/stores/counter.ts` — Existing store test patterns
  - `frontend/vitest.config.ts` — Test configuration

  **Acceptance Criteria**:
  - [ ] All test cases written
  - [ ] Tests pass against auth store implementation
  - [ ] Coverage: login, logout, switch, remove, persist, hydrate

  **Commit**: YES (group with T1)

---

- [x] 5. LoginView Tests (TDD)

  **What to do**:
  - Create `frontend/src/views/__tests__/LoginView.test.ts`
  - Tests:
    - Renders 70/30 layout (check CSS classes/structure)
    - Contains Base URL input, Token input, Login button
    - Empty form validation blocks submission
    - Successful login redirects
    - Failed login shows error

  **Must NOT do**:
  - Do not test auth store logic (that's T4)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Component test with Vue Test Utils
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: None
  - **Blocked By**: T2

  **Commit**: YES (group with T2)

---

### Wave 2

- [x] 6. Update API Client

  **What to do**:
  - Modify `frontend/src/api/client.ts`
  - Change: `baseURL` no longer hardcoded — read from auth store
  - Implementation: Create a helper `getBaseURL()` that reads from `useAuthStore().currentBaseUrl`
  - Append `/api/v1` to the base URL
  - Keep Bearer token interceptor — now reads from `useAuthStore().currentToken`
  - Response interceptor: on 401 → call `authStore.logout()` + redirect to `/login`
  - Handle circular dependency carefully: use dynamic import or lazy store access

  **Must NOT do**:
  - Do not import auth store at module top level (circular dep risk) — use lazy access
  - Do not change the interceptor error handling structure

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Focused change to existing interceptor
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on T1 auth store)
  - **Parallel Group**: Wave 2 (with T7, T8, T9)
  - **Blocks**: T8
  - **Blocked By**: T1

  **References**:
  - `frontend/src/api/client.ts:5-11` — Current hardcoded baseURL
  - `frontend/src/api/client.ts:14-28` — Request interceptor pattern
  - `frontend/src/api/client.ts:31-49` — Response interceptor pattern

  **Acceptance Criteria**:
  - [ ] baseURL dynamically read from auth store
  - [ ] Token dynamically read from auth store
  - [ ] 401 response triggers logout + redirect
  - [ ] No circular import issues

  **QA Scenarios**:

  ```
  Scenario: API client uses store baseURL
    Tool: vitest
    Preconditions: Auth store with backend 'http://test:8000'
    Steps:
      1. Set auth store current backend
      2. Make API call via client
      3. Assert request URL starts with 'http://test:8000/api/v1'
    Expected Result: Request uses correct baseURL
    Evidence: .sisyphus/evidence/task-6-baseurl.txt

  Scenario: 401 triggers logout
    Tool: vitest
    Preconditions: Auth store authenticated, mock returns 401
    Steps:
      1. Make API call
      2. Assert response interceptor triggered
      3. Assert auth store isAuthenticated === false
    Expected Result: Auto-logout on 401
    Evidence: .sisyphus/evidence/task-6-logout.txt
  ```

  **Commit**: YES
  - Message: `feat(auth): dynamic API client baseURL from auth store`
  - Files: `frontend/src/api/client.ts`

---

- [x] 8. Update Router

  **What to do**:
  - Modify `frontend/src/router/index.ts`
  - Routes:
    ```typescript
    { path: '/login', name: 'login', component: LoginView }
    { path: '/', name: 'home', component: HomeView }
    ```
  - **No catch-all route** — unknown paths show empty RouterView
  - `beforeEach` guard:
    - If `to.path === '/login'` AND `authStore.isAuthenticated` → redirect `/`
    - If `to.path !== '/login'` AND `!authStore.isAuthenticated` → redirect `/login`
    - Else → allow
  - Import auth store lazily to avoid circular deps

  **Must NOT do**:
  - Do not add catch-all redirect (causes infinite loop without dashboard)
  - Do not hardcode auth check — use the auth store

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Router config, straightforward
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on T1, T2, T3)
  - **Parallel Group**: Wave 2
  - **Blocks**: T10, T11
  - **Blocked By**: T1, T2, T3

  **References**:
  - `frontend/src/router/index.ts` — Current empty router
  - `frontend/src/views/LoginView.vue` — Login page (from T2)
  - `frontend/src/views/HomeView.vue` — Home placeholder (from T3)

  **Acceptance Criteria**:
  - [ ] `/login` renders LoginView, `/` renders HomeView
  - [ ] Unauthenticated access to `/` → redirect to `/login`
  - [ ] Authenticated access to `/login` → redirect to `/`
  - [ ] No infinite redirect loops

  **Commit**: YES
  - Message: `feat(auth): add /login and / routes with auth guard`
  - Files: `frontend/src/router/index.ts`

---

- [x] 9. API Client Tests (TDD)

  **What to do**:
  - Create `frontend/src/api/__tests__/client.test.ts`
  - Tests:
    - baseURL is read from auth store
    - Bearer token header is set from auth store
    - 401 response triggers auth store logout
    - Requests without auth store state use default/empty values

  **Commit**: YES (group with T7)

---

- [x] 10. Router Guard Tests (TDD)

  **What to do**:
  - Create `frontend/src/router/__tests__/guard.test.ts`
  - Tests:
    - Unauthenticated user accessing `/` → redirect to `/login`
    - Authenticated user accessing `/` → allow
    - Authenticated user accessing `/login` → redirect to `/`
    - `/login` always accessible when unauthenticated

  **Commit**: YES (group with T8)

---

### Wave 3

- [x] 11. BackendSwitcher Component

  **What to do**:
  - Create `frontend/src/components/BackendSwitcher.vue`
  - Naive UI `NPopselect` or `NDropdown` with list of saved backends
  - Shows current backend name/URL as trigger button
  - Dropdown items: each saved backend (show baseUrl), click to switch
  - "Add new" option at bottom → navigates to /login (or opens inline form)
  - "Remove" action per backend (via right-click or icon)
  - Component reads from `authStore.backendOptions` and calls `authStore.switchBackend()`

  **Must NOT do**:
  - Do not duplicate backend storage logic — use auth store

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: UI component with Naive UI dropdown
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on T1, T8)
  - **Parallel Group**: Wave 3 (with T12, T13)
  - **Blocks**: T12, T13
  - **Blocked By**: T1, T8

  **References**:
  - `frontend/src/stores/auth.store.ts` — `backendOptions` getter, `switchBackend()` action
  - Naive UI docs: `NDropdown` / `NPopselect` component

  **Acceptance Criteria**:
  - [ ] Dropdown shows all saved backends
  - [ ] Clicking a backend switches `currentBackendIndex`
  - [ ] Current backend highlighted
  - [ ] "Add new" option exists

  **QA Scenarios**:

  ```
  Scenario: Switch backend via dropdown
    Tool: vitest
    Preconditions: Auth store with 2 backends saved
    Steps:
      1. Mount BackendSwitcher
      2. Click dropdown trigger
      3. Assert 2 backend options visible
      4. Click second option
      5. Assert authStore.currentBackendIndex === 1
    Expected Result: Backend switched
    Evidence: .sisyphus/evidence/task-10-switch.txt
  ```

  **Commit**: YES
  - Message: `feat(auth): add backend switcher to top bar`
  - Files: `frontend/src/components/BackendSwitcher.vue`

---

- [x] 12. Update App.vue

  **What to do**:
  - Modify `frontend/src/App.vue`
  - Remove boilerplate (Vue logo, HelloWorld, nav)
  - Add `BackendSwitcher` to header (only show when authenticated)
  - Clean up styles — minimal header with switcher
  - Keep `RouterView`

  **Commit**: YES
  - Message: `feat(auth): integrate backend switcher into app layout`
  - Files: `frontend/src/App.vue`

---

- [x] 13. BackendSwitcher Tests (TDD)

  **What to do**:
  - Create `frontend/src/components/__tests__/BackendSwitcher.test.ts`
  - Tests: renders backends, switches on click, shows current, add new option

  **Commit**: YES (group with T10)

---

- [x] 14. E2E Playwright QA

  **What to do**:
  - Full login flow: navigate to /login, fill form, submit, verify redirect
  - Backend switching: add multiple backends, switch between them
  - Auth guard: clear auth, navigate to protected route, verify redirect to /login
  - Save screenshots and evidence

  **Blocked By**: T4, T12

  **Commit**: NO (QA only)

---

## Final Verification Wave

- [x] F1. **Plan Compliance Audit** — `oracle`
  Verify: login page renders, multi-backend works, route guard active, API client dynamic, tests pass. Compare deliverables against plan.

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run vitest + lint. Check for `as any`, console.log, unused imports, AI slop.

- [x] F3. **Real Manual QA** — `unspecified-high` + `playwright`
  Execute all QA scenarios with Playwright. Full login flow, backend switching, edge cases.

- [x] F4. **Scope Fidelity Check** — `deep`
  Verify only planned files modified. No dashboard created. No backend changes.

---

## Commit Strategy

- **Wave 1**: `feat(auth): add auth store + login/home views + MSW mocks + tests`
- **Wave 2**: `feat(auth): dynamic API client + router guard + tests`
- **Wave 3**: `feat(auth): backend switcher component + app integration + tests`

---

## Success Criteria

### Verification Commands
```bash
cd frontend && npm run test:unit  # All vitest tests pass
cd frontend && npm run lint       # No lint errors
cd frontend && npm run build      # Build succeeds
```

### Final Checklist
- [ ] Login page renders with 70/30 layout
- [ ] Auth check via /api/v1/protected works
- [ ] Multi-backend credentials persist in localStorage
- [ ] Backend switcher in top bar works
- [ ] API client baseURL switches dynamically
- [ ] Route guard redirects to /login
- [ ] All vitest tests pass
- [ ] No backend code modified
