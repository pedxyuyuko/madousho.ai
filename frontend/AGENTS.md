# Frontend - Vue 3 SPA

## OVERVIEW

Vue 3 SPA for Madousho.ai dashboard. Built with Vite, TypeScript, Pinia state management, and Naive UI component library. Dev server proxies `/api/v1` to FastAPI backend. Production builds output to `../public/` (served by FastAPI static files).

## STRUCTURE

```
frontend/
├── src/
│   ├── main.ts           # App bootstrap (Pinia, Router, Naive UI, MSW in dev)
│   ├── App.vue            # Root component
│   ├── api/
│   │   └── client.ts      # Axios instance with Bearer token interceptor
│   ├── assets/            # CSS, SCSS (global variables auto-injected)
│   ├── components/        # Reusable Vue components
│   ├── mocks/             # MSW handlers for dev (browser.ts, handlers.ts, node.ts)
│   ├── router/            # Vue Router (currently empty routes)
│   ├── stores/            # Pinia stores (index.ts re-exports all stores)
│   └── views/             # Page-level components (HomeView, AboutView)
├── vite.config.ts         # Vite config (proxy, SCSS, build output)
├── vitest.config.ts       # Vitest config (jsdom environment)
├── eslint.config.ts       # ESLint + Oxlint + Vue + TypeScript
└── package.json           # Dependencies, scripts
```

## WHERE TO LOOK

| Component | File | Purpose |
|-----------|------|---------|
| Bootstrap | `src/main.ts` | App init, MSW in dev, plugin registration |
| API client | `src/api/client.ts` | Axios with Bearer token + error interceptors |
| Router | `src/router/index.ts` | Vue Router (routes currently empty) |
| Stores | `src/stores/` | Pinia state management |
| Mocks | `src/mocks/` | MSW for API mocking in dev |
| Vite config | `vite.config.ts` | Proxy, SCSS globals, build output |
| Tests | `src/components/__tests__/` | Vitest + Vue Test Utils |

## CONVENTIONS

- **Path alias**: `@` maps to `./src` (use `@/components/...` not relative paths)
- **API proxy**: Dev server proxies `/api/v1` → `http://localhost:8000`
- **Build output**: `../public/` — FastAPI serves this at root `/`
- **SCSS globals**: `_variables.scss` auto-injected via `additionalData` (no manual imports)
- **MSW in dev**: Worker starts in `bootstrap()` only when `import.meta.env.DEV`
- **Store pattern**: Centralized re-exports in `src/stores/index.ts`
- **Linting**: Oxlint (fast) + ESLint (Vue/TS) via `run-s lint:*`
- **Component library**: Naive UI — imported globally in `main.ts`

## ANTI-PATTERNS

- **DO NOT** import SCSS variables manually — they're auto-injected via vite config
- **DO NOT** use relative paths for `src/` — use `@/` alias
- **DO NOT** add API calls without interceptors — use `apiClient` from `@/api/client`
- **DO NOT** skip MSW handlers for new API endpoints — add to `mocks/handlers.ts`
- **DO NOT** modify `public/` directly — it's a build artifact (`vite build` outputs there)

## COMMANDS

```bash
# Development
npm install              # Install dependencies
npm run dev              # Start dev server (port 5173, proxies to :8000)

# Build
npm run build            # Type-check + build to ../public/
npm run preview          # Preview production build

# Quality
npm run lint             # Oxlint + ESLint (auto-fix)
npm run type-check       # vue-tsc type checking
npm run test:unit        # Vitest unit tests
```

## NOTES

- **Node requirement**: `^20.19.0 || >=22.12.0` (enforced in package.json engines)
- **Naive UI**: Component library loaded globally — no per-component imports needed
- **Vue Router**: Currently empty routes — add route definitions to `router/index.ts`
- **SCSS**: Use `scss/` directory for organized stylesheets, `assets/` for static CSS

## RELATED

- Root: `./AGENTS.md` for project-wide conventions
- API: `src/madousho/api/AGENTS.md` for backend API endpoints
- Config: `src/madousho/config/AGENTS.md` for backend configuration
