# Models - SQLAlchemy Database Models

## OVERVIEW

SQLAlchemy ORM models for database-backed flows and tasks. UUID-based primary keys, JSON fields for flexible data storage.

## WHERE TO LOOK

| Model | File | Purpose |
|-------|------|---------|
| Flow | `flow.py` | AI workflow definitions |
| Task | `task.py` | Individual task execution data |
| Exports | `__init__.py` | `Flow`, `Task` |

## CONVENTIONS

- **UUID primary keys**: `String(36)` with `uuid.uuid4()` default
- **Base class**: Inherits from `src.madousho.database.base_model.Base`
- **Timestamps**: `created_at` uses `datetime.now(timezone.utc)`
- **JSON columns**: Store structured data (task lists, messages, results)
- **Foreign keys**: Task references Flow with `ondelete="CASCADE"`
- **Indexes**: Task model defines `__table_args__` for query performance

## MODEL PATTERNS

**Flow**: Workflow container with name, description, plugin, and task list (JSON).

**Task**: Execution unit with state machine (`pending` → `running` → `completed`/`failed`), timeout, messages (OpenAI format), result/error storage.

## RELATED

- Migrations: `alembic/versions/` for schema changes
- Database: `src/madousho/database/` for connection handling
