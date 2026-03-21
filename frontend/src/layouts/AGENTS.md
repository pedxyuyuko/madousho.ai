# Layouts Knowledge Base

## OVERVIEW

`AdminLayout.vue` is the authenticated shell boundary: navigation, header controls, logout flow, and shell-specific theme styling all converge here.

## WHERE TO LOOK

| Task | File | Notes |
|------|------|-------|
| Shell structure | `AdminLayout.vue` | Sidebar, header, router outlet |
| Layout tests | `__tests__/AdminLayout.test.ts` | Stable structure and ordering contract |

## CONVENTIONS

- Header action order is fixed: `ThemeSwitcher` → `LanguageSwitcher` → `BackendSwitcher` → logout button.
- Required test ids: `admin-layout`, `admin-sidebar`, `admin-header`, `sidebar-toggle`, `logout-btn`.
- Sidebar contract: 240px expanded, 64px collapsed, icon-only brand when collapsed.
- Menu items are localized through `t('admin.sidebar.*')` and routed by route name.
- Shell theming is expressed here with explicit `[data-theme='starry-night'|'parchment'] .admin-*` selectors.

## TEST-ENFORCED CONTRACTS

- Layout must render the Naive shell structure and router outlet.
- Dashboard and Flows labels must remain localized.
- Sidebar toggle must collapse and expand predictably.
- Logout must call `authStore.logout()` before redirecting to login.

## ANTI-PATTERNS

- **DO NOT** reorder header controls casually; unit and E2E tests assert their order.
- **DO NOT** remove or rename the stable `data-testid` hooks without updating tests deliberately.
- **DO NOT** move shell theming entirely into generic theme files; layout-specific shell CSS lives here on purpose.
- **DO NOT** hardcode labels outside i18n.

## RELATED

- Parent: `../../AGENTS.md`
- Coupled with: `../components/*`, `../stores/auth.store.ts`, `../theme/*`, `../../tests/e2e/admin-layout.spec.ts`
