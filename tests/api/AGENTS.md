# Tests/API - FastAPI Authentication Tests

## OVERVIEW

TDD test suite for API authentication. Tests Bearer token, X-API-Token header, and auth bypass for health/OPTIONS. Uses `monkeypatch` for config mocking.

## STRUCTURE

```
tests/api/
├── __init__.py
├── test_auth.py        # Auth middleware tests (Bearer, X-API-Token, priority)
└── test_health.py      # Health endpoint + static file tests
```

## WHERE TO LOOK

| Test File | Coverage | Key Patterns |
|-----------|----------|--------------|
| `test_auth.py` | Auth middleware | Bearer scheme, X-API-Token, header priority, OPTIONS bypass |
| `test_health.py` | Health endpoint | `/api/v1/health`, static file mounting |

## CONVENTIONS

- **Mock config**: Patch `loader._cached_config` with `MockConfig` (SimpleNamespace)
- **TestClient**: Use `TestClient(app)` from FastAPI - no real server needed
- **Class organization**: Group by feature (`TestAuthBearerToken`, `TestHealthEndpoint`)
- **TDD pattern**: Tests written RED phase first (will fail until implementation)

## FIXTURE PATTERNS

### Mock Config
```python
class MockConfig:
    """Minimal mock config with api.token for auth testing."""
    def __init__(self, token: str = TEST_TOKEN) -> None:
        self.api = SimpleNamespace(token=token)

@pytest.fixture
def mock_config(monkeypatch: pytest.MonkeyPatch) -> MockConfig:
    """Patch _cached_config so get_config() returns a controlled token."""
    cfg = MockConfig()
    monkeypatch.setattr(loader, "_cached_config", cfg)
    return cfg
```

### TestClient
```python
@pytest.fixture
def client() -> TestClient:
    """Create TestClient for the FastAPI app."""
    return TestClient(app)
```

## TEST CLASSES

| Class | Purpose |
|-------|---------|
| `TestAuthMissingToken` | 401 when no auth headers |
| `TestAuthBearerToken` | Bearer scheme validation |
| `TestAuthXApiToken` | X-API-Token header validation |
| `TestAuthHeaderPriority` | Authorization takes priority |
| `TestHealthEndpointBypass` | Health endpoint skips auth |
| `TestOptionsBypass` | OPTIONS requests skip auth |
| `TestOpenAPISecurityScheme` | OpenAPI spec declares security |

## ANTI-PATTERNS

- **DO NOT** use real config files - always mock `_cached_config`
- **DO NOT** test multiple auth methods in one function - one assertion per test
- **DO NOT** forget health/OPTIONS bypass tests - they must remain unauthenticated

## RELATED

- API: `src/madousho/api/` for implementation
- Auth: `src/madousho/api/auth.py` for token verification
- Config: `src/madousho/config/AGENTS.md` for config patterns
