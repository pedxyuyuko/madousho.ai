# Login Page - Design Decisions

## Multi-Backend Architecture

- **Storage format**: `[{ baseUrl: string, token: string, name?: string }]` + `currentBackendIndex: number` in localStorage key `madousho_backends`
- **Base URL input**: User enters host+port (e.g. `http://localhost:8000`), frontend auto-appends `/api/v1`
- **Auto-backend name**: Derive from URL hostname if no name provided

## Auth Flow

- **Verification**: Login calls `{baseUrl}/api/v1/protected` with Bearer token
- **Success**: Save backend credentials, set as current, redirect to `/`
- **Failure**: Show error, keep user on login page
- **401 handling**: Auto-logout + redirect to `/login` on any API 401

## API Client Design

- **Dynamic baseURL**: Axios interceptor reads from auth store reactively
- **Lazy store access**: Avoid circular deps by importing store inside interceptor
- **Token source**: Read from auth store, not localStorage directly

## Routing Strategy

- **Routes**: Only `/login` and `/`
- **No catch-all**: Avoids infinite redirect loop (no dashboard exists)
- **Guard logic**: Unauth on `/` → `/login`. Auth on `/login` → `/`

## UI Layout

- **Login page**: 70% left gradient + 30% right form (flexbox)
- **Responsive**: Mobile (<768px) stacks vertically
- **Backend switcher**: Top bar dropdown in App.vue, only visible when authenticated

## TDD Approach

- Tests written BEFORE or alongside implementation
- Each task has dedicated test task
- RED → GREEN → REFACTOR cycle
