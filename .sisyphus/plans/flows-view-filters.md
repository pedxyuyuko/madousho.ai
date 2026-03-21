# Flows View Filters & Sorting

## TL;DR
> **Summary**: Add a visible filter/sort toolbar directly under the Flows page title in `frontend/src/views/FlowsView.vue`, using real `/flows` API requests for keyword/status filtering and frontend-local sorting for created-at order.
> **Deliverables**:
> - Visible toolbar with keyword, status, sort, and reset controls
> - Deterministic local filtering/sorting pipeline over fetched flows
> - Updated locale copy for toolbar and filtered-empty messaging
> - Updated Vitest and Playwright coverage for toolbar behavior and edge cases
> **Effort**: Short
> **Parallel**: YES - 2 waves
> **Critical Path**: Task 1 → Task 2 → Final Verification

## Context
### Original Request
在 `frontend/src/views/FlowsView.vue` 页面标题下新增排序/筛选功能，支持关键字查询、时间范围、状态排序&筛选、插件筛选，并优先选择合适的 Naive UI 组件。

### Interview Summary
- Keyword search scope is **name + description only**.
- Status interaction is **filter-only**; sorting is **created_at only**.
- Final data source must **directly use the real API** via shared `apiClient`.
- Implementation should stay local to `FlowsView.vue`; no store extraction.
- Plugin filter is removed from scope.
- Date-range filter is removed from scope.

### Metis Review (gaps addressed)
- Fixed all ambiguous behaviors up front: default sort, inclusive date boundaries, deterministic tie-break, plugin option generation, reset semantics, and filtered-empty state.
- Explicitly forbids scope creep into URL sync, Pinia persistence, extra endpoints, server-side query params, and generic shared filter components.
- Requires stale Flows tests to be rewritten to match current card-based implementation before asserting new toolbar behavior.

## Work Objectives
### Core Objective
Implement a decision-complete filter/sort experience for the Flows page that uses backend query params for keyword/status filtering and frontend-local created-at sorting inside `FlowsView.vue` using visible Naive UI controls.

### Deliverables
- `frontend/src/views/FlowsView.vue` gains a visible toolbar directly under `.flows-title`
- Toolbar uses `NForm` + `NSpace` + `NInput` + `NSelect` + reset button
- New derived rendered result set applies frontend-local sorting to backend-filtered `/flows` responses
- `frontend/src/locales/zh-CN/admin.json` gets minimal new `admin.flows.*` strings required by the feature
- `frontend/src/views/__tests__/FlowsView.test.ts` updated for local logic and current markup
- `frontend/tests/e2e/flows.spec.ts` updated for real toolbar interactions with seeded auth and `page.route()` overrides

### Definition of Done (verifiable conditions with commands)
- `npm run lint` succeeds in `frontend/`
- `npm run type-check` succeeds in `frontend/`
- `npm run test:unit -- FlowsView` or equivalent targeted Vitest run for `src/views/__tests__/FlowsView.test.ts` succeeds
- `npx playwright test tests/e2e/flows.spec.ts --reporter=line` succeeds in `frontend/`
- The page fetches `apiClient.get('/flows')` using backend-supported query params for `name` and `status`, then applies user-selected created-at sort locally on the fetched results
- Filtered-empty, fetch-empty, and fetch-error are distinguishable in UI and tests

### Must Have
- Toolbar remains always visible directly below the title
- Keyword search uses backend `name` query param and matches the backend fuzzy-search contract
- Status filter uses backend `status` query param with raw status values: `created`, `processing`, `finished`
- Sort control remains in scope and is implemented only against already-fetched results
- Default visible order is backend `created_at desc`, represented in the UI as local sort value `desc`
- Reset button clears keyword and status and restores default sort state in one click
- Existing card expand/collapse behavior continues working after filtered/sorted rendering

### Must NOT Have (guardrails, AI slop patterns, scope boundaries)
- Must NOT add query-string sync, localStorage persistence, or Pinia state for filters
- Must NOT add new API endpoints, query params, pagination, or server-side filtering/sorting in this work
- Must NOT broaden keyword search to `uuid`, `plugin`, `tasks`, `flow_template`, or translated labels
- Must NOT turn status into a sort dimension
- Must NOT hide primary controls inside dropdowns/popovers/drawers
- Must NOT introduce plugin filtering or date-range filtering in this work
- Must NOT mutate `flows.value` in place while sorting if alternate client-side sort is kept
- Must NOT refactor unrelated route/layout logic or genericize this into a reusable shared toolbar component

## Verification Strategy
> ZERO HUMAN INTERVENTION — all verification is agent-executed.
- Test decision: tests-after with existing Vitest + Playwright stack
- QA policy: Every implementation task includes agent-executed happy-path and edge/failure scenarios
- Evidence: `.sisyphus/evidence/task-{N}-{slug}.{ext}`

## Execution Strategy
### Parallel Execution Waves
> Target: 5-8 tasks per wave. <3 per wave (except final) = under-splitting.
> Extract shared dependencies as Wave-1 tasks for max parallelism.

Wave 1: test/spec definition, locale/control contract definition

Wave 2: `FlowsView.vue` implementation and test alignment

### Dependency Matrix (full, all tasks)
- Task 1 blocks Task 2
- Task 2 blocks Final Verification Wave

### Agent Dispatch Summary (wave → task count → categories)
- Wave 1 → 1 task → `unspecified-high`
- Wave 2 → 1 task → `visual-engineering`
- Final Verification → 4 tasks → `oracle`, `unspecified-high`, `unspecified-high`, `deep`

## TODOs
> Implementation + Test = ONE task. Never separate.
> EVERY task MUST have: Agent Profile + Parallelization + QA Scenarios.

- [ ] 1. Define filter contract and rewrite stale Flows tests

  **What to do**:
  - Update `frontend/src/views/__tests__/FlowsView.test.ts` so it matches the current card-based `FlowsView.vue` implementation instead of stale collapse assumptions.
  - Add deterministic fixture data covering the remaining dimensions with intentionally distinct `name`, `description`, `status`, and `created_at` combinations.
  - Define unit-test expectations for the exact local behavior contract:
    - default sort = newest first by `created_at` using frontend-local ordering over fetched results
    - tie-break for identical `created_at` = `uuid` ascending
    - keyword = trimmed, case-insensitive substring match on `name` + `description ?? ''`
    - status = single-select exact equality on raw status value
    - combined behavior = keyword + status together
    - reset = restore default state and full result list
    - filtered-empty = distinct behavior from fetch-empty and fetch-error
    - expansion behavior preserved for still-visible cards after filtering/sorting
  - Update `frontend/tests/e2e/flows.spec.ts` to define realistic browser-level expectations for keyword/status/sort toolbar interaction using seeded auth and `page.route()`.
  - Add stable selectors or `data-testid` expectations in tests for the remaining toolbar controls so implementation has a precise contract to satisfy.

  **Must NOT do**:
  - Must NOT introduce new endpoints, query params, or route-state persistence in tests
  - Must NOT keep stale `n-collapse` assertions after replacement coverage exists
  - Must NOT depend on Naive UI internal class names when a stable selector/test id can be introduced

  **Recommended Agent Profile**:
  - Category: `unspecified-high` — Reason: Multi-file test contract definition with strict behavior coverage and stale-test cleanup
  - Skills: `[]` — No additional skill required
  - Omitted: `[pua]` — Not needed unless execution stalls repeatedly

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: [2] | Blocked By: []

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `frontend/src/views/FlowsView.vue:1-39` — current local state shape and single mount-time `/flows` fetch
  - Pattern: `frontend/src/views/FlowsView.vue:42-115` — current title, loading/error/empty/data-state structure, card rendering, and expand/collapse behavior
  - API/Type: `frontend/src/types/flow.ts:1-17` — exact `Flow` and `FlowListResponse` contract
  - API/Type: `frontend/src/api/client.ts:18-57` — request normalization to `/api/v1`, auth header behavior, and 401/403/500 handling
  - Test: `frontend/src/views/__tests__/FlowsView.test.ts:1-230` — current stale baseline that must be modernized
  - Test: `frontend/tests/e2e/flows.spec.ts:1-120` — seeded-auth Playwright pattern and per-scenario `page.route()` override pattern
  - Locale: `frontend/src/locales/zh-CN/admin.json:1-20` — existing `admin.flows` namespace to extend minimally
  - External: `https://github.com/tusen-ai/naive-ui/blob/dbb66f5ca4cc46795fcc5bfa80113a8cb286b890/src/input/demos/enUS/clearable.demo.vue#L1-L20` — `NInput` clearable usage
  - External: `https://github.com/tusen-ai/naive-ui/blob/dbb66f5ca4cc46795fcc5bfa80113a8cb286b890/src/select/demos/enUS/clearable.demo.vue#L64-L80` — `NSelect` clearable behavior
  - External: `https://github.com/tusen-ai/naive-ui/blob/dbb66f5ca4cc46795fcc5bfa80113a8cb286b890/src/form/demos/enUS/inline.demo.vue#L70-L84` — inline `NForm` toolbar pattern
  - External: `https://github.com/tusen-ai/naive-ui/blob/dbb66f5ca4cc46795fcc5bfa80113a8cb286b890/src/space/demos/enUS/basic.demo.vue#L1-L9` — `NSpace` wrapping/alignment pattern

  **Acceptance Criteria** (agent-executable only):
  - [ ] `frontend/src/views/__tests__/FlowsView.test.ts` contains assertions for default sort, keyword, status, combined behavior, reset, and filtered-empty behavior
  - [ ] `frontend/src/views/__tests__/FlowsView.test.ts` no longer asserts `n-collapse`-based behavior that does not exist in current `FlowsView.vue`
  - [ ] `frontend/tests/e2e/flows.spec.ts` includes realistic user-flow assertions for toolbar controls with seeded auth and `page.route()` response control only
  - [ ] New test selectors/contracts identify each toolbar control unambiguously without relying on brittle internal DOM details

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: Unit test contract defines full local filtering behavior
    Tool: Bash
    Steps: Run `npx vitest run src/views/__tests__/FlowsView.test.ts` in `frontend/` after rewriting the spec. Confirm the spec file now contains cases for keyword, status, sort, reset, combined behavior, filtered-empty, and stale-markup replacement.
    Expected: The file and targeted run clearly encode the full behavior contract for implementation; if run before implementation completion, failures must correspond to the new contract rather than stale assumptions.
    Evidence: .sisyphus/evidence/task-1-flows-test-contract.txt

  Scenario: Playwright contract defines realistic toolbar interactions
    Tool: Bash
    Steps: Run `npx playwright test tests/e2e/flows.spec.ts --reporter=line` in `frontend/` after updating the spec to cover seeded-auth navigation plus keyword, status, sort, reset, and filtered-empty interactions.
    Expected: The spec encodes browser-level expectations using seeded localStorage auth and `page.route()` only; any failures point to missing implementation rather than ambiguous test design.
    Evidence: .sisyphus/evidence/task-1-flows-e2e-contract.txt
  ```

  **Commit**: YES | Message: `test(flows): define filter and sort expectations` | Files: [`frontend/src/views/__tests__/FlowsView.test.ts`, `frontend/tests/e2e/flows.spec.ts`]

- [ ] 2. Implement visible local filter/sort toolbar in FlowsView

  **What to do**:
  - Update `frontend/src/views/FlowsView.vue` to import `computed` in addition to existing Vue imports.
  - Keep `flows` as the raw fetched list from `apiClient.get<FlowListResponse>('/flows')` and do not change the mount-time fetch behavior.
  - Add local toolbar state in the same component with these exact defaults:
    - `keyword = ''`
    - `selectedStatus = null`
    - `createdAtSort = 'desc'`
  - Insert a visible toolbar directly under the `h2.flows-title`, before loading/error/empty/data state branches.
  - Use these exact controls and behaviors:
    - `NForm` wrapper, inline layout first
    - `NSpace` for wrapping/alignment
    - keyword `NInput` with `clearable`
    - status `NSelect` single-select with `clearable`
    - sort `NSelect` with exactly two values: `desc` and `asc`
    - explicit reset button that restores all defaults in one action
  - Add minimal locale-backed labels/placeholders/options/messages under `admin.flows.*`; do not hardcode visible strings.
  - Fetch logic must use backend-supported query params for `name` and `status` whenever those controls are set.
  - Create a single derived `computed` result pipeline with this exact order:
    1. start from fetched `flows.value`
    2. create a copied array
    3. sort by parsed `created_at` using `createdAtSort`
    4. if parsed timestamps tie, sort by `uuid.localeCompare()` ascending
    5. invalid/unparseable dates sort after valid dates for both directions, then by `uuid`
  - Empty-state behavior is fixed and must not be improvised:
    - fetch-empty (`flows.length === 0`) keeps existing empty-state behavior/message
    - filtered-empty (`flows.length > 0` but current query result is empty) shows a distinct localized empty-result message
    - fetch-error keeps existing error state
  - Expansion-state behavior is fixed and must not be improvised:
    - preserve `expandedFlows` membership for flows that remain visible after filtering/sorting
    - do not auto-expand anything
    - if a flow disappears due to filtering, it simply does not render; if it returns later and its UUID is still in the set, it reappears expanded
  - Add stable selectors or `data-testid` hooks for each toolbar control and filtered-empty state to support Playwright/Vitest.
  - Update component tests and E2E tests until they match the final implementation exactly.

  **Must NOT do**:
  - Must NOT add route query sync, localStorage persistence, or Pinia for filter state
  - Must NOT add debounce, highlighted matches, saved filters, or badge counts
  - Must NOT broaden keyword scope beyond `name` + `description`
  - Must NOT introduce plugin filtering or date-range filtering
  - Must NOT add unsupported backend sort params
  - Must NOT refactor card structure beyond what is required to insert the toolbar and stable selectors

  **Recommended Agent Profile**:
  - Category: `visual-engineering` — Reason: Vue/Naive UI implementation with UX-sensitive toolbar layout and selector stability
  - Skills: `[]` — No additional skill required
  - Omitted: `[pua]` — Not needed unless execution stalls repeatedly

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: [Final Verification] | Blocked By: [1]

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `frontend/src/views/FlowsView.vue:1-39` — current single-fetch local-state setup to preserve
  - Pattern: `frontend/src/views/FlowsView.vue:42-115` — exact current title placement and state branch structure; toolbar must be inserted under title, before these branches
  - Pattern: `frontend/src/views/FlowsView.vue:117-252` — existing scoped styling and card classes to preserve
  - API/Type: `frontend/src/types/flow.ts:1-17` — fields available for local filtering/sorting
  - API/Type: `frontend/src/api/client.ts:18-57` — shared real-API usage contract; continue calling `apiClient.get('/flows')`
  - Test: `frontend/src/views/__tests__/FlowsView.test.ts:1-230` — unit-test baseline that must be updated in lockstep
  - Test: `frontend/tests/e2e/flows.spec.ts:1-120` — seeded-auth and route-override E2E pattern to preserve
  - Locale: `frontend/src/locales/zh-CN/admin.json:1-20` — existing `admin.flows` namespace to extend minimally
  - External: `https://github.com/tusen-ai/naive-ui/blob/dbb66f5ca4cc46795fcc5bfa80113a8cb286b890/src/form/demos/enUS/inline.demo.vue#L70-L84` — inline `NForm` toolbar guidance
  - External: `https://github.com/tusen-ai/naive-ui/blob/dbb66f5ca4cc46795fcc5bfa80113a8cb286b890/src/space/demos/enUS/basic.demo.vue#L1-L9` — `NSpace` wrapping/alignment guidance
  - External: `https://github.com/tusen-ai/naive-ui/blob/dbb66f5ca4cc46795fcc5bfa80113a8cb286b890/src/input/demos/enUS/clearable.demo.vue#L1-L20` — clearable keyword input pattern
  - External: `https://github.com/tusen-ai/naive-ui/blob/dbb66f5ca4cc46795fcc5bfa80113a8cb286b890/src/select/demos/enUS/clearable.demo.vue#L64-L80` — clearable status/plugin selects

  **Acceptance Criteria** (agent-executable only):
  - [ ] `frontend/src/views/FlowsView.vue` renders a visible localized toolbar under `.flows-title` with exactly four controls: keyword, status, sort, reset
  - [ ] The component uses backend query params for keyword/status changes and does not introduce unsupported plugin/date/sort params
  - [ ] Keyword and status behavior match the backend-supported request contract, while sort/reset match the fixed UI rules above
  - [ ] Filtered-empty, fetch-empty, and fetch-error each produce the correct distinct UI state/message
  - [ ] Stable selectors/test ids exist for toolbar controls and filtered-empty assertions
  - [ ] `frontend/src/views/__tests__/FlowsView.test.ts` and `frontend/tests/e2e/flows.spec.ts` both pass against the final implementation

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: User filters and sorts flows end-to-end
    Tool: Playwright
    Steps: Seed auth state via `page.addInitScript()`. Override `**/api/v1/flows` with responses that vary by incoming `name` and `status` query params. Visit `/flows`. Fill the keyword control with a term matching one flow, set status to `processing`, then switch sort between newest and oldest.
    Expected: Requests carry supported backend query params for keyword/status; rendered results follow the mocked backend response; sort changes only visible ordering of the fetched result set and never depends on unsupported backend sort params.
    Evidence: .sisyphus/evidence/task-2-flows-toolbar-playwright.txt

  Scenario: Reset and empty-state behavior remain correct
    Tool: Playwright
    Steps: Using mocked `/api/v1/flows` data with at least one flow present, apply keyword/status combinations that intentionally produce zero matches. Assert the filtered-empty message appears. Then click reset and confirm the full result set returns in default backend newest-first order. In separate scenarios, verify fetch-empty response still shows the original empty state and a 500 response still shows error state.
    Expected: Filtered-empty is distinct from fetch-empty and fetch-error; reset restores all defaults; default order matches backend `created_at desc`.
    Evidence: .sisyphus/evidence/task-2-flows-reset-empty.txt

  Scenario: Unit logic is deterministic across edge cases
    Tool: Bash
    Steps: Run `npx vitest run src/views/__tests__/FlowsView.test.ts` in `frontend/` with fixtures covering null descriptions, trimmed mixed-case keyword input, backend query-param generation for name/status, invalid dates, and identical created_at timestamps.
    Expected: Tests pass and prove the fixed logic: keyword input is normalized correctly, name/status query params are generated correctly, invalid dates sort after valid ones, and ascending/descending created-at sorting behaves deterministically.
    Evidence: .sisyphus/evidence/task-2-flows-vitest.txt
  ```

  **Commit**: YES | Message: `feat(flows): add flows query toolbar with local sorting` | Files: [`frontend/src/views/FlowsView.vue`, `frontend/src/locales/zh-CN/admin.json`, `frontend/src/views/__tests__/FlowsView.test.ts`, `frontend/tests/e2e/flows.spec.ts`]

## Final Verification Wave (MANDATORY — after ALL implementation tasks)
> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
> **Do NOT auto-proceed after verification. Wait for user's explicit approval before marking work complete.**
> **Never mark F1-F4 as checked before getting user's okay.** Rejection or user feedback -> fix -> re-run -> present again -> wait for okay.
- [ ] F1. Plan Compliance Audit — oracle
- [ ] F2. Code Quality Review — unspecified-high
- [ ] F3. Real Manual QA — unspecified-high (+ playwright if UI)
- [ ] F4. Scope Fidelity Check — deep

## Commit Strategy
- Commit 1: `test(flows): define filter and sort expectations`
- Commit 2: `feat(flows): add flows query toolbar with local sorting`
- Commit 3: `test(flows): stabilize selectors and edge cases`

## Success Criteria
- The toolbar is visible, localized, and stable under the title
- Filtering rules are deterministic and fully covered by unit/E2E tests
- Keyword/status filtering uses the existing real `/flows` API contract
- No new persistence, routing, or backend contract work is introduced
- Sort switching is frontend-local and never depends on unsupported backend sort params
