# Models - SQLAlchemy Database Models

## OVERVIEW

SQLAlchemy ORM models for database-backed flows and tasks. UUID-based primary keys, JSON fields for flexible data storage.

## STRUCTURE

```
models/
├── __init__.py         # Exports: Flow, Task
├── enums.py            # FlowStatus enum (created, processing, finished)
├── flow.py             # Flow model (workflow container)
└── task.py             # Task model (execution unit)
```

## WHERE TO LOOK

| Model | File | Purpose |
|-------|------|---------|
| Flow | `flow.py` | AI workflow definitions (name, description, plugin, tasks) |
| Task | `task.py` | Individual task execution data (state machine, messages, results) |
| FlowStatus | `enums.py` | Flow lifecycle states: `created`, `processing`, `finished` |
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
