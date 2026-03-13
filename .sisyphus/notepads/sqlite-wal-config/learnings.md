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

## Alembic Migration Fixed and Applied (2026-03-12)

### Problem
The generated migration file was empty because alembic/env.py didn't properly import the Flow and Task models.

### Solution
1. Fixed `alembic/env.py` to import models: `from src.madousho.models import Flow, Task`
2. Deleted the empty migration file
3. Regenerated migration with `alembic revision --autogenerate -m "create flows and tasks tables"`

### Migration File Verification
Migration ID: `91b3f4ede6ab`

**upgrade()** creates:
- `flows` table with columns: uuid, name, description, plugin, tasks (JSON), created_at
- `tasks` table with columns: uuid, flow_uuid, label, state, timeout, messages (JSON), result (JSON), error (JSON), started_at, completed_at, created_at
- Indexes: `idx_task_created_at`, `idx_task_flow_uuid`, `idx_task_state`

**downgrade()** drops:
- All indexes and tables in reverse order

### Database Verification
```bash
sqlite3 madousho.db ".tables"
```

Output:
```
alembic_version  flows            tasks          
```

### Schema Verification

**flows table:**
```sql
CREATE TABLE flows (
	uuid VARCHAR(36) NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	plugin VARCHAR(255) NOT NULL, 
	tasks JSON, 
	created_at DATETIME, 
	PRIMARY KEY (uuid)
);
```

**tasks table:**
```sql
CREATE TABLE tasks (
	uuid VARCHAR(36) NOT NULL, 
	flow_uuid VARCHAR(36) NOT NULL, 
	label VARCHAR(255) NOT NULL, 
	state VARCHAR(20) NOT NULL, 
	timeout FLOAT, 
	messages JSON, 
	result JSON, 
	error JSON, 
	started_at DATETIME, 
	completed_at DATETIME, 
	created_at DATETIME, 
	PRIMARY KEY (uuid), 
	FOREIGN KEY(flow_uuid) REFERENCES flows (uuid) ON DELETE CASCADE
);
CREATE INDEX idx_task_created_at ON tasks (created_at);
CREATE INDEX idx_task_flow_uuid ON tasks (flow_uuid);
CREATE INDEX idx_task_state ON tasks (state);
```

### Python Query Test
```python
from src.madousho.database.connection import Database
db = Database.get_instance()
db.init('sqlite:///./madousho.db')
with db.session() as session:
    from src.madousho.models import Flow, Task
    flows = session.query(Flow).all()
    tasks = session.query(Task).all()
    print(f'Flows: {len(flows)}, Tasks: {len(tasks)}')
```

Output:
```
Flows: 0, Tasks: 0
```

### Notes
- Alembic autogenerate properly detected both tables and all indexes
- Migration successfully applied with `alembic upgrade head`
- Database queries work correctly after initializing Database singleton with `db.init()`
