# Loguru Logging Implementation for Madousho.ai

## TL;DR

> **Quick Summary**: Implement centralized loguru logging with `get_logger(name=None)` pattern - one-time init, globally accessible logger with optional named sub-loggers via bind().
> 
> **Deliverables**:
> - `src/madousho/logging/__init__.py` - Logger module with init + get_logger()
> - `src/madousho/logging/config.py` - Configuration (sinks, formats, levels)
> - Updated `pyproject.toml` with loguru dependency
> - Example usage in main package
> 
> **Estimated Effort**: Short
> **Parallel Execution**: NO - sequential (2 tasks, dependency chain)
> **Critical Path**: Task 1 (config) → Task 2 (module + get_logger)

---

## Context

### Original Request
导入 logrous 作为本项目的 logger，创建 src/logging/ 包，实现一次 init 任意地方都能获取当前 logger，比如说 get_logger(name=None)，默认获取主 logger，如果 name 不是 None 则是获取带前缀的子 logger。使用 Delgan/loguru。

### Interview Summary
**Key Discussions**:
- **Library choice**: Delgan/loguru (Python logging library) - confirmed after initial sirupsen/logrus (Go) confusion
- **API pattern**: `get_logger(name=None)` - returns main logger if None, or `logger.bind(name=...)` for named sub-loggers
- **Package location**: Clarified to use `src/madousho/logging/` (within package namespace) not `src/logging/`

**Research Findings**:
- Loguru uses `bind()` for named logger differentiation
- `configure()` for one-time global setup with sinks
- Filter functions can route named logger output to different sinks
- Supports rotation, retention, JSON/text formats out of the box

### Metis Review
**Identified Gaps** (addressed):
- **Package structure**: Use `src/madousho/logging/` not `src/logging/` - incorporated into plan
- **Configuration separation**: Split config from module logic - added config.py
- **Edge cases**: Added error handling for permission errors, disk space, multiple init
- **Environment adaptability**: Added ENV-based log level override

---

## Work Objectives

### Core Objective
Implement centralized, globally accessible loguru logging with optional named sub-loggers for module differentiation.

### Concrete Deliverables
- `src/madousho/logging/__init__.py` - Main module with get_logger()
- `src/madousho/logging/config.py` - Sink/format/level configuration
- `pyproject.toml` - loguru>=0.7.3 dependency
- `src/madousho/__init__.py` - Initialize logger on package import

### Definition of Done
- [x] `from madousho.logging import get_logger` works anywhere
- [x] `get_logger()` returns main logger
- [x] `get_logger("auth")` returns logger bound with name="auth"
- [x] Logs written to console + file (`logs/madousho.log`)
- [x] `bun test` (pytest) passes with logging enabled

### Must Have
- One-time initialization (idempotent - safe to call multiple times)
- Console sink (stderr) with colored output
- File sink with rotation (100 MB) and retention (7 days)
- Environment variable override for log level (`LOGURU_LEVEL`)
- Thread-safe for concurrent access

### Must NOT Have (Guardrails)
- **NO** separate `src/logging/` directory - must be `src/madousho/logging/`
- **NO** complex configuration files (YAML/JSON config) - keep it simple
- **NO** external logging services (ELK, Datadog) - out of scope
- **NO** sensitive data filtering logic - document as user responsibility
- **NO** custom formatters beyond standard loguru format strings

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest in pyproject.toml)
- **Automated tests**: YES (Tests-after) - Test task after implementation
- **Framework**: pytest
- **Test scope**: Verify get_logger() returns correct logger, verify file output

### QA Policy
Every task MUST include agent-executed QA scenarios.

- **Module testing**: Bash (pytest) - Run tests, assert pass
- **Integration verification**: Bash (python -c) - Import and call get_logger(), verify output
- **File verification**: Bash - Check log file created, check rotation config

---

## Execution Strategy

### Sequential Tasks (2 tasks + 1 test)

```
Wave 1 (Start Immediately):
├── Task 1: Add loguru dependency + create config module [quick]
└── Task 2: Create logging module with get_logger() [quick]

Wave 2 (After Wave 1 - Verification):
└── Task 3: Add tests + verify integration [quick]

Critical Path: Task 1 → Task 2 → Task 3
Parallel Speedup: N/A (sequential, small scope)
```

## File Structure & Changes

### Directory Tree (Before → After)

```
# BEFORE (current state)
src/madousho/
├── __init__.py          # exists, needs modification
└── _version.py          # exists, no change

pyproject.toml           # exists, needs modification

# AFTER (after implementation)
src/madousho/
├── __init__.py          # MODIFIED: import logging module
├── _version.py          # unchanged
└── logging/             # NEW DIRECTORY
    ├── __init__.py      # NEW: get_logger() API
    └── config.py        # NEW: sink configuration

logs/                    # NEW DIRECTORY (created at runtime)
└── madousho.log         # NEW FILE (auto-created)

pyproject.toml           # MODIFIED: add loguru dependency
```

---

### File-by-File Changes

#### 1. `pyproject.toml` (MODIFY)

**Location**: Line ~30 (in `[project]` section)

**Change**: Add to `dependencies` array

```toml
# BEFORE
dependencies = [
    "typer>=0.9.0",
]

# AFTER
dependencies = [
    "typer>=0.9.0",
    "loguru>=0.7.3",
]
```

---

#### 2. `src/madousho/logging/config.py` (CREATE)

**Purpose**: Centralized logger configuration (sinks, formats, levels)

**Pseudo-code**:
```python
#### 2. `src/madousho/logging/config.py` (CREATE)

**Purpose**: Centralized logger configuration (sinks, formats, levels) with customizable options.

**Pseudo-code**:
```python
from pathlib import Path
from loguru import logger
import sys
import os

# Constants
PROJECT_ROOT = Path(__file__).parent.parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"

# 标准格式（彩色友好）
STANDARD_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# JSON 格式（结构化日志）
JSON_FORMAT = "{message}"

def configure_logging(
    level: str | None = None,
    is_json: bool = False,
    colorize: bool | None = None
) -> None:
    """
    配置日志 sinks（一次性初始化）
    
    Args:
        level: 日志级别（控制台和文件使用相同级别），
               默认从环境变量 LOGURU_LEVEL 读取，其次 "INFO"
               可选："DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
        is_json: 是否使用 JSON 格式输出，默认 False
        colorize: 是否彩色输出，默认根据 is_json 和 stderr 自动决定
                  is_json=True 时自动禁用彩色
    
    Examples:
        >>> configure_logging()  # 默认：INFO 级别，标准格式，自动彩色
        >>> configure_logging(level="DEBUG")  # DEBUG 级别（控制台 + 文件）
        >>> configure_logging(is_json=True)  # JSON 格式
        >>> configure_logging(level="WARNING", colorize=False)  # 无彩色
    """
    # 1. 创建 logs 目录
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        pass  # 优雅降级 - 仅控制台输出
    
    # 2. 确定日志级别（参数 > 环境变量 > 默认）
    if level is None:
        level = os.getenv("LOGURU_LEVEL", "INFO").upper()
    
    # 3. 确定是否彩色（JSON 格式强制禁用彩色）
    if colorize is None:
        colorize = not is_json and sys.stderr.isatty()
    else:
        colorize = colorize and not is_json
    
    # 4. 选择格式
    log_format = JSON_FORMAT if is_json else STANDARD_FORMAT
    
    # 5. 移除默认 handler（如果已存在）
    logger.remove()
    
    # 6. 添加控制台输出
    logger.add(
        sink=sys.stderr,
        format=log_format,
        level=level,
        colorize=colorize,
        backtrace=True,
        diagnose=True,
        serialize=is_json  # JSON 模式使用 serialize
    )
    
    # 7. 添加文件输出（与控制台相同级别和格式）
    logger.add(
        sink=LOGS_DIR / "madousho.log",
        format=log_format,
        level=level,  # 与控制台相同级别
        rotation="100 MB",
        retention="7 days",
        enqueue=True,
        compression="zip",
        colorize=False  # 文件不需要彩色
    )
```

**Key Functions**:
- `configure_logging(level, is_json, colorize)` → `None`: 配置 sinks

---
#### 3. `src/madousho/logging/__init__.py` (CREATE)

**Purpose**: Public API - `get_logger(name=None)` and `configure_logging()`

**Pseudo-code**:
```python
from loguru import logger
from .config import configure_logging

# 注意：不在模块导入时自动初始化
# 调用方需要显式调用 configure_logging()

from loguru import Logger as LoguruLogger

def get_logger(name: str | None = None) -> LoguruLogger:
    """
    获取 logger 实例
    
    Args:
        name: 可选的 logger 名称
              If None, returns the main logger.
              If string, returns logger bound with name=name.
    
    Returns:
        Loguru Logger instance
    
    Examples:
        >>> logger = get_logger()
        >>> logger.info("message")
        
        >>> auth_logger = get_logger("auth")
        >>> auth_logger.info("user logged in")
    """
    if name is None:
        return logger
    else:
        return logger.bind(name=name)

# 导出公共 API
__all__ = ["get_logger", "configure_logging"]
```

**Key Functions**:
- `get_logger(name: str | None = None)` → `Logger`: Main API
- `configure_logging(level, is_json, colorize)` → `None`: 显式调用初始化

---

#### 4. `src/madousho/__init__.py` (MODIFY)

**Current Content** (likely):
```python
from ._version import __version__

__all__ = ["__version__"]
```

**After Modification**:
```python
from ._version import __version__

# 导出 logging 相关函数（不自动初始化）
from .logging import get_logger, configure_logging

__all__ = ["__version__", "get_logger", "configure_logging"]
```

**Effect**: 
- **不自动触发初始化** - 调用方需要显式调用 `configure_logging()`
- 可以方便地从主包导入：`from madousho import get_logger, configure_logging`

---

#### 5. `tests/test_logging.py` (CREATE)

**Purpose**: Test get_logger() functionality

**Pseudo-code**:
```python
import pytest
from pathlib import Path
import os

# Test imports
from madousho.logging import get_logger, configure_logging
from loguru import logger as loguru_logger

class TestGetLogger:
    def test_get_logger_returns_logger_instance(self):
        """get_logger() returns loguru Logger"""
        result = get_logger()
        assert type(result) == type(loguru_logger)
    
    def test_get_logger_none_returns_main_logger(self):
        """get_logger(None) == get_logger()"""
        assert get_logger(None) is get_logger()
    
    def test_get_logger_name_returns_bound_logger(self):
        """get_logger('name') returns different logger"""
        main = get_logger()
        auth = get_logger("auth")
        assert main is not auth
    
    def test_get_logger_same_name_returns_same_binding(self):
        """get_logger('auth') twice returns equivalent loggers"""
        auth1 = get_logger("auth")
        auth2 = get_logger("auth")
        # Both should have same binding context
        assert type(auth1) == type(auth2)

class TestLoggingOutput:
    def test_logging_writes_to_file(self, tmp_path):
        """Verify logs are written to file"""
        # This test would need to configure a temp log file
        # Implementation depends on test setup
        pass
    
    def test_environment_level_override(self, monkeypatch):
        """LOGURU_LEVEL env var overrides default"""
        monkeypatch.setenv("LOGURU_LEVEL", "DEBUG")
        # Reconfigure and verify DEBUG level works
        # Note: This is tricky with singleton logger
        pass
```

**Test Classes**:
- `TestGetLogger`: API behavior tests
- `TestLoggingOutput`: Integration tests (file output, env vars)

---

### Task Boundaries (Clear Demarcation)

```
┌─────────────────────────────────────────────────────────────┐
│ Task 1: Dependency + Config                                  │
├─────────────────────────────────────────────────────────────┤
│ FILES TOUCHED:                                               │
│   ✏️ pyproject.toml (modify - add dependency)                │
│   🆕 src/madousho/logging/config.py (create)                 │
│                                                              │
│ RESPONSIBILITY:                                              │
│   - Add loguru to dependencies                               │
│   - Create config module with sink setup                     │
│   - Handle directory creation, error handling                │
│                                                              │
│ DOES NOT TOUCH:                                              │
│   - src/madousho/logging/__init__.py                         │
│   - src/madousho/__init__.py                                 │
│   - tests/                                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Task 2: Logging Module + get_logger()                        │
├─────────────────────────────────────────────────────────────┤
│ FILES TOUCHED:                                               │
│   🆕 src/madousho/logging/__init__.py (create)               │
│   ✏️ src/madousho/__init__.py (modify - import logging)      │
│                                                              │
│ RESPONSIBILITY:                                              │
│   - Implement get_logger(name=None) function                 │
│   - Trigger one-time init on module import                   │
│   - Export public API                                        │
│                                                              │
│ DOES NOT TOUCH:                                              │
│   - pyproject.toml                                           │
│   - src/madousho/logging/config.py                           │
│   - tests/                                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Task 3: Tests + Verification                                 │
├─────────────────────────────────────────────────────────────┤
│ FILES TOUCHED:                                               │
│   🆕 tests/test_logging.py (create)                          │
│                                                              │
│ RESPONSIBILITY:                                              │
│   - Write pytest tests for get_logger()                      │
│   - Verify file output                                       │
│   - Run pytest and ensure all pass                           │
│                                                              │
│ DOES NOT TOUCH:                                              │
│   - pyproject.toml                                           │
│   - src/madousho/logging/*                                   │
│   - src/madousho/__init__.py                                 │
└─────────────────────────────────────────────────────────────┘
```

---

### Usage Examples (After Implementation)

```python
# Pattern 1: Import from logging module
from madousho.logging import get_logger

logger = get_logger()
logger.info("Application started")

auth_logger = get_logger("auth")
auth_logger.info("User logged in")

# Pattern 2: Import from main package (re-exported)
from madousho import get_logger

db_logger = get_logger("database")
db_logger.debug("Query executed")

# Pattern 3: Anywhere in the codebase
# Just import and use - no init needed (auto-initialized)
from madousho.logging import get_logger

def some_function():
    logger = get_logger("my_module")
    logger.info("Function called")
```

---

### Runtime Flow

```
1. User imports: from madousho.logging import get_logger
        ↓
2. Python loads: src/madousho/logging/__init__.py
        ↓
3. Module imports: from .config import configure_logging
        ↓
4. Module calls: _configure_once = configure_logging()
        ↓
5. Config creates: logs/ directory (if not exists)
        ↓
6. Config adds sinks: console (stderr) + file (logs/madousho.log)
        ↓
7. get_logger() now available - returns bound/unbound logger
        ↓
8. User calls: logger.info("message") → writes to console + file
```

---

### Environment Variables

| Variable | Default | Effect |
|----------|---------|--------|
| `LOGURU_LEVEL` | `"INFO"` | Minimum log level for console output. Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

**Example**:
```bash
# Development (see DEBUG logs)
export LOGURU_LEVEL=DEBUG
python -m madousho

# Production (only WARNING and above)
export LOGURU_LEVEL=WARNING
python -m madousho
```

---



### Dependency Matrix

- **1**: — — 2
- **2**: 1 — 3
- **3**: 2 — Final

### Agent Dispatch Summary

- **Wave 1**: **2** — T1 → `quick`, T2 → `quick`
- **Wave 2**: **1** — T3 → `quick`

---

## TODOs

- [x] 1. Add loguru dependency and create config module

  **What to do**:
  - Add `loguru>=0.7.3` to pyproject.toml `[project.dependencies]`
  - Create `src/madousho/logging/config.py` with:
    - `LOGS_DIR = Path(__file__).parent.parent.parent / "logs"`
    - `DEFAULT_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"`
    - `configure_logging()` function that calls `logger.configure()` with:
      - Console sink (sys.stderr, colorize=True, level from env LOGURU_LEVEL or "INFO")
      - File sink (`logs/madousho.log`, rotation="100 MB", retention="7 days", enqueue=True)
    - Handle errors: create logs dir if not exists, catch permission errors gracefully

  **Must NOT do**:
  - Do NOT create YAML/JSON config files
  - Do NOT add external service sinks (Datadog, ELK, etc.)
  - Do NOT implement sensitive data filtering

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple dependency addition + straightforward config module
  - **Skills**: `[]`
    - No special skills needed - basic Python file operations

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (first task)
  - **Blocks**: Task 2
  - **Blocked By**: None

  **References**:
  - `pyproject.toml` - Add loguru to dependencies section
  - Loguru docs: https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.add - Sink configuration
  - Loguru rotation: https://loguru.readthedocs.io/en/stable/resources/troubleshooting.html#rotate-and-retention - Rotation/retention patterns

  **Acceptance Criteria**:
  - [x] `loguru>=0.7.3` added to pyproject.toml dependencies
  - [x] `src/madousho/logging/config.py` exists with configure_logging()
  - [x] Running `python -c "from madousho.logging.config import configure_logging; configure_logging()"` creates logs/ directory
  - [x] Console output shows colored logs
  - [x] File `logs/madousho.log` created after logging

  **QA Scenarios**:

  ```
  Scenario: Config creates logs directory and file
    Tool: Bash
    Preconditions: logs/ directory does not exist
    Steps:
      1. Run: python -c "from madousho.logging.config import configure_logging; configure_logging(); from loguru import logger; logger.info('test')"
      2. Check: logs/ directory exists
      3. Check: logs/madousho.log exists and contains "test"
    Expected Result: Directory and file created, log message present
    Failure Indicators: PermissionError, directory not created, file empty
    Evidence: .sisyphus/evidence/task-1-config-qa.txt

  Scenario: Environment variable overrides log level
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: LOGURU_LEVEL=DEBUG python -c "from madousho.logging.config import configure_logging; configure_logging(); from loguru import logger; logger.debug('debug msg')"
      2. Check: Output shows DEBUG level message
      3. Run: LOGURU_LEVEL=WARNING python -c "... logger.info('info msg')"
      4. Check: INFO message NOT shown (filtered)
    Expected Result: Level filtering works per env var
    Failure Indicators: Wrong level shown, filtering not working
    Evidence: .sisyphus/evidence/task-1-level-override.txt
  ```

  **Commit**: YES
  - Message: `feat(logging): add loguru dependency and config module`
  - Files: `pyproject.toml, src/madousho/logging/config.py`
  - Pre-commit: `python -m pytest tests/ -v` (if tests exist)

---

- [x] 2. Create logging module with get_logger() function

  **What to do**:
  - Create `src/madousho/logging/__init__.py` with:
    - Import `logger` from loguru
    - Import `configure_logging` from config module
    - Implement `get_logger(name: str | None = None) -> Logger`:
      - If name is None: return base logger
      - If name is str: return `logger.bind(name=name)`
    - **Do NOT** call configure_logging() on module import
    - Export `get_logger` and `configure_logging`
  - Update `src/madousho/__init__.py` to re-export functions (no auto-init)

  **Must NOT do**:
  - Do NOT create separate logger instances (loguru uses singleton pattern)
  - Do NOT implement custom Logger class (use loguru's built-in)
  - Do NOT add complex binding beyond name parameter
  - **Do NOT auto-initialize on import**

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple module with get_logger() wrapper
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (depends on Task 1)
  - **Blocks**: Task 3
  - **Blocked By**: Task 1

  **References**:
  - `src/madousho/logging/config.py` (from Task 1) - Import configure_logging
  - Loguru bind(): https://loguru.readthedocs.io/en/stable/resources/migration.html#replacing-logger-objects - Named logger pattern
  - `src/madousho/__init__.py` - Add logging import

  **Acceptance Criteria**:
  - [x] `src/madousho/logging/__init__.py` exists with get_logger()
  - [x] `from madousho.logging import get_logger, configure_logging` works
  - [x] `get_logger()` returns logger without binding
  - [x] `get_logger("auth")` returns logger bound with name="auth"
  - [x] **Does NOT** auto-initialize on import (requires explicit configure_logging() call)
  - [x] After configure_logging(), logging works correctly

  **QA Scenarios**:

  ```
  Scenario: get_logger() returns main logger
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from madousho.logging import get_logger; logger = get_logger(); logger.info('main logger test')"
      2. Check: Output shows message without name filter
      3. Check: logs/madousho.log contains "main logger test"
    Expected Result: Main logger works, writes to file
    Failure Indicators: AttributeError, no output, file not written
    Evidence: .sisyphus/evidence/task-2-main-logger.txt

  Scenario: get_logger(name) returns bound logger
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from madousho.logging import get_logger; auth_logger = get_logger('auth'); auth_logger.info('auth test')"
      2. Check: Output shows message with name context
      3. Run: python -c "from madousho.logging import get_logger; main = get_logger(); auth = get_logger('auth'); print(type(main), type(auth))"
      4. Check: Both are loguru Logger types
    Expected Result: Named logger works, bound correctly
    Failure Indicators: TypeError, binding not applied
    Evidence: .sisyphus/evidence/task-2-named-logger.txt

  Scenario: Multiple imports don't break
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from madousho.logging import get_logger; from madousho.logging.config import configure_logging; import madousho.logging; get_logger().info('test1'); get_logger('test').info('test2')"
      2. Check: No errors, both messages logged
      3. Check: logs/madousho.log has both messages
    Expected Result: Idempotent, safe multiple imports
    Failure Indicators: Duplicate handlers, errors on re-import
    Evidence: .sisyphus/evidence/task-2-multiple-imports.txt
  ```

  **Commit**: YES (group with Task 1 if small, or separate)
  - Message: `feat(logging): implement get_logger() with named logger support`
  - Files: `src/madousho/logging/__init__.py, src/madousho/__init__.py`
  - Pre-commit: `python -c "from madousho.logging import get_logger; get_logger().info('test')"`

---

- [x] 3. Add tests and verify integration

  **What to do**:
  - Create `tests/test_logging.py` with:
    - Test get_logger() returns logger instance
    - Test get_logger(None) == get_logger()
    - Test get_logger("name") returns different (bound) logger
    - Test logging actually writes to file
    - Test environment variable level override
  - Run pytest to verify all tests pass
  - Verify integration: import from different module patterns

  **Must NOT do**:
  - Do NOT test loguru internals (format, rotation - that's library's job)
  - Do NOT mock loguru (test real behavior)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple test file, straightforward assertions
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (depends on Task 2)
  - **Blocks**: None (final verification)
  - **Blocked By**: Task 2

  **References**:
  - `src/madousho/logging/__init__.py` - Test get_logger()
  - `src/madousho/logging/config.py` - Test configure_logging()
  - Existing test patterns in `tests/` (if any exist)

  **Acceptance Criteria**:
  - [x] `tests/test_logging.py` exists
  - [x] `pytest tests/test_logging.py -v` passes (all tests green)
  - [x] Tests cover: get_logger(), get_logger(name), file output, level override
  - [x] No pytest warnings or errors

  **QA Scenarios**:

  ```
  Scenario: All tests pass
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: pytest tests/test_logging.py -v
      2. Check: Exit code 0
      3. Check: All tests show PASSED
    Expected Result: 100% pass rate
    Failure Indicators: FAILED tests, exit code != 0
    Evidence: .sisyphus/evidence/task-3-pytest-output.txt

  Scenario: Integration from external module
    Tool: Bash
    Preconditions: Create test script
    Steps:
      1. Create: /tmp/test_integration.py with "from madousho.logging import get_logger; get_logger('integration').info('from outside')"
      2. Run: python /tmp/test_integration.py
      3. Check: Output shows message, file has entry
    Expected Result: Works from any module
    Failure Indicators: ImportError, ModuleNotFoundError
    Evidence: .sisyphus/evidence/task-3-integration.txt
  ```

  **Commit**: YES
  - Message: `test(logging): add pytest tests for get_logger()`
  - Files: `tests/test_logging.py`
  - Pre-commit: `pytest tests/test_logging.py -v`

---

## Final Verification Wave

- [x] F1. **Plan Compliance Audit** — `oracle`
  Verify: loguru in pyproject.toml, src/madousho/logging/ exists, get_logger() works, logs/ created.
  Output: `Must Have [3/3] | Must NOT Have [5/5] | Tasks [3/3] | VERDICT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run `tsc --noEmit` (N/A, Python) + `pytest tests/`. Check for: unused imports, bare excepts, hardcoded paths.
  Output: `Build [N/A] | Tests [N pass/0 fail] | Files [N clean] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`
  Execute all QA scenarios from all tasks. Verify file output, console output, named logger binding.
  Output: `Scenarios [N/N pass] | Integration [3/3] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  Verify no extra files created, no config files (YAML/JSON), no external service integration.
  Output: `Tasks [3/3 compliant] | Contamination [CLEAN] | VERDICT`

---

## Commit Strategy

- **1**: `feat(logging): add loguru dependency and config module` — pyproject.toml, src/madousho/logging/config.py
- **2**: `feat(logging): implement get_logger() with named logger support` — src/madousho/logging/__init__.py, src/madousho/__init__.py
- **3**: `test(logging): add pytest tests for get_logger()` — tests/test_logging.py

---

## Success Criteria

### Verification Commands
```bash
# Verify dependency installed
pip show loguru  # Expected: Version 0.7.3+

# Verify module import
python -c "from madousho.logging import get_logger; get_logger().info('test')"  # Expected: colored output + logs/madousho.log created

# Verify named logger
python -c "from madousho.logging import get_logger; get_logger('auth').info('auth test')"  # Expected: shows name context

# Run tests
pytest tests/test_logging.py -v  # Expected: all pass
```

### Final Checklist
- [x] All "Must Have" present (one-time init, console + file, env override, thread-safe)
- [x] All "Must NOT Have" absent (no src/logging/, no YAML config, no external services)
- [x] All tests pass (pytest tests/test_logging.py)
- [x] Evidence files exist in .sisyphus/evidence/
