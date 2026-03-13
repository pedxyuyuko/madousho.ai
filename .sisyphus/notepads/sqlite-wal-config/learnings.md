## 2026-03-12: Added SQLite WAL Configuration Models

### Changes Made
Added SQLite WAL configuration models to `src/madousho/config/models.py`:

1. **SqliteConfig class** - 11 WAL configuration fields:
   - `wal_enabled` (bool, default=True) - Enable Write-Ahead Logging mode
   - `synchronous` (str, default="NORMAL") - Synchronization mode
   - `cache_size` (int, default=-64000) - Page cache size in KB
   - `temp_store` (str, default="DEFAULT") - Temporary storage location
   - `mmap_size` (int, default=268435456) - Memory-mapped I/O size (256MB)
   - `journal_size_limit` (int, default=67108864) - WAL file size limit (64MB)
   - `busy_timeout` (int, default=5000) - Busy timeout in milliseconds
   - `wal_autocheckpoint` (int, default=1000) - Auto-checkpoint page count
   - `locking_mode` (str, default="NORMAL") - Database locking mode
   - `foreign_keys` (bool, default=True) - Enable foreign key constraints
   - `ignore_check_constraints` (bool, default=False) - Ignore CHECK constraints

2. **DatabaseConfig class** - Database configuration container:
   - `url` (str, default="sqlite://./madousho.db") - Database connection URL
   - `sqlite` (SqliteConfig) - SQLite-specific configuration

3. **Config class update** - Added `database` field with default_factory

### Verification
```bash
python -c "from src.madousho.config.models import SqliteConfig; c = SqliteConfig(); print(c.wal_enabled, c.synchronous, c.cache_size)"
# Output: True NORMAL -64000
```

### Notes
- Followed existing Pydantic model patterns with Field defaults and descriptions
- No new linting errors introduced (pre-existing warnings about deprecated typing.Dict/List)
- Models use default_factory for nested configurations to avoid mutable default arguments
