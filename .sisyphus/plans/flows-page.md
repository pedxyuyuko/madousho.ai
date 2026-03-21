# Implementation Plan: Flows View

## Objective
Create a new "Flows" view in AdminLayout showing a list of flows fetched from API. The view features a vertical list of full-width cards that expand to show details.

## Context & Guardrails
- **State**: `FlowsView` must manage its own data lifecycle via local `ref`s (no Pinia for this).
- **Layout Bug**: `AdminLayout.vue` currently has a hardcoded menu state (`value="dashboard"`). This must be fixed so the sidebar reacts to the current route.
- **Route/Menu Alignment**: The current route name is `home` while the sidebar menu key is `dashboard`; the implementation must align these so active highlighting works correctly. Prefer changing the menu key from `dashboard` to `home` instead of renaming the route, unless product wording explicitly requires otherwise.
- **API Contract** (verified from `src/madousho/api/schemas/flow.py`): The backend `GET /api/v1/flows` returns `FlowListResponse`:
  ```json
  {
    "items": [
      {
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Test Flow",
        "description": "Example flow for testing",
        "plugin": "example-plugin",
        "tasks": ["task-uuid-1", "task-uuid-2"],
        "status": "created",
        "flow_template": null,
        "created_at": "2026-03-19T10:00:00Z"
      }
    ],
    "total": 2,
    "offset": 0,
    "limit": 20
  }
  ```
  Valid `status` values: `created`, `processing`, `finished` (from `FlowStatus` enum).
- **Edge Cases**: Must handle loading (`NSpin`), empty (`NEmpty`), and error (`NResult` or equivalent warning state) states.
- **E2E Testing**: Add Playwright coverage seeding auth state to avoid login flow dependencies.

## Execution Waves

### Wave 1: Foundation (Parallel)

#### Task 1: API Types, Mocks, and i18n ✅
- **What**: 
  1. **CREATE NEW FILE** `frontend/src/types/flow.ts` (following existing `types/menu.ts` convention). Define TypeScript interfaces matching the backend Pydantic schemas:
     ```typescript
     export interface Flow {
       uuid: string
       name: string
       description: string | null
       plugin: string
       tasks: string[] | null
       status: 'created' | 'processing' | 'finished'
       flow_template: string | null
       created_at: string // ISO 8601 datetime
     }

     export interface FlowListResponse {
       items: Flow[]
       total: number
       offset: number
       limit: number
     }
     ```
  2. Add MSW handler in `frontend/src/mocks/handlers.ts` for `GET */api/v1/flows` returning a paginated mock response. Use realistic mock data:
     ```typescript
     const mockFlows: Flow[] = [
       {
         uuid: '550e8400-e29b-41d4-a716-446655440000',
         name: '文本分析流程',
         description: '用于测试的示例流程',
         plugin: 'text-analyzer',
         tasks: ['task-001', 'task-002'],
         status: 'created',
         flow_template: null,
         created_at: '2026-03-19T10:00:00Z'
       },
       {
         uuid: '660e8400-e29b-41d4-a716-446655440001',
         name: '图像处理流程',
         description: null,
         plugin: 'image-processor',
         tasks: [],
         status: 'processing',
         flow_template: 'default-template',
         created_at: '2026-03-19T11:00:00Z'
       }
     ]
     // Return: { items: mockFlows, total: mockFlows.length, offset: 0, limit: 20 }
     ```
  3. Add i18n keys to `src/locales/zh-CN/admin.json` under new `flows` namespace (sibling to existing `sidebar` and `header`):
     **Current file structure**:
     ```json
     {
       "sidebar": { "dashboard": "仪表盘", "flows": "工作流", "toggle": "切换菜单" },
       "header": { "logout": "退出", "title": "魔导书" }
     }
     ```
     **New structure after this task**:
     ```json
     {
       "sidebar": { "dashboard": "仪表盘", "flows": "工作流", "toggle": "切换菜单" },
       "header": { "logout": "退出", "title": "魔导书" },
       "flows": {
         "title": "工作流列表",
         "name": "名称",
         "uuid": "UUID",
         "description": "描述",
         "status": "状态",
         "empty": "暂无工作流",
         "error": "加载失败"
       }
     }
     ```
     **Note**: `admin.sidebar.flows` ("工作流") is the menu label, while `admin.flows.*` keys are for page content labels - these serve different purposes. Add matching placeholder keys to `src/locales/en-US/admin.json` (empty strings are acceptable for now).
- **QA Scenarios**:
  - **Scenario 1: Type-check passes**
    - **Tool**: Bash
    - **Steps**: Run `npm run type-check` in `frontend/` after adding the shared types and MSW handler.
    - **Expected**: TypeScript completes successfully with no errors related to `Flow`, `FlowListResponse`, or the new handler.
    - **Evidence**: `.sisyphus/evidence/task-1-typecheck.txt`
  - **Scenario 2: MSW mock returns correct shape**
    - **Tool**: Bash (vitest)
    - **Steps**: Create a test file `frontend/src/mocks/__tests__/flows-handler.test.ts`. Import the MSW handler, call it with a mock request, assert the response body has `items` (array with 2+ items), `total` (number), `offset` (0), `limit` (20). Verify each item has all required `Flow` fields.
    - **Expected**: Response shape matches `FlowListResponse` interface exactly.
    - **Evidence**: `.sisyphus/evidence/task-1-mock-shape.txt`
  - **Scenario 3: en-US placeholders exist**
    - **Tool**: Bash
    - **Steps**: Run `grep -A 10 '"flows"' frontend/src/locales/en-US/admin.json` and verify all keys from zh-CN exist (even if empty strings).
    - **Expected**: JSON structure matches zh-CN namespace with same key names.
    - **Evidence**: `.sisyphus/evidence/task-1-enus-placeholders.txt`
  - **Scenario 4: MSW handler registration verified**
    - **Tool**: Bash (vitest)
    - **Steps**: Run `npx vitest run frontend/src/mocks/__tests__/flows-handler.test.ts`. Test should verify the handler is registered and intercepts `GET */api/v1/flows` requests.
    - **Expected**: Test passes proving MSW handler is correctly registered and intercepts requests.
    - **Evidence**: `.sisyphus/evidence/task-1-msw-registered.txt`

#### Task 2: Router & Layout Fix ✅
- **What**: 
  1. Register `/flows` route in `frontend/src/router/index.ts` under the AdminLayout (`/`) children, lazily loading `FlowsView.vue`.
  2. Update `frontend/src/layouts/AdminLayout.vue` to derive the `<n-menu>` active value from `useRoute()`.
  3. **COMMIT to `home`**: Change the existing menu key from `dashboard` to `home`. Update `src/locales/zh-CN/admin.json` key from `sidebar.dashboard` to `sidebar.home` (keeping value "仪表盘"). Update `src/locales/en-US/admin.json` similarly.
  4. Update `frontend/src/layouts/__tests__/AdminLayout.test.ts` if menu selection assertions depend on the old hardcoded value.
- **QA Scenarios**:
  - **Scenario 1: Type-check passes**
    - **Tool**: Bash
    - **Steps**: Run `npm run type-check` in `frontend/` after the route and layout changes.
    - **Expected**: Vue type-check passes with the new `/flows` route and reactive menu binding.
    - **Evidence**: `.sisyphus/evidence/task-2-typecheck.txt`
  - **Scenario 2: Menu reacts to route changes**
    - **Tool**: Bash (vitest)
    - **Steps**: Run `npx vitest run src/layouts/__tests__/AdminLayout.test.ts`. Test should mount AdminLayout with a mock router, navigate to `/flows`, and assert the menu's active value equals the current route name.
    - **Expected**: Unit test passes proving menu selection updates when route changes.
    - **Evidence**: `.sisyphus/evidence/task-2-menu-reactive.txt`
  - **Scenario 3: Menu key changed to home**
    - **Tool**: Bash (grep)
    - **Steps**: Run `grep -n "key: 'home'" frontend/src/layouts/AdminLayout.vue` and verify no `key: 'dashboard'` exists. Also verify `grep "sidebar.home" frontend/src/locales/zh-CN/admin.json` returns the translation key.
    - **Expected**: Menu uses `key: 'home'` and i18n key is `sidebar.home`.
    - **Evidence**: `.sisyphus/evidence/task-2-menu-key.txt`

### Wave 2: UI Implementation

#### Task 3: FlowsView Component ✅
- **What**: 
  1. Create `frontend/src/views/FlowsView.vue`.
  2. Implement local state (`loading`, `error`, `flows` using `ref`).
  3. Fetch flows in `onMounted` using `apiClient.get('/flows')`, because the shared API client already prefixes relative URLs with `/api/v1`.
  4. Read flow data from `response.data.items`.
  5. Render loading (`NSpin`), empty (`NEmpty`), error (`NResult` or equivalent warning state), and data list.
  6. Use `NCard` for each flow (full width). Use `NTag` for status with the following color mapping (**NEW CONVENTION** - no existing pattern in codebase): `finished=success` (green), `processing=warning` (orange), `created=default` (gray/blue).
  7. Use `NCollapse` and `NCollapseItem` inside the card to expand and show the Description and UUID. Handle `description: null` gracefully by showing "—" (em dash).
  8. **Handle 401/403**: If API returns 401, the apiClient interceptor redirects to `/login` automatically. If API returns 403, the interceptor only logs error - component should show error state (user sees error message, stays on page).
- **QA Scenarios**:
  - **Scenario 1: Lint and type-check pass**
    - **Tool**: Bash
    - **Steps**: Run `npm run lint && npm run type-check` in `frontend/` after implementing `FlowsView.vue`.
    - **Expected**: Linting and type-check both pass; no Vue/TS diagnostics remain for `FlowsView.vue`.
    - **Evidence**: `.sisyphus/evidence/task-3-lint-typecheck.txt`
  - **Scenario 2: Loading state renders**
    - **Tool**: Bash (vitest)
    - **Steps**: Mount `FlowsView` with a mocked `apiClient` that delays 100ms. Assert `NSpin` is visible before data resolves.
    - **Expected**: `NSpin` component renders during the loading phase.
    - **Evidence**: `.sisyphus/evidence/task-3-loading-state.txt`
  - **Scenario 3: Empty state renders**
    - **Tool**: Bash (vitest)
    - **Steps**: Mount `FlowsView` with mocked `apiClient` returning `{ items: [], total: 0, offset: 0, limit: 20 }`. Assert `NEmpty` is visible.
    - **Expected**: `NEmpty` component renders when `items` array is empty.
    - **Evidence**: `.sisyphus/evidence/task-3-empty-state.txt`
  - **Scenario 4: Error state renders (500)**
    - **Tool**: Bash (vitest)
    - **Steps**: Mount `FlowsView` with mocked `apiClient` that rejects with 500 error. Assert `NResult` (or error message) is visible.
    - **Expected**: Error UI renders when API call fails with 500.
    - **Evidence**: `.sisyphus/evidence/task-3-error-state.txt`
  - **Scenario 5: Null description handled**
    - **Tool**: Bash (vitest)
    - **Steps**: Mount `FlowsView` with mock data where one flow has `description: null`. Expand that card and assert UI shows "—" instead of crashing or showing "null".
    - **Expected**: Card expands gracefully without errors, showing "—" for null description.
    - **Evidence**: `.sisyphus/evidence/task-3-null-description.txt`
  - **Scenario 6: 401 triggers redirect**
    - **Tool**: Bash (vitest)
    - **Steps**: Mount `FlowsView` with mocked `apiClient` that rejects with 401 and a mocked router. Assert router.push('/login') was called.
    - **Expected**: Component doesn't render error state; redirect to `/login` occurs instead.
    - **Evidence**: `.sisyphus/evidence/task-3-401-redirect.txt`
  - **Scenario 7: 403 shows error state (no redirect)**
    - **Tool**: Bash (vitest)
    - **Steps**: Mount `FlowsView` with mocked `apiClient` that rejects with 403. Assert error UI is visible and router.push was NOT called.
    - **Expected**: Component shows error state; user stays on page (403 does not trigger redirect).
    - **Evidence**: `.sisyphus/evidence/task-3-403-error.txt`
  - **Scenario 8: Status tag colors match convention**
    - **Tool**: Bash (vitest)
    - **Steps**: Mount `FlowsView` with mock flows having all three statuses (`created`, `processing`, `finished`). Assert each `NTag` has correct `type` prop (`default`, `warning`, `success` respectively).
    - **Expected**: Tags render with correct color mapping per the new convention.
    - **Evidence**: `.sisyphus/evidence/task-3-status-colors.txt`

### Wave 3: Testing

#### Task 4: E2E Playwright Tests ✅
- **What**: Add `frontend/tests/e2e/flows.spec.ts` (**CORRECTED PATH** - inside `frontend/` directory).
- **Details**: Reuse the auth-seeding pattern from `frontend/tests/e2e/admin-layout.spec.ts` via `page.addInitScript`. Navigate to `/flows`, verify the loading state appears, check that mock cards render, and verify that expanding a card reveals the UUID.
- **QA Scenarios**:
  - **Scenario 1: E2E happy path passes**
    - **Tool**: Bash
    - **Steps**: Run `npx playwright test frontend/tests/e2e/flows.spec.ts --reporter=line` in project root (or `cd frontend && npx playwright test tests/e2e/flows.spec.ts --reporter=line`).
    - **Expected**: The spec passes, proving navigation to `/flows`, successful list rendering from mocks, and expandable detail display.
    - **Evidence**: `.sisyphus/evidence/task-4-e2e-happy.txt`
  - **Scenario 2: E2E verifies empty state**
    - **Tool**: Bash
    - **Steps**: Add a test case that modifies MSW to return empty `items` array, navigate to `/flows`, assert `NEmpty` is visible.
    - **Expected**: Test passes proving empty state renders correctly in E2E.
    - **Evidence**: `.sisyphus/evidence/task-4-e2e-empty.txt`
  - **Scenario 3: E2E verifies error handling**
    - **Tool**: Bash
    - **Steps**: Add a test case that modifies MSW to return 500 error for `/api/v1/flows`, navigate to `/flows`, assert error UI (`NResult` or error message) is visible.
    - **Expected**: Test passes proving error state renders correctly in E2E.
    - **Evidence**: `.sisyphus/evidence/task-4-e2e-error.txt`

## Final Verification Wave
- **Tool**: Bash
- **Preparation**: Create `.sisyphus/evidence/final-verification-flows/` directory if not exists (`mkdir -p .sisyphus/evidence/final-verification-flows/`).
- **Steps**:
  1. Run `npm run type-check` in `frontend/` and capture output to `.sisyphus/evidence/final-verification-flows/typecheck.txt`. **Automated validation**: `grep -q "Found 0 errors" typecheck.txt || exit 1`.
  2. Run `npm run lint` in `frontend/` and capture output to `.sisyphus/evidence/final-verification-flows/lint.txt`. **Automated validation**: Check exit code is 0.
  3. Run `npx vitest run src/layouts/__tests__/AdminLayout.test.ts` in `frontend/` and capture output to `.sisyphus/evidence/final-verification-flows/vitest.txt`. **Automated validation**: `grep -q "Pass" vitest.txt || exit 1`.
  4. Run `npx playwright test tests/e2e/flows.spec.ts --reporter=line` in `frontend/` and capture output to `.sisyphus/evidence/final-verification-flows/playwright.txt`. **Automated validation**: `grep -q "passed" playwright.txt || exit 1`.
  5. **Add Playwright test for menu highlighting**: Verify `frontend/tests/e2e/flows.spec.ts` includes a test case that navigates to `/flows` and asserts the sidebar menu highlights the "flows" item (matching route name).
- **Expected**: All commands pass; `/flows` is routable, sidebar highlighting follows the active route, and the flows page shows loading, empty/error-safe handling, and expandable cards sourced from the mock API.
- **Evidence**: `.sisyphus/evidence/final-verification-flows/` (directory containing all 4 output files above). **Note**: Individual task evidence files (e.g., `.sisyphus/evidence/task-1-*.txt`) are cumulative and should be preserved for detailed debugging; final verification captures aggregate pass/fail status.
- **Automated Validation Script**: Create `.sisyphus/evidence/final-verification-flows/validate.sh` that runs all grep checks above and exits with code 0 only if all validations pass.
