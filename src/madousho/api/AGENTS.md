# API - FastAPI Server

## OVERVIEW

FastAPI application for HTTP API serving. Non-standard location (outside commands/) - mounted by `serve` command. Uses public/protected router split for auth enforcement.

## STRUCTURE

```
api/
├── __init__.py         # Empty (module marker)
├── main.py             # FastAPI app, static file mounting, router registration
├── deps.py             # Dependency injection (get_db for database sessions)
├── auth.py             # Token verification middleware (AuthError, verify_token)
├── errors.py           # Unified error format (ErrorResponse, error_response helper)
├── routes/
│   ├── __init__.py     # Router exports (public_router, protected_router)
│   └── flow.py         # Flow CRUD endpoints (list, get, create)
└── schemas/
    ├── __init__.py     # Empty (module marker)
    └── flow.py         # Pydantic schemas (FlowCreate, FlowResponse, FlowListResponse)
```

## WHERE TO LOOK

| Component | File | Purpose |
|-----------|------|---------|
| FastAPI app | `main.py` | `app` instance, version, contact, license, static file mounting |
| Dependencies | `deps.py` | `get_db()` - yields database session for dependency injection |
| Auth | `auth.py` | `AuthError` exception, `verify_token()` - Bearer + X-API-Token validation |
| Errors | `errors.py` | `ErrorResponse` model, `error_response()` helper, error constants |
| Public routes | `routes/__init__.py` | `public_router` - unauthenticated endpoints (health check) |
| Protected routes | `routes/__init__.py` | `protected_router` - auth-required endpoints (flow CRUD) |
| Flow endpoints | `routes/flow.py` | GET /flows (list), GET /flows/{uuid} (detail), POST /flows (create) |
| Flow schemas | `schemas/flow.py` | `FlowCreate`, `FlowResponse`, `FlowListResponse` |
| Static files | `main.py:18-21` | SPA static file serving from `public/` directory |

## ROUTER ARCHITECTURE

Two routers with different auth requirements:

```python
# routes/__init__.py
public_router = APIRouter()                        # No auth
protected_router = APIRouter(
    dependencies=[Depends(bearer_scheme), Depends(verify_token)]  # Auth required
)

# Mounted in main.py
app.include_router(public_router, prefix="/api/v1")
app.include_router(protected_router, prefix="/api/v1")
```

**Public endpoints**: `/api/v1/health`
**Protected endpoints**: `/api/v1/flows/*`, `/api/v1/protected`

## CONVENTIONS

- **Router prefix**: All API routes under `/api/v1` prefix (set in `main.py:24-25`)
- **Dependency injection**: Use `Depends(get_db)` for database access in route handlers
- **Chinese comments**: Infrastructure files use Chinese docstrings/comments
- **Static file mounting**: SPA files served at root `/`, API at `/api/v1`
- **Health endpoint**: `/api/v1/health` returns `{"status": "ok"}` for load balancer checks
- **Error format**: Always use `error_response(status_code, error_code, message)` for consistent JSON errors
- **Schema separation**: Pydantic request/response models in `schemas/`, route handlers in `routes/`

## FLOW CRUD API

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/flows` | Yes | List flows (paginated, filterable by status/plugin/name) |
| GET | `/api/v1/flows/{uuid}` | Yes | Get single flow by UUID |
| POST | `/api/v1/flows` | Yes | Create new flow (returns `{uuid}`) |

Query parameters for list: `offset` (0), `limit` (20, max 100), `status`, `plugin`, `name` (fuzzy).

## MOUNTING IN SERVE COMMAND

From `commands/serve.py`:
```python
uvicorn.run("madousho.api.main:app", host=host, port=port, reload=reload)
```

## ANTI-PATTERNS

- **DO NOT** import from `src.` prefix - use `madousho.api.` instead
- **DO NOT** create multiple FastAPI apps - single `app` instance in `main.py`
- **DO NOT** bypass dependency injection - always use `Depends(get_db)` for DB access
- **DO NOT** add routes directly to `app` - use `public_router` or `protected_router`
- **DO NOT** return raw dicts for errors - use `error_response()` for consistent format
- **DO NOT** skip auth on sensitive endpoints - use `protected_router`

## TESTING

API endpoints tested with `TestClient`:
```python
from fastapi.testclient import TestClient
from madousho.api.main import app

client = TestClient(app)
response = client.get("/api/v1/health")
assert response.status_code == 200
assert response.json() == {"status": "ok"}
```

For protected endpoints, mock config token:
```python
class MockConfig:
    def __init__(self, token: str = TEST_TOKEN) -> None:
        self.api = SimpleNamespace(token=token)

monkeypatch.setattr(loader, "_cached_config", MockConfig())
response = client.get("/api/v1/flows", headers={"Authorization": f"Bearer {token}"})
```

See: `tests/api/test_health.py`, `tests/api/test_auth.py`, `tests/api/test_flow_crud.py`

## RELATED

- Commands: `src/madousho/commands/serve.py` for server startup
- Database: `src/madousho/database/AGENTS.md` for session management
- Config: `src/madousho/config/AGENTS.md` for configuration loading
