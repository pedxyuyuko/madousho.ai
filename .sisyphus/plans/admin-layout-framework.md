# Admin Layout Framework

## TL;DR

> **Quick Summary**: Rewrite AdminLayout.vue using Naive UI layout system (NLayout + NSider + NHeader + NContent) with collapsible sidebar, top header bar (Theme/Lang/Backend/Logout), and dual-theme support. Create LanguageSwitcher component and admin i18n locale.
>
> **Deliverables**:
> - Rewritten `AdminLayout.vue` with Naive UI layout components
> - New `LanguageSwitcher.vue` component (zh-CN/en-US toggle)
> - New `admin.json` locale file (zh-CN + empty en-US)
> - Updated `i18n.ts` to include admin locale
> - Vitest + Playwright tests for all components
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: Locale → i18n → LanguageSwitcher → AdminLayout → E2E

---

## Context

### Original Request
Build an admin layout framework with sidebar menu + top header bar for the Madousho.ai Vue 3 frontend. Sidebar should be collapsible (icon-only mode). Header has Theme switcher, Language switcher, Backend switcher, Logout button. Must adapt to 2 themes (starry-night dark / parchment light). TDD approach.

### Interview Summary
**Key Discussions**:
- Sidebar: Naive UI NSider, collapsible (240px → 64px), toggle button inside sidebar
- Menu items: Dashboard / Flows (placeholder, flat structure)
- Logo: text "魔导书" + subtitle when expanded, icon when collapsed
- Header button order: Theme | Lang | Backend | Logout
- Language switcher: Build UI first (zh-CN/en-US toggle), en-US empty for now
- Test strategy: TDD with Vitest (unit) + Playwright (E2E)

**Research Findings**:
- Both starry-night.ts and parchment.ts already have Menu component color overrides ready
- BackendSwitcher and ThemeSwitcher components already exist and work correctly
- Auth store has logout() which sets isAuthenticated=false, currentBackendIndex=-1
- Naive UI is globally registered — NLayout/NSider/NMenu/NHeader available directly
- themes.css defines CSS variables per `[data-theme]` attribute

### Metis Review
**Identified Gaps** (addressed):
- Sidebar state persistence: EXCLUDED — reset on reload
- Mobile responsive: EXCLUDED — desktop-only for now
- Menu item icons: EXCLUDED — text only for placeholders
- Sub-menus: EXCLUDED — flat structure only
- Keyboard shortcuts: EXCLUDED — basic implementation only
- Empty menu item behavior: Dashboard/Flows links are stubs — no routing

---

## Work Objectives

### Core Objective
Create a production-ready admin layout framework with collapsible sidebar and header status bar, fully adapted to both starry-night (dark) and parchment (light) themes.

### Concrete Deliverables
- `src/layouts/AdminLayout.vue` — Rewritten with Naive UI NLayout + NSider + NHeader + NContent
- `src/components/LanguageSwitcher.vue` — New component, dropdown with zh-CN / en-US
- `src/locales/zh-CN/admin.json` — Admin layout i18n strings
- `src/locales/en-US/admin.json` — Empty placeholder for future translations
- `src/i18n.ts` — Updated to import admin locale
- Tests: Vitest unit tests + Playwright E2E tests

### Definition of Done
- [ ] `cd frontend && npx vitest run` passes all tests
- [ ] `cd frontend && npx playwright test admin-layout.spec.ts` passes
- [ ] `cd frontend && npm run type-check` passes
- [ ] `cd frontend && npm run lint` passes
- [ ] Sidebar collapses/expands with smooth animation
- [ ] All header components render in correct order (Theme | Lang | Backend | Logout)
- [ ] Both themes apply correctly to sidebar and header

### Must Have
- Naive UI NLayout system (NLayout, NSider, NHeader, NContent)
- Sidebar collapsible (240px expanded, 64px collapsed)
- Menu items: Dashboard, Flows (placeholder)
- Logo: text when expanded, icon when collapsed
- Header: ThemeSwitcher, LanguageSwitcher, BackendSwitcher, Logout
- Dual-theme support via existing theme system
- TDD: unit tests + E2E tests

### Must NOT Have (Guardrails)
- No Dashboard/Flows view components or routes
- No sidebar state persistence (localStorage)
- No responsive/mobile layout handling
- No sub-menus or nested menu structure
- No menu item icons (text-only placeholders)
- No keyboard shortcuts for sidebar toggle
- No modifications to existing BackendSwitcher or ThemeSwitcher

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: YES (Vitest + Playwright)
- **Automated tests**: TDD
- **Framework**: Vitest (unit), Playwright (E2E)

### QA Policy
Every task includes agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Frontend/UI**: Use Playwright — Navigate, interact, assert DOM, screenshot
- **Component**: Use Vitest — Mount component, assert rendering and behavior

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — foundation):
├── Task 1: Create locale files + update i18n.ts
└── Task 2: Create TypeScript types for menu items

Wave 2 (After Wave 1 — components):
├── Task 3: LanguageSwitcher component + tests
└── Task 4: AdminLayout rewrite + tests

Wave 3 (After Wave 2 — integration verification):
└── Task 5: E2E tests for full admin layout flow

Wave FINAL (After ALL tasks — verification):
├── Task F1: Type-check + lint verification
├── Task F2: Visual QA with Playwright
└── Task F3: Theme adaptation verification
```

### Dependency Matrix
- **Task 1**: None → unblocks 3, 4
- **Task 2**: None → unblocks 4
- **Task 3**: 1 → part of Wave 2
- **Task 4**: 1, 2 → part of Wave 2
- **Task 5**: 3, 4 → Wave 3

### Agent Dispatch Summary
- **Wave 1** (2 tasks): T1 → `quick`, T2 → `quick`
- **Wave 2** (2 tasks): T3 → `visual-engineering`, T4 → `visual-engineering`
- **Wave 3** (1 task): T5 → `visual-engineering`
- **FINAL** (3 tasks): F1 → `quick`, F2 → `visual-engineering`, F3 → `visual-engineering`

---

## TODOs

- [x] 1. Create locale files and update i18n.ts

  **What to do**:
  - Create `src/locales/zh-CN/admin.json` with keys: `sidebar.dashboard`, `sidebar.flows`, `sidebar.toggle`, `header.logout`, `header.title`
  - Create `src/locales/en-US/admin.json` with empty placeholder values
  - Update `src/i18n.ts` to import and register `admin` namespace
  - Add `admin` to the messages object: `import admin from './locales/zh-CN/admin.json'`

  **Must NOT do**:
  - Do not modify existing locale files (common, login, home, backend, theme)
  - Do not add en-US locale directory creation logic

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple file creation and one-line import addition
  - **Skills**: []
    - No specialized skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: Task 3, Task 4
  - **Blocked By**: None

  **References**:
  **Pattern References**:
  - `src/i18n.ts:1-26` — Existing i18n setup with JSON imports
  - `src/locales/zh-CN/common.json:1-5` — Existing locale file structure (minimal JSON)

  **API/Type References**:
  - `src/i18n.ts:9-16` — Messages object structure showing how namespaces are merged

  **WHY Each Reference Matters**:
  - `src/i18n.ts` — Must follow exact import pattern and messages object structure
  - `src/locales/zh-CN/common.json` — Must match JSON key-value format for consistency

  **Acceptance Criteria**:
  - [ ] `src/locales/zh-CN/admin.json` exists with 5 keys
  - [ ] `src/locales/en-US/admin.json` exists with matching empty keys
  - [ ] `src/i18n.ts` imports `admin` and includes it in messages
  - [ ] `cd frontend && npx vitest run` still passes (no regressions)

  **QA Scenarios**:

  ```
  Scenario: i18n loads admin locale successfully
    Tool: Bash (vitest)
    Preconditions: None
    Steps:
      1. cd frontend && npx vitest run src/i18n.ts
      2. Verify test passes without import errors
    Expected Result: No errors, admin namespace available
    Failure Indicators: Module not found, undefined keys
    Evidence: .sisyphus/evidence/task-1-i18n-load.txt

  Scenario: admin.json has all required keys
    Tool: Bash (node)
    Preconditions: Files exist
    Steps:
      1. node -e "const d = require('./src/locales/zh-CN/admin.json'); console.log(Object.keys(d))"
      2. Verify keys include: sidebar, header
    Expected Result: sidebar and header objects present
    Failure Indicators: Missing keys, parse errors
    Evidence: .sisyphus/evidence/task-1-locale-keys.txt
  ```

  **Commit**: YES (with Task 2)
  - Message: `feat(i18n): add admin layout locale files`
  - Files: `src/locales/zh-CN/admin.json`, `src/locales/en-US/admin.json`, `src/i18n.ts`

---

- [x] 2. Create TypeScript types for menu items

  **What to do**:
  - Create `src/types/menu.ts` with `MenuItem` interface: `{ label: string, key: string, icon?: Component }`
  - Keep it simple — just the type definition, no runtime logic

  **Must NOT do**:
  - Do not create a store for menu state
  - Do not add menu configuration files

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single type definition file
  - **Skills**: []
    - No specialized skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Task 4
  - **Blocked By**: None

  **References**:
  **Pattern References**:
  — No existing type files to reference (this is a new pattern)
  — Follow TypeScript interface conventions from `src/stores/auth.store.ts:5-9` (Backend interface pattern)

  **WHY Each Reference Matters**:
  - `auth.store.ts:5-9` — Shows the project's TypeScript interface style (export interface, optional fields with `?`)

  **Acceptance Criteria**:
  - [ ] `src/types/menu.ts` exists
  - [ ] `MenuItem` interface exported with `label: string`, `key: string`, optional `icon`
  - [ ] `cd frontend && npx tsc --noEmit` passes

  **QA Scenarios**:

  ```
  Scenario: MenuItem type is valid TypeScript
    Tool: Bash (tsc)
    Preconditions: File exists
    Steps:
      1. cd frontend && npx tsc --noEmit
      2. Verify no errors related to menu.ts
    Expected Result: Zero type errors
    Failure Indicators: TS2xxx errors in menu.ts
    Evidence: .sisyphus/evidence/task-2-type-check.txt
  ```

  **Commit**: YES (with Task 1)
  - Message: `feat(types): add MenuItem interface`
  - Files: `src/types/menu.ts`

---

- [x] 3. LanguageSwitcher component with tests

  **What to do**:
  - Create `src/components/LanguageSwitcher.vue` — dropdown with zh-CN / en-US options
  - Uses Naive UI `NDropdown` (same pattern as BackendSwitcher)
  - Uses `useI18n()` to read/set locale
  - Current locale shows ✓ indicator
  - Add `data-testid="language-switcher"` for E2E testing
  - Create `src/components/__tests__/LanguageSwitcher.test.ts` with TDD:
    - Renders dropdown trigger
    - Shows zh-CN and en-US options
    - Changes locale on selection
    - Current locale is marked

  **Must NOT do**:
  - Do not add flag icons or country images
  - Do not persist language preference to localStorage
  - Do not add more than 2 language options

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: UI component with interactive dropdown behavior and theme adaptation
  - **Skills**: []
    - Standard Vue component development, no specialized skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 4)
  - **Blocks**: Task 5
  - **Blocked By**: Task 1

  **References**:
  **Pattern References**:
  - `src/components/BackendSwitcher.vue:1-85` — Component structure, dropdown usage, i18n integration, scoped styles
  - `src/components/ThemeSwitcher.vue:1-45` — Simple toggle component with i18n and theme store integration

  **API/Type References**:
  - `vue-i18n` `useI18n()` — `t()` for labels, `locale` ref for current locale
  - Naive UI `NDropdown` — `options` array, `trigger="click"`, `@select` handler

  **Test References**:
  - `src/components/__tests__/` — Follow existing test file naming and structure

  **WHY Each Reference Matters**:
  - `BackendSwitcher.vue` — Exact dropdown pattern to follow (NDropdown + computed options + handleSelect)
  - `ThemeSwitcher.vue` — i18n usage pattern and button styling conventions
  - Existing `__tests__/` — Test co-location convention

  **Acceptance Criteria**:
  - [ ] `src/components/LanguageSwitcher.vue` exists
  - [ ] Renders dropdown with zh-CN and en-US options
  - [ ] Current locale shows ✓ indicator
  - [ ] `data-testid="language-switcher"` attribute present
  - [ ] `src/components/__tests__/LanguageSwitcher.test.ts` exists
  - [ ] `cd frontend && npx vitest run src/components/__tests__/LanguageSwitcher.test.ts` passes

  **QA Scenarios**:

  ```
  Scenario: LanguageSwitcher renders and switches locale
    Tool: Vitest
    Preconditions: i18n configured with admin locale
    Steps:
      1. Mount LanguageSwitcher component
      2. Click dropdown trigger
      3. Verify dropdown shows "中文" and "English" options
      4. Click "English" option
      5. Verify i18n locale changes to 'en-US'
    Expected Result: Locale changes to en-US, dropdown updates
    Failure Indicators: Dropdown not rendering, locale not changing
    Evidence: .sisyphus/evidence/task-3-lang-switcher-unit.txt

  Scenario: LanguageSwitcher shows current locale indicator
    Tool: Vitest
    Preconditions: i18n locale = 'zh-CN'
    Steps:
      1. Mount LanguageSwitcher component
      2. Verify trigger shows "中文" label
      3. Open dropdown
      4. Verify "中文" option has ✓ indicator
    Expected Result: Current locale clearly marked
    Failure Indicators: No indicator, wrong label
    Evidence: .sisyphus/evidence/task-3-lang-indicator.txt
  ```

  **Commit**: YES
  - Message: `feat(components): add LanguageSwitcher with i18n integration`
  - Files: `src/components/LanguageSwitcher.vue`, `src/components/__tests__/LanguageSwitcher.test.ts`

---

- [x] 4. AdminLayout rewrite with Naive UI layout system

  **What to do**:
  - Rewrite `src/layouts/AdminLayout.vue` using Naive UI components:
    - `NLayout` as root container (full viewport)
    - `NSider` on the left: 240px expanded, 64px collapsed, `collapse-mode="width"`, `collapsed-width={64}`
    - `NMenu` inside sider: Dashboard + Flows items, `mode="vertical"`, `collapsed-width={64}` for icon mode
    - Sider header: Logo area — "魔导书" text + subtitle when expanded, icon when collapsed
    - Toggle button inside sidebar (using NSider's built-in collapsible feature or custom button)
    - `NLayout` > `NHeader`: Right-aligned flexbox with ThemeSwitcher, LanguageSwitcher, BackendSwitcher, Logout button (order: Theme | Lang | Backend | Logout)
    - `NLayout` > `NContent`: `<RouterView />`
  - Sidebar state managed with `ref<boolean>(false)` for collapsed
  - Menu items defined as computed array in script
  - Logout button calls `authStore.logout()` then `router.push('/login')`
  - Add `data-testid` attributes: `admin-layout`, `admin-sidebar`, `admin-header`, `sidebar-toggle`, `logout-btn`
  - Create `src/layouts/__tests__/AdminLayout.test.ts` with TDD:
    - Renders sidebar with correct initial width
    - Sidebar collapses/expands on toggle
    - Header contains all 4 components
    - Logo shows/hides based on collapsed state
    - Logout button calls auth store

  **Must NOT do**:
  - Do not create Dashboard/Flows view components
  - Do not add routes for Dashboard/Flows
  - Do not add sidebar state persistence
  - Do not add responsive/mobile handling
  - Do not modify existing BackendSwitcher or ThemeSwitcher components

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Complex layout component with Naive UI integration, theme adaptation, and multiple interactive elements
  - **Skills**: []
    - Standard Vue component development with Naive UI

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 3)
  - **Blocks**: Task 5
  - **Blocked By**: Task 1, Task 2

  **References**:
  **Pattern References**:
  - `src/layouts/AdminLayout.vue:1-41` — Current minimal layout to rewrite
  - `src/components/BackendSwitcher.vue:1-85` — Dropdown + i18n + auth store usage pattern
  - `src/components/ThemeSwitcher.vue:1-45` — Simple component with theme store integration
  - `src/App.vue:1-35` — Root component with NConfigProvider, theme binding, data-theme attribute

  **API/Type References**:
  - `src/types/menu.ts:MenuItem` — Menu item interface from Task 2
  - `src/stores/auth.store.ts:67-70` — `logout()` function signature
  - `src/stores/theme.store.ts:43-49` — `toggle()` function for theme switching
  - Naive UI `NLayout`, `NSider`, `NHeader`, `NContent`, `NMenu` — Layout component APIs

  **Test References**:
  - `src/components/__tests__/` — Test co-location convention and assertion patterns

  **External References**:
  - Naive UI Layout docs: `https://www.naiveui.com/en-US/os-theme/components/layout` — NSider collapse behavior, width props
  - Naive UI Menu docs: `https://www.naiveui.com/en-US/os-theme/components/menu` — Menu options format, collapsed-width

  **WHY Each Reference Matters**:
  - `AdminLayout.vue` — Understand what exists to rewrite it completely
  - `BackendSwitcher.vue` — Pattern for header component integration with auth store
  - `App.vue` — How NConfigProvider wraps everything, data-theme binding pattern
  - `auth.store.ts:67-70` — logout() implementation to call correctly
  - `theme.store.ts:43-49` — Theme toggle integration
  - `MenuItem` type — Menu options format for NMenu

  **Acceptance Criteria**:
  - [ ] `src/layouts/AdminLayout.vue` rewritten with Naive UI layout
  - [ ] Sidebar starts at 240px width
  - [ ] Sidebar collapses to 64px on toggle click
  - [ ] Menu items show "仪表盘" and "工作流" labels
  - [ ] Header contains ThemeSwitcher, LanguageSwitcher, BackendSwitcher, Logout in order
  - [ ] Logo shows "魔导书" text when expanded, icon when collapsed
  - [ ] Logout button redirects to /login
  - [ ] `data-testid` attributes on all interactive elements
  - [ ] `src/layouts/__tests__/AdminLayout.test.ts` exists
  - [ ] `cd frontend && npx vitest run src/layouts/__tests__/AdminLayout.test.ts` passes
  - [ ] `cd frontend && npm run type-check` passes

  **QA Scenarios**:

  ```
  Scenario: AdminLayout renders with sidebar and header
    Tool: Vitest
    Preconditions: Router, i18n, theme store configured
    Steps:
      1. Mount AdminLayout with router-view stub
      2. Assert NLayout, NSider, NHeader, NContent present
      3. Assert sidebar width is 240px
      4. Assert header contains 4 action components
    Expected Result: Full layout structure rendered
    Failure Indicators: Missing components, wrong structure
    Evidence: .sisyphus/evidence/task-4-layout-render.txt

  Scenario: Sidebar collapse and expand works
    Tool: Vitest
    Preconditions: AdminLayout mounted
    Steps:
      1. Find toggle button (data-testid="sidebar-toggle")
      2. Click toggle button
      3. Assert sidebar width changes to 64px
      4. Assert menu item text is hidden
      5. Assert logo text hidden, logo icon visible
      6. Click toggle again
      7. Assert sidebar expands back to 240px
    Expected Result: Smooth collapse/expand with correct UI changes
    Failure Indicators: Width not changing, content not hiding
    Evidence: .sisyphus/evidence/task-4-sidebar-toggle.txt

  Scenario: Logout button works correctly
    Tool: Vitest
    Preconditions: AdminLayout mounted, auth store with backends
    Steps:
      1. Click logout button (data-testid="logout-btn")
      2. Assert authStore.isAuthenticated becomes false
      3. Assert router navigates to /login
    Expected Result: Logout clears auth and redirects
    Failure Indicators: Auth state not cleared, no redirect
    Evidence: .sisyphus/evidence/task-4-logout.txt

  Scenario: Dual-theme adaptation
    Tool: Vitest
    Preconditions: AdminLayout mounted
    Steps:
      1. Toggle theme to parchment
      2. Assert sidebar background color changes
      3. Assert header background color changes
      4. Toggle theme to starry-night
      5. Assert colors revert to dark theme values
    Expected Result: Both themes apply correctly to layout
    Failure Indicators: Wrong colors, Naive UI overrides not applied
    Evidence: .sisyphus/evidence/task-4-theme-adapt.txt
  ```

  **Commit**: YES
  - Message: `feat(layout): rewrite AdminLayout with Naive UI layout system`
  - Files: `src/layouts/AdminLayout.vue`, `src/layouts/__tests__/AdminLayout.test.ts`

---

- [x] 5. E2E tests for admin layout integration

  **What to do**:
  - Create `tests/e2e/admin-layout.spec.ts` with Playwright tests:
    - Full sidebar expand/collapse flow
    - Theme switch while sidebar visible (both themes)
    - Language switch dropdown interaction
    - Logout button redirects to /login
    - All header components are clickable and in correct order
    - Menu items render correctly
  - Use existing Playwright config from `playwright.config.ts`

  **Must NOT do**:
  - Do not test actual Dashboard/Flows page content (they don't exist)
  - Do not test mobile responsive behavior

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: E2E testing of UI layout with Playwright browser automation
  - **Skills**: []
    - Standard Playwright testing

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (after Tasks 3 and 4)
  - **Blocks**: Final verification
  - **Blocked By**: Task 3, Task 4

  **References**:
  **Pattern References**:
  - `tests/e2e/` — Existing E2E test directory and conventions
  - `playwright.config.ts` — Playwright configuration

  **WHY Each Reference Matters**:
  - Existing E2E tests — Follow established patterns for Playwright test structure
  - Playwright config — Use correct base URL and browser settings

  **Acceptance Criteria**:
  - [ ] `tests/e2e/admin-layout.spec.ts` exists
  - [ ] `cd frontend && npx playwright test admin-layout.spec.ts` passes
  - [ ] All 6 test scenarios pass
  - [ ] Playwright report generated

  **QA Scenarios**:

  ```
  Scenario: Full sidebar expand/collapse flow
    Tool: Playwright
    Preconditions: Authenticated (MSW mock or test setup)
    Steps:
      1. Navigate to /
      2. Assert sidebar visible at 240px
      3. Click toggle button
      4. Assert sidebar collapsed to 64px
      5. Assert menu text hidden
      6. Click toggle again
      7. Assert sidebar expanded to 240px
    Expected Result: Smooth animation, correct widths
    Failure Indicators: Animation glitches, wrong widths
    Evidence: .sisyphus/evidence/task-5-sidebar-e2e.png

  Scenario: Theme switch preserves layout
    Tool: Playwright
    Preconditions: Authenticated
    Steps:
      1. Click ThemeSwitcher button
      2. Assert data-theme attribute changes
      3. Assert sidebar background color changes
      4. Assert header components still in correct order
      5. Switch back to original theme
      6. Assert colors revert
    Expected Result: Theme applies to all layout elements
    Failure Indicators: Partial theme application, layout breakage
    Evidence: .sisyphus/evidence/task-5-theme-e2e.png

  Scenario: Logout redirects to login
    Tool: Playwright
    Preconditions: Authenticated
    Steps:
      1. Click logout button (data-testid="logout-btn")
      2. Assert URL changes to /login
      3. Assert login form is visible
    Expected Result: Clean redirect to login page
    Failure Indicators: No redirect, error page
    Evidence: .sisyphus/evidence/task-5-logout-e2e.png
  ```

  **Commit**: NO (part of final verification)

---

## Final Verification Wave

- [x] F1. Type-check + lint verification — `quick`
  Run `cd frontend && npm run type-check` and `cd frontend && npm run lint`. Verify zero errors.
  Output: `Type-check [PASS/FAIL] | Lint [PASS/FAIL] | VERDICT`

- [x] F2. Visual QA with Playwright — `visual-engineering`
  Start dev server. Open browser to /. Verify: sidebar renders, header components visible, theme switch works, collapse/expand works, logout redirects. Take screenshots of expanded + collapsed + dark + light states. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Visual [PASS/FAIL] | Themes [2/2] | Interactions [N/N] | VERDICT`

- [x] F3. Theme adaptation verification — `visual-engineering`
  Verify both themes apply correctly: starry-night sidebar has purple accents, parchment sidebar has cream tones. Check Naive UI Menu overrides are active. Verify header components readable in both themes.
  Output: `starry-night [PASS/FAIL] | parchment [PASS/FAIL] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `feat(i18n): add admin layout locale files + MenuItem type` — locale files, i18n.ts, types/menu.ts, vitest
- **Wave 2**: `feat(components): add LanguageSwitcher + AdminLayout with tests` — LanguageSwitcher.vue, AdminLayout.vue, test files, vitest
- **Wave 3**: `test(e2e): add admin layout integration tests` — admin-layout.spec.ts, playwright

---

## Success Criteria

### Verification Commands
```bash
cd frontend && npm run type-check        # Expected: 0 errors
cd frontend && npm run lint               # Expected: 0 errors
cd frontend && npx vitest run             # Expected: all pass
cd frontend && npx playwright test admin-layout.spec.ts  # Expected: all pass
```

### Final Checklist
- [ ] AdminLayout uses Naive UI NLayout + NSider + NHeader + NContent
- [ ] Sidebar collapses from 240px to 64px
- [ ] Menu items: Dashboard, Flows
- [ ] Logo: text when expanded, icon when collapsed
- [ ] Header: Theme | Lang | Backend | Logout
- [ ] Both themes apply correctly
- [ ] All tests pass (unit + E2E)
- [ ] Type-check passes
- [ ] Lint passes
