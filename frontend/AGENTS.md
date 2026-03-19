# Frontend - Vue 3 SPA

**Generated:** 2026-03-19 | **Commit:** f24a7e9 | **Branch:** frontend

## OVERVIEW

Vue 3 SPA for Madousho.ai dashboard. Built with Vite 7, TypeScript, Pinia, and Naive UI. Current frontend shape includes an authenticated admin shell (`AdminLayout.vue`), backend/language/theme header controls, dual-theme support, and Playwright coverage that seeds auth state through localStorage.

## STRUCTURE

```
frontend/
├── src/
│   ├── main.ts              # App bootstrap (Pinia, Router, Naive UI, MSW in dev)
│   ├── App.vue               # Root: NConfigProvider, theme binding, transition overlay
│   ├── i18n.ts               # vue-i18n setup (zh-CN namespaces: common/login/home/backend/theme/admin)
│   ├── api/
│   │   └── client.ts         # Axios instance, Bearer token interceptor, error handling
│   ├── assets/
│   │   ├── base.css, main.css
│   │   ├── css/              # login.css, themes.css
│   │   └── scss/             # _variables.scss auto-injected (no manual imports)
│   ├── components/
│   │   ├── BackendSwitcher.vue   # Dropdown for switching API backends
│   │   ├── ThemeSwitcher.vue     # Dark/light toggle (🌙/☀️)
│   │   ├── LanguageSwitcher.vue  # zh-CN / en-US label switcher (UI only; en-US placeholders)
│   │   └── __tests__/            # Co-located component tests + local vue shim for tests
│   ├── layouts/
│   │   ├── AdminLayout.vue       # Authenticated shell: collapsible sider + header actions + RouterView
│   │   └── __tests__/            # Layout-focused Vitest tests
│   ├── locales/
│   │   ├── zh-CN/                # Active locale namespaces
│   │   └── en-US/                # Placeholder admin namespace only
│   ├── mocks/                # MSW handlers for dev (disable: VITE_USE_MOCKS=false)
│   │   ├── browser.ts, node.ts
│   │   └── handlers.ts       # Mock API responses (add new endpoints here)
│   ├── router/
│   │   ├── index.ts          # Vue Router, auth guards
│   │   └── __tests__/        # Guard tests
│   ├── stores/
│   │   ├── index.ts          # Centralized re-exports
│   │   ├── auth.store.ts     # Multi-backend auth (login, logout, switchBackend, removeBackend)
│   │   ├── theme.store.ts    # Theme state, persistence, system listener
│   │   ├── counter.ts
│   │   ├── modules/          # Extended store modules
│   │   │   └── example.store.ts
│   │   └── __tests__/        # Store tests
│   ├── theme/                # Naive UI GlobalThemeOverrides
│   │   ├── index.ts          # getThemeOverrides(name)
│   │   ├── starry-night.ts   # Dark theme + Dropdown option overrides
│   │   └── parchment.ts      # Light theme + Dropdown option overrides
│   └── views/
│       ├── HomeView.vue, LoginView.vue
│       └── __tests__/        # View tests
├── tests/
│   └── e2e/                  # Playwright end-to-end tests
├── vite.config.ts            # Proxy, SCSS, i18n plugin, build output to ../public
├── vitest.config.ts          # jsdom environment
├── playwright.config.ts      # E2E test configuration
├── eslint.config.ts          # Vue/TS + Oxlint + Vitest plugin
├── tsconfig.app.json         # noUncheckedIndexedAccess, @/* paths
└── package.json
```

## WHERE TO LOOK

| Component | File | Purpose |
|-----------|------|---------|
| Bootstrap | `src/main.ts` | App init, optional MSW in dev, theme store setup |
| Root component | `src/App.vue` | NConfigProvider, theme overrides, `data-theme` binding |
| API client | `src/api/client.ts` | Axios with Bearer token + 401 redirect to /login |
| i18n | `src/i18n.ts` | vue-i18n config, admin namespace registration |
| Router | `src/router/index.ts` | Lazy-loaded views, auth guards, AdminLayout at `/` |
| Auth store | `src/stores/auth.store.ts` | Multi-backend auth, localStorage, removeBackend |
| Theme store | `src/stores/theme.store.ts` | Dark/light toggle, system preference, 100ms transition |
| Theme configs | `src/theme/` | Naive UI overrides for each theme |
| Mocks | `src/mocks/handlers.ts` | MSW handlers — add new API mocks here |
| Backend switcher | `src/components/BackendSwitcher.vue` | Dropdown for API backend selection |
| Theme switcher | `src/components/ThemeSwitcher.vue` | Dark/light toggle button |
| Language switcher | `src/components/LanguageSwitcher.vue` | zh-CN / en-US dropdown, updates `locale.value` directly |
| Admin shell | `src/layouts/AdminLayout.vue` | Collapsible sidebar, themed shell surfaces, logout redirect |
| Vite config | `vite.config.ts` | Proxy to :8000, SCSS globals, i18n plugin, build output |
| Tests | `src/**/__tests__/` | Co-located Vitest unit tests |
| E2E Tests | `tests/e2e/` | Playwright end-to-end tests |

## CONVENTIONS

- **Path alias**: `@` → `./src` (use `@/components/...` not relative paths)
- **API proxy**: Dev server proxies `/api/v1` → `http://localhost:8000`
- **Build output**: `../public/` — FastAPI serves this at root `/`
- **SCSS globals**: `_variables.scss` auto-injected via `additionalData` (no manual imports)
- **MSW in dev**: Worker starts in `bootstrap()` only when `import.meta.env.DEV`; local `.env` may disable it with `VITE_USE_MOCKS=false`
- **Store pattern**: Centralized re-exports in `src/stores/index.ts`; modules in `stores/modules/`
- **Store naming**: `<name>.store.ts` convention
- **Test co-location**: `__tests__/` directories next to source files
- **E2E tests**: Playwright tests in `tests/e2e/`
- **Linting**: Oxlint (fast) + ESLint (Vue/TS) via `run-s lint:*`
- **Component library**: Naive UI — imported globally in `main.ts`
- **Theme system**: Two themes defined in `src/theme/`, managed by `theme.store.ts`, shell surfaces themed via `[data-theme='...']` selectors plus shared CSS vars
- **i18n**: vue-i18n with zh-CN runtime locale; JSON namespaces live under `src/locales/**`, but Vite plugin only auto-includes `zh-CN/**/*.json`
- **Layout testing**: `tsconfig.app.json` excludes `src/**/__tests__/*`; test-local shims may be needed for SFC typing in test folders

## AUTH FLOW

Multi-backend authentication with localStorage persistence (`madousho_backends` key):

```typescript
// Router guard (router/index.ts)
router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  if (to.path === '/login' && authStore.isAuthenticated) return { path: '/' }
  if (to.path !== '/login' && !authStore.isAuthenticated) return { path: '/login' }
  return true
})
```

- **Auth store**: Handles login/logout, backend switching/removal, token storage in localStorage
- **API client**: Attaches Bearer token via interceptor; 401 triggers logout + redirect
- **Backend switcher**: UI dropdown for switching between configured backends
- **removeBackend()**: Removes a backend by index, auto-adjusts currentBackendIndex

## THEME SYSTEM

Dual-theme architecture with Naive UI `GlobalThemeOverrides`:

- **starry-night** (dark): Deep purple `#0d0d1a→#2d1b4e`, glass-morphism cards, glowing accents
- **parchment** (light): Warm cream `#F5E6C8`, medieval manuscript feel, serif fonts
- **Store** (`theme.store.ts`): Manages user preference, system `prefers-color-scheme` listener
- **Transition**: 100ms overlay animation in store + 350ms CSS color/background transitions in `assets/css/themes.css`
- **CSS**: Applied via `data-theme` on `document.documentElement`; AdminLayout shell uses explicit `[data-theme='starry-night'|'parchment'] .admin-*` selectors rather than invented global shell vars
- **Dropdown theming**: `theme/*.ts` use typed `Dropdown.option*` fields, not legacy `Dropdown.peers.InternalMenu`

## i18n SYSTEM

Internationalization via `vue-i18n` with JSON locale files:

```typescript
// src/i18n.ts
export const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages: { 'zh-CN': { common, login, home, backend, theme, admin } },
})
```

- **Locale files**: `src/locales/zh-CN/*.json` — organized by feature (common, login, home, backend, theme, admin)
- **Vite plugin**: `@intlify/unplugin-vue-i18n` auto-includes JSON files via glob pattern
- **Usage**: `const { t } = useI18n()` in components; keys like `t('common.save')`
- **Adding translations**: Create new JSON file → import in `i18n.ts` → add to messages object; en-US placeholder files do not become active until imported into runtime `messages`

## ADMIN LAYOUT PATTERNS

- **Authenticated shell**: `/` renders `AdminLayout` with `<RouterView />` children
- **Sidebar**: 240px expanded / 64px collapsed, text-only placeholder menu items (`Dashboard`, `Flows`), toggle lives inside the sider
- **Header order**: `ThemeSwitcher` → `LanguageSwitcher` → `BackendSwitcher` → logout button
- **Logout flow**: UI calls `authStore.logout()` then `router.push('/login')`
- **Language switch**: UI labels are `中文` / `English`; internal locale values remain `zh-CN` / `en-US`
- **Theme adaptation**: shell visuals must actually change between parchment and starry-night; verify real computed styles, not just `data-theme`

## TESTING PATTERNS

- **Component/layout unit tests**: stub Naive UI and child components rather than mounting full app shell
- **Admin layout E2E**: seed `madousho_backends` and `madousho_theme` in `page.addInitScript()` before `page.goto('/')`
- **Reason for seeded auth**: local manual login can hit real `/api/v1/protected` if MSW is disabled by local env, so layout E2E should avoid relying on login-form flow
- **Verification set for layout work**:
  - `npx vitest run src/components/__tests__/LanguageSwitcher.test.ts`
  - `npx vitest run src/layouts/__tests__/AdminLayout.test.ts`
  - `npx playwright test admin-layout.spec.ts --reporter=line`

## ANTI-PATTERNS

- **DO NOT** import SCSS variables manually — auto-injected via vite config
- **DO NOT** use relative paths for `src/` — use `@/` alias
- **DO NOT** add API calls without interceptors — use `apiClient` from `@/api/client`
- **DO NOT** skip MSW handlers for new API endpoints — add to `mocks/handlers.ts`
- **DO NOT** modify `public/` directly — build artifact only
- **DO NOT** set theme via `localStorage` directly — use `theme.store.ts` methods
- **DO NOT** add theme colors inline — extend `src/theme/*.ts` overrides
- **DO NOT** hardcode user-facing strings — use `t()` from vue-i18n
- **DO NOT** skip adding locale JSON for new features — add to `src/locales/zh-CN/`
- **DO NOT** assume theme adaptation works because the toggle flips `data-theme` — verify shell background/text changes in the live UI
- **DO NOT** rely on local login flow in E2E when local env disables MSW — seed auth state instead

## COMMANDS

```bash
npm run dev              # Dev server (port 5173, proxies to :8000)
npm run build            # Type-check + build to ../public/
npm run preview          # Preview production build
npm run lint             # Oxlint + ESLint (auto-fix)
npm run type-check       # vue-tsc type checking
npm run test:unit        # Vitest unit tests
npm run test:e2e         # Playwright e2e tests
npm run test:e2e:ui      # Playwright with UI mode
npm run test:e2e:headed  # Playwright headed mode (visible browser)
```

## NOTES

- **Node**: `^20.19.0 || >=22.12.0` (enforced in engines field)
- **Naive UI**: Global registration — no per-component imports needed
- **Router**: Lazy-loaded views to avoid circular deps (guard also lazy-imports auth store)
- **TypeScript**: `noUncheckedIndexedAccess` enabled for extra safety
- **MSW**: Browser worker in `public/` directory; disable with `VITE_USE_MOCKS=false` env var
- **i18n runtime**: UI currently ships zh-CN runtime messages plus an en-US label path used by `LanguageSwitcher`; full en-US runtime coverage is not wired yet
- **Circular deps**: Avoided via lazy imports in router guards and API client

## RELATED

- Root: `../AGENTS.md` for project-wide conventions
