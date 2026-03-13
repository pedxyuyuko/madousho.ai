# DATABASE LAYER

## OVERVIEW

SQLite with WAL mode, SQLAlchemy 2.0+ async patterns, connection pooling. Singleton `Database` class manages all connections and sessions.

## WHERE TO LOOK

| File | Purpose |
|------|---------|
| `connection.py` | `Database` singleton, WAL config, session manager |
| `base_model.py` | `Base` declarative, `BaseModel` with optional id/timestamps |
| `__init__.py` | Exports: `Database`, `Base`, `BaseModel` |

## CONVENTIONS

- **Singleton pattern**: `Database.get_instance()` returns unique instance
- **WAL mode**: Auto-enabled via `@event.listens_for("connect")` listener
- **Session management**: Use `db.session()` context manager (auto commit/rollback)
- **Two model patterns**:
  - `BaseModel` → auto increment id, created_at, updated_at
  - `Base` → custom primary key (UUID, etc.)

## SQLite WAL CONFIGURATION

```python
sqlite_config = {
    "journal_mode": "WAL",           # Auto-enabled
    "synchronous": "NORMAL",         # Balance safety/performance
    "cache_size": -64000,            # 64MB page cache
    "temp_store": "MEMORY",          # Temp tables in RAM
    "mmap_size": 268435456,          # 256MB memory-mapped I/O
    "journal_size_limit": 67108864,  # 64MB WAL limit
    "busy_timeout": 30000,           # 30s wait on lock
    "foreign_keys": True,            # Enforce FK constraints
}
```

## CONNECTION MANAGEMENT

```python
# Initialize once
db = Database.get_instance()
db.init(database_url, sqlite_config=sqlite_config)

# Use session
with db.session() as session:
    session.add(obj)
    # Auto-commits on success, rollbacks on error
```

## NOTES

- `check_same_thread=False` for SQLite (multi-threaded access)
- Pool defaults: size=5, timeout=30s, recycle=1h
- Call `db.dispose()` for test cleanup
