# Flow CRUD - Learnings

## Conventions
- UUID primary keys: `String(36)` with `uuid.uuid4()` default
- Database singleton: `Database.get_instance()`
- DB session: `Depends(get_db)` + context manager auto commit/rollback
- Config mocking: Patch `loader._cached_config` with `MockConfig(SimpleNamespace)`
- Tests: TestClient + pytest fixtures + in-memory SQLite

## Patterns
- protected_router for authenticated endpoints
- public_router for unauthenticated endpoints
- ErrorResponse format: `{"error": "...", "message": "..."}`
- Pydantic v2: `model_config`, `Field()`, `field_validator`

## Anti-patterns to Avoid
- Never use autoincrement IDs - UUID required
- Never call `Database()` directly - use `Database.get_instance()`
- Never bypass `db.session()` context manager
- Never import from `src.` prefix - use `madousho.` instead
