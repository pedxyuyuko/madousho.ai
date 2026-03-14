# API - FastAPI Server

## OVERVIEW

FastAPI application for HTTP API serving. Non-standard location (outside commands/) - mounted by `serve` command.

## STRUCTURE

```
api/
├── __init__.py         # Empty (module marker)
├── main.py             # FastAPI app, static file mounting, router registration
├── deps.py             # Dependency injection (get_db for database sessions)
├── auth.py             # Token verification middleware
├── errors.py           # Custom exception handlers (Chinese docstrings)
└── routes/
    └── __init__.py     # APIRouter with endpoints (/health)
```

## WHERE TO LOOK

| Component | File | Purpose |
|-----------|------|---------|
| FastAPI app | `main.py` | `app` instance, version, contact, license, static file mounting |
| Dependencies | `deps.py` | `get_db()` - yields database session for dependency injection |
| Auth | `auth.py` | `verify_token()` - Bearer + X-API-Token header validation |
| Errors | `errors.py` | Custom exception classes with unified error format |
| Routes | `routes/__init__.py` | `api_router` - APIRouter with endpoint definitions |
| Static files | `main.py:18-20` | SPA static file serving from `public/` directory |

## CONVENTIONS

- **Router prefix**: All API routes under `/api/v1` prefix (set in `main.py:23`)
- **Dependency injection**: Use `Depends(get_db)` for database access in route handlers
- **Chinese comments**: Infrastructure files use Chinese docstrings/comments
- **Static file mounting**: SPA files served at root `/`, API at `/api/v1`
- **Health endpoint**: `/api/v1/health` returns `{"status": "ok"}` for load balancer checks

## MOUNTING IN SERVE COMMAND

From `commands/serve.py`:
```python
from madousho.api.main import app as api_app
uvicorn.run(api_app, host=host, port=port, reload=reload)
```

## ANTI-PATTERNS

- **DO NOT** import from `src.` prefix - use `madousho.api.` instead
- **DO NOT** create multiple FastAPI apps - single `app` instance in `main.py`
- **DO NOT** bypass dependency injection - always use `Depends(get_db)` for DB access
- **DO NOT** add routes directly to `app` - use `api_router` in `routes/`

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

See: `tests/api/test_health.py` for test patterns.

## RELATED

- Commands: `src/madousho/commands/serve.py` for server startup
- Database: `src/madousho/database/AGENTS.md` for session management
- Config: `src/madousho/config/AGENTS.md` for configuration loading
