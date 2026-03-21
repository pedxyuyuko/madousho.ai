
## Task 1: Flows Types, MSW Handler, i18n (2026-03-19)

### Created Files
- `frontend/src/types/flow.ts` - Flow and FlowListResponse interfaces matching backend schema
- `frontend/src/mocks/__tests__/flows-handler.test.ts` - MSW handler integration test

### Modified Files
- `frontend/src/mocks/handlers.ts` - Added GET */api/v1/flows handler with typed mock data
- `frontend/src/locales/zh-CN/admin.json` - Added flows namespace with 7 keys
- `frontend/src/locales/en-US/admin.json` - Added flows namespace (placeholder empty strings)

### Patterns
- Types use `interface` not `type` (matches existing `menu.ts` convention)
- MSW handlers use `*/api/v1/*` glob pattern for proxy compatibility
- Mock data uses Chinese names matching zh-CN locale
- Status union type `'created' | 'processing' | 'finished'` matches FlowStatus enum
- Tests use `setupServer` from `msw/node` for handler testing

### Verification
- `npm run type-check` passes
- `npx vitest run src/mocks/__tests__/flows-handler.test.ts` passes (4/4 tests)

## Route Registration & Menu Fix (2026-03-19)
- When adding `useRoute()` to a component, tests that mock `vue-router` must also mock `useRoute` returning an object with at least `name` property
- Menu key must match route name for `:value="route.name"` to highlight correctly
- Changing i18n key from `admin.sidebar.dashboard` to `admin.sidebar.home` is safe as long as the label text ("仪表盘") remains unchanged

## Task 3: FlowsView Component (2026-03-19)

### Created Files
- `frontend/src/views/FlowsView.vue` - Flow list view with loading/empty/error/data states
- `frontend/src/views/__tests__/FlowsView.test.ts` - 10 unit tests

### Patterns
- Vue SFC `<script setup lang="ts">` with `ref` + `onMounted` (matches HomeView pattern)
- `apiClient.get<FlowListResponse>('/flows')` - generic type param for response
- Status color mapping via `Record<Flow['status'], 'success' | 'warning' | 'default'>`
- Null coalescing for description: `flow.description ?? '—'`
- Tests mock `@/api/client` module, not axios directly
- Naive UI stubs use `data-testid` attributes for reliable selection
- Error catch sets `error.value = true` for 401/403/500 (interceptor handles 401 redirect separately)

### Verification
- `npm run type-check` passes
- `npm run lint` passes (0 warnings, 0 errors)
- `npx vitest run src/views/__tests__/FlowsView.test.ts` passes (10/10 tests)

## Task 4: E2E Tests (2026-03-19)

### Created Files
- `frontend/tests/e2e/flows.spec.ts` - 4 E2E tests for flows page

### Modified Files
- `frontend/playwright.config.ts` - Disabled MSW for E2E, use dedicated port 5174

### Patterns
- MSW vs Playwright: MSW service worker intercepts before `page.route()`. Must disable MSW with `VITE_USE_MOCKS=false` for `page.route()` to work
- E2E port isolation: Use port 5174 (not 5173) to avoid conflicts with running dev server
- Auth seeding: `page.addInitScript()` sets localStorage before page loads (same as admin-layout)
- MSW override: `page.route('**/api/v1/flows', ...)` intercepts API calls when MSW disabled
- Error state selector: Use `page.getByText('加载失败')` instead of CSS classes (Naive UI class names may vary)
- Happy path needs explicit mock data in `page.route()` when MSW disabled
- `reuseExistingServer: false` ensures clean E2E environment
- `VITE_USE_MOCKS=false` in webServer command overrides .env file

### Verification
- `npx playwright test tests/e2e/flows.spec.ts --reporter=line` passes (4/4 tests)
- `npx playwright test admin-layout.spec.ts --reporter=line` passes (5/5 tests)
