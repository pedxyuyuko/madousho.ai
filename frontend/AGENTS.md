# Frontend Knowledge Base

**Generated:** 2026-03-20 20:51 EDT
**Commit:** a3795ac
**Branch:** frontend

## OVERVIEW

Vue 3 admin SPA embedded into the Python app, not a standalone frontend deployment. Vite builds directly into repo-root `../public`, auth is localStorage-backed with multi-backend switching, and UI verification relies on co-located Vitest plus seeded-state Playwright coverage.

## STRUCTURE

```text
frontend/
├── src/
│   ├── main.ts                # bootstrap: Pinia, Router, Naive UI, dev-only MSW
│   ├── App.vue                # root provider + theme binding
│   ├── i18n.ts                # zh-CN runtime messages only
│   ├── api/                   # shared axios client + tests
│   ├── components/            # header controls + unit tests
│   ├── layouts/               # authenticated shell boundary
│   ├── locales/               # zh-CN active, en-US placeholder-only
│   ├── mocks/                 # MSW handlers for dev and test
│   ├── router/                # auth guards + route wiring
│   ├── stores/                # auth/theme runtime contracts
│   ├── theme/                 # Naive UI theme overrides
│   └── views/                 # route pages + view tests
├── tests/e2e/                 # Playwright seeded-state integration tests
├── public/                    # source static assets, incl. mockServiceWorker.js
├── vite.config.ts             # proxy + i18n include + build-to-../public
├── vitest.config.ts           # jsdom, excludes e2e
├── playwright.config.ts       # dev server on :5174 with mocks forced on
└── eslint.config.ts           # Vue/TS rules + Vitest scope + Oxlint
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| App bootstrap | `src/main.ts` | Starts MSW only in dev |
| Shared API behavior | `src/api/client.ts` | Base URL normalization, Bearer token, 401 logout |
| Auth routing | `src/router/index.ts` | Redirects `/login` vs protected routes |
| Auth persistence | `src/stores/auth.store.ts` | `madousho_backends` contract |
| Theme persistence | `src/stores/theme.store.ts` | `madousho_theme` contract |
| Admin shell | `src/layouts/AdminLayout.vue` | Header order, sidebar behavior, themed shell |
| Runtime i18n | `src/i18n.ts` | Only zh-CN loaded into `messages` |
| Mock API surface | `src/mocks/handlers.ts` | Add handlers for new endpoints |
| E2E setup | `tests/e2e/*.spec.ts` | Seed auth/theme through `page.addInitScript()` |

## CHILD GUIDES

- `src/stores/AGENTS.md` — auth/theme persistence and store-specific test contracts
- `src/layouts/AGENTS.md` — admin shell structure, required test ids, action ordering
- `src/mocks/AGENTS.md` — MSW handler conventions and response-shape expectations
- `tests/e2e/AGENTS.md` — Playwright seeded-state strategy and integration rules

## CONVENTIONS

- Use `@/` for anything under `src`; avoid relative imports into app code.
- Vite includes only `./src/locales/zh-CN/**/*.json`; `en-US/` on disk is not active runtime coverage.
- SCSS variables are auto-injected from `@/assets/scss/_variables`; do not import them manually.
- Build artifacts go to repo-root `../public`; `frontend/public/` is source-side static input, not the final build output.
- Unit tests live beside features under `src/**/__tests__/`; app tsconfig excludes them and `tsconfig.vitest` brings them back for tests.
- Playwright runs its own dev server on `:5174` with `VITE_USE_MOCKS=true`.

## PROJECT-SPECIFIC GOTCHAS

- This app is coupled to the backend serving model: `npm run build` empties and rewrites repo-root `public/`.
- Auth state is multi-backend, not single-token; backend switching and persistence are part of the product contract.
- Theme behavior is split across store logic, Naive UI overrides, and explicit `[data-theme='...'] .admin-*` CSS.
- Layout and E2E tests treat header control order and several `data-testid` values as stable API.

## ANTI-PATTERNS

- **DO NOT** edit repo-root `public/` as source.
- **DO NOT** hardcode visible strings; add zh-CN locale JSON and wire new namespaces if needed.
- **DO NOT** call APIs outside the shared client or skip MSW coverage for new endpoints.
- **DO NOT** assume an `en-US` file on disk means runtime translations are active.
- **DO NOT** treat a `data-theme` flip as sufficient theme verification; shell visuals must actually change.
- **DO NOT** rely on login-form flow in local E2E; seed storage instead.

## COMMANDS

```bash
npm run dev
npm run build
npm run lint
npm run type-check
npm run test:unit
npm run test:e2e
```

## NOTES

- Node engine: `^20.19.0 || >=22.12.0`
- `vitest.config.ts` excludes `tests/e2e/**`
- `playwright.config.ts` uses Chromium only and retries in CI
- Related: `../AGENTS.md` for repo-wide Python/backend context
