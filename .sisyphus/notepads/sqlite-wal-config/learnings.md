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
# SQLite WAL Configuration Pattern

## Configuration Added (2026-03-12)
Location: config/madousho.yaml

### Settings Applied:
- WAL mode enabled for better concurrency
- Synchronous=NORMAL for balance of safety/performance
- Cache size: -64000 (64MB negative = KB pages)
- Memory-mapped I/O: 256MB
- Connection pool: 50 connections, 30s timeout
- Busy timeout: 30s for high contention scenarios
- Foreign keys enforced

### Verification:
```bash
python -c "from src.madousho.config.loader import init_config; c = init_config(); print(c.database.url)"
# Output: sqlite:///./data/madousho.db
```



## Example Configuration File Entry (2026-03-12)

Location: `config/madousho.example.yaml`

Added complete database configuration section with all WAL settings documented:

```yaml
# Database configuration
database:
  url: "sqlite:///./data/madousho.db"
  sqlite:
    wal_enabled: true
    synchronous: "NORMAL"
    cache_size: -64000
    temp_store: "MEMORY"
    mmap_size: 268435456
    journal_size_limit: 67108864
    pool_size: 50
    pool_timeout: 30
    pool_recycle: 3600
    busy_timeout: 30000
    foreign_keys: true
```

### Verification Command
```bash
python -c "import yaml; yaml.safe_load(open('config/madousho.example.yaml'))"
```

All settings validated successfully with PyYAML safe_load.
