# Login Page - Learnings

## Frontend Conventions

- **Pinia store pattern**: Use `defineStore('name', () => { ... })` with setup syntax (composition API style)
- **State typing**: Define interface for state, use `ref<Type['field']>()` pattern
- **Re-exports**: Add new stores to `src/stores/index.ts`
- **Path alias**: `@` maps to `./src` — use `@/api/client` not relative paths
- **SCSS**: Variables auto-injected via Vite config `additionalData` — no manual imports
- **Naive UI**: Imported globally in `main.ts` — no per-component imports needed
- **MSW handlers**: Add to `src/mocks/handlers.ts` handlers array
- **Axios**: Use `apiClient` from `@/api/client` for all API calls

## Vue Router Conventions

- `router/index.ts` exports default router instance
- Use `router.push()` for programmatic navigation
- `beforeEach` guards return `true`, `false`, or `{ path: '...' }` for redirect

## API Client Pattern

- `baseURL: '/api/v1'` — hardcoded, Dev server proxies to localhost:8000
- Bearer token from localStorage in request interceptor
- Response interceptor handles 401/403/500 (currently only console.error)

## Test Conventions

- Vitest + jsdom environment
- `@vue/test-utils` for component testing
- Test files in `__tests__/` directories
- Pattern: `describe('Component', () => { it('should...', ...) })`

## Gotchas

- The current API client has `baseURL: '/api/v1'` hardcoded — this is for dev proxy
- When connecting to remote backends, the frontend will need to construct full URLs
- HomeView.vue currently imports TheWelcome — must be replaced entirely
- App.vue has boilerplate Vue logo and HelloWorld — must be cleaned up

## LoginView.vue Implementation

### Layout Pattern
- 70/30 split using flexbox: `flex: 0 0 70%` / `flex: 0 0 30%`
- Responsive: `column-reverse` on mobile (<768px) puts form on top first
- Dark background base: `#0a0a0f`, panels `#0d0d1a` / `#0f0f18`

### Gradient Design
- Linear gradient: dark purple tones (#0d0d1a → #1a1035 → #2d1b4e)
- Three animated glow orbs with `radial-gradient` + `blur(80px)` + `pulse-slow` animation
- Orbs positioned absolutely with staggered animation durations (6s, 8s, 10s)

### Form Handling
- Validation via `canSubmit` computed: both fields must be non-empty after trim
- Loading state managed locally (not in store) — `isLoading` ref
- Error display via Naive UI `NAlert` with `v-if` conditional
- Disabled states on inputs during loading

### Auth Integration
- Import: `import { useAuthStore } from '@/stores/auth.store'`
- Call: `await authStore.login(baseUrl.trim(), token.trim())`
- Success redirect: `router.push('/')`
- Error caught and displayed, loading always reset in `finally`

### SCSS Variables Used
- `$spacing-sm`, `$spacing-lg`, `$spacing-xl` for spacing
- `$breakpoint-md` (768px) for responsive breakpoint
- Auto-injected via Vite config — no manual imports

### Typography
- Brand title: `'Noto Sans SC'` for Chinese characters (魔導書)
- Subtitle: `'JetBrains Mono'` monospace for technical feel
- Form labels: uppercase, letter-spaced for clarity
