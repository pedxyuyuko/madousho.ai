# src/madousho/flow/ KNOWLEDGE BASE

**Generated:** 2026-03-03
**Commit:** 3b8ad40
**Branch:** master

## OVERVIEW

Flow engine - the core AI agent execution system with fixed flow control, DAG support, and context management.

## STRUCTURE

```
flow/
├── base.py         # FlowBase class, step execution primitives
├── loader.py       # Flow definition loader (328 lines - largest module)
├── models.py       # Flow data models (Pydantic v2)
├── registry.py     # FlowRegistry for flow discovery/registration
└── __init__.py     # Package exports
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Flow execution | `base.py` | `FlowBase`, step primitives |
| Flow loading | `loader.py` | `FlowLoader` - parses flow definitions |
| Flow models | `models.py` | Pydantic models for flow data |
| Flow registry | `registry.py` | `FlowRegistry` - discovery/registration |
| Flow persistence | `loader.py:200+` | Pause/resume functionality |

## CONVENTIONS

- **Flow naming**: `{action}_flow` suffix for flow functions
- **Step registration**: Use `@flow` decorator for flow definitions
- **Context passing**: Shared state via context manager
- **Model validation**: All models use `ConfigDict(extra="forbid")`
- **Type hints**: Full typing required (Python 3.14+ target)

## ANTI-PATTERNS (THIS MODULE)

- DO NOT bypass FlowLoader - always use registry for flow discovery
- DO NOT use Pydantic v1 methods (`.dict()`, `.parse_obj()`)
- DO NOT modify flow state directly - use context manager
- DO NOT skip flow validation before execution
- DO NOT hardcode flow paths - use registry lookup

## UNIQUE STYLES

- **Fixed flow control**: Flow structure predefined, model executes steps
- **DAG support**: Flows can have directed acyclic graph structure
- **Context trimming**: Automatic context size management
- **Flow persistence**: Flows can be paused/resumed via storage backend
- **Plugin architecture**: Git-based plugin system for flow extensions

## NOTES

- **Largest module**: `loader.py` (328 lines) - contains core loading logic
- **Flow persistence**: Uses TinyDB for flow state storage
- **SSE support**: Real-time progress updates via Server-Sent Events
- **Plugin system**: Reserved `plugins/` directory for Git-based installation
