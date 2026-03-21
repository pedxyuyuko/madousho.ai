# Stores Knowledge Base

## OVERVIEW

Cross-cutting runtime state lives here: auth persistence, backend selection, theme persistence, and DOM theme mutation.

## WHERE TO LOOK

| Task | File | Notes |
|------|------|-------|
| Auth state | `auth.store.ts` | `madousho_backends`, login verification, backend switching |
| Theme state | `theme.store.ts` | `madousho_theme`, `data-theme`, system preference listener |
| Re-export surface | `index.ts` | Shared import entry when adding more stores |
| Store tests | `__tests__/auth.store.test.ts` | Encodes auth semantics |
| Theme tests | `__tests__/theme.store.test.ts` | Encodes storage and DOM mutation rules |

## CONVENTIONS

- Store files use `<name>.store.ts` naming.
- Auth store normalizes trailing slashes before probing `/api/v1/protected`.
- Persisted auth shape is `{ backends, currentBackendIndex }` under `madousho_backends`.
- Persisted theme shape is `{ userPreference }` under `madousho_theme`.
- Theme changes update `document.documentElement[data-theme]` through store methods, not callers.

## TEST-ENFORCED CONTRACTS

- Logging into an existing backend updates its token instead of duplicating entries.
- Invalid login must leave auth state unchanged and reset `loading`.
- `switchBackend()` and `removeBackend()` ignore invalid indexes.
- Theme store must tolerate empty or corrupt localStorage data.
- `resetToSystem()` persists `userPreference: null`.

## IMPORTANT MISMATCH TO NOTICE

- Tests define logout as de-authentication while preserving saved backends.
- Current `auth.store.ts` implementation removes the active backend on `logout()`.
- Treat that as an active contract hotspot before changing auth behavior or tests.

## ANTI-PATTERNS

- **DO NOT** write `localStorage` directly from components.
- **DO NOT** add ad hoc auth state outside Pinia stores.
- **DO NOT** bypass store tests when changing persistence shape or logout semantics.
- **DO NOT** mutate theme DOM state anywhere except the theme store.

## RELATED

- Parent: `../../AGENTS.md`
- Depends on: `../api/client.ts`, `../router/index.ts`, `../theme/*`
