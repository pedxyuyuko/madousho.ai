# Frontend - Vue 3 SPA

**Generated:** 2026-03-18 | **Commit:** 7dc2ead | **Branch:** frontend

## OVERVIEW

Vue 3 SPA for Madousho.ai dashboard. Built with Vite 7, TypeScript, Pinia, and Naive UI. Features a dual-theme system (starry-night dark / parchment light) with smooth transitions. Dev server proxies `/api/v1` to FastAPI backend. Production builds output to `../public/`.

## STRUCTURE

```
frontend/
├── src/
│   ├── main.ts              # App bootstrap (Pinia, Router, Naive UI, MSW in dev)
│   ├── App.vue               # Root: NConfigProvider with theme overrides
│   ├── i18n.ts               # vue-i18n setup (zh-CN locale, lazy-loaded JSON)
│   ├── api/
│   │   └── client.ts         # Axios instance, Bearer token interceptor, error handling
│   ├── assets/
│   │   ├── base.css, main.css
│   │   ├── css/              # login.css, themes.css
│   │   └── scss/             # _variables.scss auto-injected (no manual imports)
│   ├── components/
│   │   ├── BackendSwitcher.vue   # Dropdown for switching API backends
│   │   ├── ThemeSwitcher.vue     # Dark/light toggle (🌙/☀️)
│   │   ├── HelloWorld.vue, TheWelcome.vue, WelcomeItem.vue
│   │   ├── icons/
│   │   └── __tests__/        # Co-located component tests
│   ├── locales/zh-CN/        # i18n JSON files (common, login, home, backend, theme)
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
│   │   ├── index.ts          # Theme switcher utility
│   │   ├── starry-night.ts   # Dark theme: deep purple, glass-morphism
│   │   └── parchment.ts      # Light theme: warm cream, medieval manuscript
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
| Bootstrap | `src/main.ts` | App init, MSW in dev, theme store setup |
| Root component | `src/App.vue` | NConfigProvider, theme overrides, header layout |
| API client | `src/api/client.ts` | Axios with Bearer token + 401 redirect to /login |
| i18n | `src/i18n.ts` | vue-i18n config, zh-CN locale, lazy JSON loading |
| Router | `src/router/index.ts` | Lazy-loaded views, auth guards |
| Auth store | `src/stores/auth.store.ts` | Multi-backend auth, localStorage, removeBackend |
| Theme store | `src/stores/theme.store.ts` | Dark/light toggle, system preference, 100ms transition |
| Theme configs | `src/theme/` | Naive UI overrides for each theme |
| Mocks | `src/mocks/handlers.ts` | MSW handlers — add new API mocks here |
| Backend switcher | `src/components/BackendSwitcher.vue` | Dropdown for API backend selection |
| Theme switcher | `src/components/ThemeSwitcher.vue` | Dark/light toggle button |
| Vite config | `vite.config.ts` | Proxy to :8000, SCSS globals, i18n plugin, build output |
| Tests | `src/**/__tests__/` | Co-located Vitest unit tests |
| E2E Tests | `tests/e2e/` | Playwright end-to-end tests |

## CONVENTIONS

- **Path alias**: `@` → `./src` (use `@/components/...` not relative paths)
- **API proxy**: Dev server proxies `/api/v1` → `http://localhost:8000`
- **Build output**: `../public/` — FastAPI serves this at root `/`
- **SCSS globals**: `_variables.scss` auto-injected via `additionalData` (no manual imports)
- **MSW in dev**: Worker starts in `bootstrap()` only when `import.meta.env.DEV`; disable with `VITE_USE_MOCKS=false`
- **Store pattern**: Centralized re-exports in `src/stores/index.ts`; modules in `stores/modules/`
- **Store naming**: `<name>.store.ts` convention
- **Test co-location**: `__tests__/` directories next to source files
- **E2E tests**: Playwright tests in `tests/e2e/`
- **Linting**: Oxlint (fast) + ESLint (Vue/TS) via `run-s lint:*`
- **Component library**: Naive UI — imported globally in `main.ts`
- **Theme system**: Two themes defined in `src/theme/`, managed by `theme.store.ts`
- **i18n**: vue-i18n with zh-CN locale; JSON files in `src/locales/zh-CN/`; auto-loaded via Vite plugin

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
- **Transition**: 100ms overlay animation on theme switch (`isTransitioning` flag)
- **CSS**: Applied via `data-theme` attribute on `document.documentElement`

## i18n SYSTEM

Internationalization via `vue-i18n` with JSON locale files:

```typescript
// src/i18n.ts
export const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages: { 'zh-CN': { common, login, home, backend, theme } },
})
```

- **Locale files**: `src/locales/zh-CN/*.json` — organized by feature (common, login, home, backend, theme)
- **Vite plugin**: `@intlify/unplugin-vue-i18n` auto-includes JSON files via glob pattern
- **Usage**: `const { t } = useI18n()` in components; keys like `t('common.save')`
- **Adding translations**: Create new JSON file → import in `i18n.ts` → add to messages object

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
- **i18n**: Currently zh-CN only; adding languages requires new locale directory + i18n.ts update
- **Circular deps**: Avoided via lazy imports in router guards and API client

## RELATED

- Root: `../AGENTS.md` for project-wide conventions
