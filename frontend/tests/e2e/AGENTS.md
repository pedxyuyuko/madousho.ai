# E2E Knowledge Base

## OVERVIEW

Playwright specs here test integrated shell behavior using seeded localStorage state and a dedicated mocked dev server.

## WHERE TO LOOK

| Task | File | Notes |
|------|------|-------|
| Shell integration | `admin-layout.spec.ts` | Header order, theme switch, logout redirect |
| Flows integration | `flows.spec.ts` | Route-level success/empty/error states |
| Home smoke path | `home.spec.ts` | Landing behavior |
| Runner config | `../../playwright.config.ts` | `:5174`, Chromium, `VITE_USE_MOCKS=true` |

## CONVENTIONS

- Seed `madousho_backends` and `madousho_theme` with `page.addInitScript()` before navigation.
- Prefer exercising real UI against mocked network, not bypassing the page with component-level assumptions.
- Route-level overrides with `page.route()` are acceptable for scenario-specific API responses.
- Keep expectations aligned with stable test ids and visible localized text.

## TEST STRATEGY

- `admin-layout.spec.ts` verifies shell composition and auth-adjacent UX without using the login form.
- `flows.spec.ts` overrides `/api/v1/flows` per scenario instead of rewriting global mocks.
- Seeded auth exists because local environments may disable MSW outside the Playwright server path.

## ANTI-PATTERNS

- **DO NOT** depend on manual login flow for routine layout coverage.
- **DO NOT** assume local env mocks are enabled outside Playwright’s configured server.
- **DO NOT** change seeded storage keys or layout test ids without updating the suite together.
- **DO NOT** couple assertions to incidental DOM noise when stable text or test ids exist.

## RELATED

- Parent: `../../AGENTS.md`
- Coupled with: `../../src/layouts/AdminLayout.vue`, `../../src/stores/*.store.ts`, `../../src/mocks/handlers.ts`
