# Mocks Knowledge Base

## OVERVIEW

MSW handlers here define the frontend’s default dev/test API surface and are part of normal feature work, not optional scaffolding.

## WHERE TO LOOK

| Task | File | Notes |
|------|------|-------|
| Browser worker boot | `browser.ts` | Dev-side MSW startup |
| Node test server | `node.ts` | Test-side server wiring |
| API handlers | `handlers.ts` | Canonical mocked endpoints |
| Handler tests | `__tests__/flows-handler.test.ts` | Response-shape assertions |

## CONVENTIONS

- Add new frontend endpoints to `handlers.ts` when UI work depends on mocks.
- Handler URLs use wildcard host matching like `*/api/v1/...`.
- Mock payloads should match backend response shape, not a UI-friendly approximation.
- Flow fixtures currently exercise enum values `created`, `processing`, `finished`.

## TEST-ENFORCED CONTRACTS

- Unhandled MSW requests fail tests via `onUnhandledRequest: 'error'`.
- `/api/v1/flows` must return `{ items, total, offset, limit }`.
- Each mocked `Flow` must include every required field.
- `/api/v1/protected` returns 401 when Authorization is missing.

## ANTI-PATTERNS

- **DO NOT** add UI API calls without adding or updating corresponding mock handlers.
- **DO NOT** return partial shapes that diverge from backend contracts.
- **DO NOT** silently allow unhandled requests in tests.

## RELATED

- Parent: `../../AGENTS.md`
- Used by: `../main.ts`, `../../playwright.config.ts`, feature tests under `src/**/__tests__`
