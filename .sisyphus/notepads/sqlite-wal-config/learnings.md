## Flow and Task Models Created (2026-03-12)

### Location
`src/madousho/models/` directory

### Models Created

1. **Flow model** (`src/madousho/models/flow.py`):
   - Primary key: `uuid` (String(36), auto-generated UUID4)
   - Fields: `name`, `description`, `plugin`, `tasks` (JSON)
   - Purpose: Store AI agent workflow definitions

2. **Task model** (`src/madousho/models/task.py`):
   - Primary key: `uuid` (String(36), auto-generated UUID4)
   - Foreign key: `flow_uuid` references `flows.uuid` with CASCADE delete
   - Fields: `label`, `state`, `timeout`, `messages`, `result`, `error`, `started_at`, `completed_at`
   - Indexes: `idx_task_flow_uuid`, `idx_task_state`, `idx_task_created_at`
   - Purpose: Store individual task execution data

3. **Package exports** (`src/madousho/models/__init__.py`):
   - Exports: `Flow`, `Task`

### Verification
```bash
python -c "from src.madousho.models import Flow, Task; print(f'Flow fields: {Flow.__table__.columns.keys()}'); print(f'Task fields: {Task.__table__.columns.keys()}'); print(f'Task indexes: {[idx.name for idx in Task.__table__.indexes]}')"
```

Output:
```
Flow fields: ['uuid', 'name', 'description', 'plugin', 'tasks', 'id', 'created_at', 'updated_at']
Task fields: ['uuid', 'flow_uuid', 'label', 'state', 'timeout', 'messages', 'result', 'error', 'started_at', 'completed_at', 'id', 'created_at', 'updated_at']
Task indexes: ['idx_task_created_at', 'idx_task_flow_uuid', 'idx_task_state']
```

### Notes
- Both models inherit from `BaseModel` which provides optional `id`, `created_at`, `updated_at` fields
- UUID primary keys follow the pattern: `default=lambda: str(uuid.uuid4())`
- Task model includes three indexes for efficient querying by flow, state, and creation time
- Foreign key constraint uses `ondelete="CASCADE"` for automatic cleanup
