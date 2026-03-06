# src/madousho/api/ KNOWLEDGE BASE

**Generated:** 2026-03-06
**Commit:** 3b8ad40
**Branch:** master

## OVERVIEW

FastAPI REST API layer with token authentication middleware and health check endpoint.

## STRUCTURE

```
api/
├── __init__.py         # Re-exports FastAPI class (under-exported)
├── app.py              # FastAPI app factory (45 lines)
├── middleware/
│   ├── __init__.py     # Package marker
│   └── auth.py         # TokenAuthMiddleware
└── routes/
    ├── __init__.py     # Package marker
    └── health.py       # Health check endpoint
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| App factory | `app.py:16` | `create_app()` - FastAPI instance |
| Auth middleware | `middleware/auth.py` | TokenAuthMiddleware |
| Health check | `routes/health.py` | `/` endpoint |
| Version import | `app.py:8-14` | From `_version.py` with fallback |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `create_app` | fn | app.py:16 | FastAPI factory function |
| `TokenAuthMiddleware` | class | middleware/auth.py | Token authentication |
| `router` | APIRouter | routes/health.py | Health check router |

## CONVENTIONS

- **App factory pattern**: `create_app()` function returns configured FastAPI instance
- **Middleware first**: Auth middleware added before routes
- **Version from package**: Import from `madousho._version` (setuptools_scm)
- **Logger**: Use loguru logger (not print)
- **API prefix**: `/api/v1` for versioned routes (currently commented out)

## ANTI-PATTERNS (THIS MODULE)

- DO NOT export only `FastAPI` class from `__init__.py` - should export `create_app`
- DO NOT use print statements - use loguru logger
- DO NOT skip version import fallback (handles missing `_version.py`)
- DO NOT add routes without including router in `create_app()`

## UNIQUE STYLES

- **Dual version import**: Try `_version.py` first, fallback to `__init__.py`
- **Loguru configuration**: Configured in `create_app()` with custom format
- **Commented router**: `/api/v1` router prepared but not included (no routes yet)

## NOTES

- **Under-exported**: `__init__.py` only exports `FastAPI` class, not `create_app`
- **Health check**: Currently only endpoint at `/` (not `/api/v1/health`)
- **Auth middleware**: TokenAuthMiddleware initialized with `token=None` (disabled)
- **Logger format**: `YYYY-MM-DD HH:mm:ss | level | name:function:line - message`
