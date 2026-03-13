# ALEMBIC MIGRATIONS

**Scope:** Database schema migrations with Alembic
**Config:** SQLite URL in `alembic.ini` (or env var)

## OVERVIEW

Auto-generated migrations from SQLAlchemy model changes. Version files follow pattern `{revision_id}_{slug}.py`. Each migration has `upgrade()` and `downgrade()` functions wrapped in transactions.

## WHERE TO LOOK

| File | Purpose |
|------|---------|
| `env.py` | Migration environment, imports models for autogenerate |
| `versions/` | Auto-generated migration scripts |
| `alembic.ini` | DB URL, logging config |

## WORKFLOW

```bash
# 1. Modify models in src/madousho/models/
# 2. Auto-generate migration
alembic revision --autogenerate -m "description"

# 3. Review generated SQL in versions/
# 4. Apply migrations
alembic upgrade head

# 5. Rollback if needed
alembic downgrade -1
```

## CONVENTIONS

- Revisions auto-generated, do not hand-edit unless necessary
- Each migration is a complete schema change (up + down)
- Foreign keys use `ondelete='CASCADE'` for cleanup
- Indexes named: `idx_{table}_{column}`
- UUIDs stored as `String(36)`
- Timestamps use `DateTime()` without timezone

## ANTI-PATTERNS

- DO NOT modify merged migrations (breaks history)
- DO NOT skip review of auto-generated code
- DO NOT run migrations without backup in production
- Avoid data-loss operations in `upgrade()`
- Never commit without testing `downgrade()` first

## NOTES

- `env.py` imports models for metadata autogenerate
- SQLite WAL mode configured at connection level
- Migration history tracked in `alembic_version` table
