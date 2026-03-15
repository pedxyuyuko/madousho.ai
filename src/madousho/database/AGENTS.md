# Database - SQLAlchemy Connection Singleton

## OVERVIEW

Database connection management via singleton pattern. Handles SQLAlchemy engine, session factory, and SQLite-specific optimizations.

## STRUCTURE

```
database/
├── __init__.py         # Exports: Database, Base, BaseModel
├── connection.py       # Database singleton class
└── base_model.py       # Base, BaseModel (DeclarativeBase with optional common fields)
```

## WHERE TO LOOK

| Component | File | Purpose |
|-----------|------|---------|
| Singleton | `connection.py` | `Database` class - single connection instance |
| Base classes | `base_model.py` | `Base` (DeclarativeBase), `BaseModel` (with id/timestamps) |
| Session management | `connection.py` | `db.session()` context manager |
| SQLite tuning | `connection.py` | PRAGMA settings via SQLAlchemy event listeners |

## CONVENTIONS

- **Singleton access**: `Database.get_instance()` - never `Database()` directly
- **Initialization**: `db.init(database_url, sqlite_config={...})` - call once at startup
- **Session usage**: Always use `with db.session() as session:` for transactions
- **Auto commit/rollback**: Context manager handles commit on success, rollback on error
- **SQLite event listeners**: PRAGMA settings applied per-connection via `@event.listens_for`

## DATABASE CLASS METHODS

| Method | Purpose |
|--------|---------|
| `get_instance()` | Get singleton instance |
| `is_initialized()` | Check if `init()` has been called |
| `init(url, sqlite_config)` | Initialize connection |
| `get_engine()` | Get SQLAlchemy Engine |
| `session()` | Context manager for Session |
| `create_all_tables()` | Create all tables (for testing) |
| `dispose()` | Close connection (for test cleanup) |

## SQLITE OPTIMIZATIONS

Configured via `sqlite_config` dict (from `SqliteConfig` in `config/models.py`):

```python
{
    "wal_enabled": True,
    "synchronous": "NORMAL",           # OFF, NORMAL, FULL, EXTRA
    "cache_size": -64000,              # 64MB (negative = KB)
    "temp_store": "MEMORY",
    "mmap_size": 268435456,            # 256MB
    "journal_size_limit": 67108864,    # 64MB
    "busy_timeout": 5000,              # 5 seconds (milliseconds)
    "wal_autocheckpoint": 1000,        # Page count threshold
    "locking_mode": "NORMAL",          # NORMAL or EXCLUSIVE
    "foreign_keys": True,
    "ignore_check_constraints": False,
}
```

**Connection pool settings** (separate from SQLite PRAGMAs, in `connection.py`):
```python
pool_size = sqlite_config.get("pool_size", 5)
pool_timeout = sqlite_config.get("pool_timeout", 30)
pool_recycle = sqlite_config.get("pool_recycle", 3600)
```

**Note**: Memory SQLite (`:memory:`) uses `SingletonThreadPool` - pool params ignored.

## ANTI-PATTERNS

- **DO NOT** instantiate `Database` directly - always `get_instance()`
- **DO NOT** call `init()` multiple times - check `is_initialized()` first
- **DO NOT** use session without context manager - manual commit/rollback is error-prone
- **DO NOT** forget to call `dispose()` in test cleanup (singleton persists across tests)

## TESTING PATTERN

```python
@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset Database singleton between tests."""
    yield
    Database.get_instance().dispose()
    Database._instance = None
```

See: `tests/test_database.py` for full test patterns.

## RELATED

- Models: `src/madousho/models/` for ORM model definitions
- Migrations: `alembic/` for schema changes
- Config: `src/madousho/config/` for database configuration
