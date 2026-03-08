# Typer CLI Framework Initialization

## TL;DR

> **Quick Summary**: Initialize minimal Typer CLI skeleton for madousho-ai project with single `version` subcommand using TDD approach.
> 
> **Deliverables**:
> - `pyproject.toml` with typer>=0.9.0 dependency
> - `src/madousho/cli.py` with Typer app and version command
> - `tests/test_cli.py` with TDD test for version command
> - `tests/__init__.py` for test package structure
> 
> **Estimated Effort**: Short
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Task 1 → Task 3 → Task 4 → Task 5

---

## Context

### Original Request
用户希望在现有 madousho-ai 项目中初始化 Typer CLI 框架环境，使用 pip + venv 环境管理，需要多命令组 CLI 结构。

### Interview Summary
**Key Discussions**:
- **Project**: Existing madousho-ai (not new project)
- **Environment**: pip + venv (virtual env already exists at .venv, Python 3.14)
- **CLI Structure**: Multi-command group CLI pattern with Typer
- **Subcommands**: Only `version` command as minimal skeleton
- **Test Strategy**: TDD with pytest + Typer's CliRunner

**Research Findings**:
- Project uses setuptools_scm for version management
- Entry point already configured: `madousho = "madousho.cli:app"`
- pytest configured in pyproject.toml with `testpaths = ["tests"]`
- `src/madousho/cli.py` does NOT exist yet

### Metis Review
**Identified Gaps** (addressed):
- **Dependency location**: typer must be in `[project.dependencies]` (runtime), not dev
- **tests/ directory**: Must be at project root (matches pyproject.toml testpaths)
- **Version fallback**: Must handle missing `_version.py` with "0.0.0.dev0"
- **Output format**: Simple version string output (no custom formatting)
- **Guardrails**: Explicit exclusions for scope creep (no extra commands/flags)

---

## Work Objectives

### Core Objective
Create minimal Typer CLI skeleton with single `version` subcommand that displays project version from setuptools_scm.

### Concrete Deliverables
- `pyproject.toml` updated with `typer>=0.9.0` dependency
- `src/madousho/cli.py` - Typer app with version command
- `tests/test_cli.py` - TDD test for version command
- `tests/__init__.py` - Test package initialization

### Definition of Done
- [x] `python -m pytest tests/test_cli.py -v` passes (exit code 0)
- [x] `madousho version` outputs version string (after `pip install -e .`)
- [x] `madousho --help` shows version subcommand

### Must Have
- Typer>=0.9.0 in `[project.dependencies]`
- Version command reads from `madousho._version` or fallback
- TDD workflow (test first, then implementation)
- Graceful fallback for missing `_version.py`

### Must NOT Have (Guardrails)
- ❌ No `init`, `config`, `run` subcommands
- ❌ No `--short`, `--long` flags on version command
- ❌ No custom `--help` text customization
- ❌ No complex error handling beyond fallback
- ❌ No additional dependencies beyond typer
- ❌ No `src/madousho/commands/` directory

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: TDD
- **Framework**: pytest with Typer's CliRunner
- **If TDD**: Each task follows RED (failing test) → GREEN (minimal impl) → REFACTOR

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **CLI Commands**: Use Bash to run commands, assert exit codes and output
- **Tests**: Use Bash to run pytest, verify pass/fail status
- **File Operations**: Use Bash to verify file existence and content

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — foundation, 2 parallel):
├── Task 1: Add Typer dependency [quick]
└── Task 2: Create tests directory structure [quick]

Wave 2 (After Wave 1 — TDD cycle, sequential):
├── Task 3: Write version command test (RED phase) [unspecified-low]
└── Task 4: Implement CLI module (GREEN phase) [unspecified-low]

Wave 3 (After Wave 2 — verification):
└── Task 5: Verify entry point works [quick]

Critical Path: Task 1 → Task 3 → Task 4 → Task 5
Parallel Speedup: ~40% faster than sequential (Wave 1 parallel)
Max Concurrent: 2 (Wave 1)
```

### Dependency Matrix

- **1**: — — 3, 4
- **2**: — — 3, 4
- **3**: 1, 2 — 4
- **4**: 3 — 5
- **5**: 4 — None

### Agent Dispatch Summary

- **Wave 1**: **2** — T1 → `quick`, T2 → `quick`
- **Wave 2**: **2** — T3 → `unspecified-low`, T4 → `unspecified-low`
- **Wave 3**: **1** — T5 → `quick`

---

## TODOs

- [x] 1. Add Typer Dependency

  **What to do**:
  - Add `typer>=0.9.0` to `[project.dependencies]` in pyproject.toml
  - Use exact format: `typer>=0.9.0` (not in optional-dependencies)
  - Verify dependency is added to correct section

  **Must NOT do**:
  - Do NOT add to `[project.optional-dependencies]` or dev dependencies
  - Do NOT add additional dependencies (rich, etc.)
  - Do NOT modify other parts of pyproject.toml

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple file edit, single dependency addition
  - **Skills**: []
    - No special skills needed for this straightforward edit

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: Tasks 3, 4
  - **Blocked By**: None (can start immediately)

  **References**:
  - `pyproject.toml:24-24` - Current dependencies section (empty array)
  - Official docs: `https://typer.tiangolo.com/` - Typer installation requirements

  **Acceptance Criteria**:
  - [x] `grep -q 'typer>=' pyproject.toml` returns exit code 0
  - [x] `typer>=0.9.0` appears in `[project.dependencies]` section

  **QA Scenarios**:

  ```
  Scenario: Verify typer in dependencies
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: grep -q 'typer>=' pyproject.toml && echo "PASS: typer in dependencies"
      2. Check exit code is 0
      3. Check output contains "PASS"
    Expected Result: Exit code 0, output contains "PASS: typer in dependencies"
    Failure Indicators: Exit code 1 or no "PASS" in output
    Evidence: .sisyphus/evidence/task-1-verify-dep.txt
  ```

  **Evidence to Capture**:
  - [x] Grep output showing typer in dependencies

  **Commit**: YES (groups with 2)
  - Message: `build(deps): add typer>=0.9.0 dependency`
  - Files: `pyproject.toml`
  - Pre-commit: `python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"`

- [x] 2. Create Tests Directory Structure

  **What to do**:
  - Create `tests/` directory at project root
  - Create `tests/__init__.py` (empty file for pytest discovery)
  - Verify directory structure matches pyproject.toml testpaths

  **Must NOT do**:
  - Do NOT create `src/madousho/tests/` (wrong location)
  - Do NOT add test files yet (that's Task 3)
  - Do NOT modify pyproject.toml testpaths

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple directory/file creation
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Tasks 3, 4
  - **Blocked By**: None (can start immediately)

  **References**:
  - `pyproject.toml:44-44` - testpaths = ["tests"] configuration
  - Pattern: Standard pytest directory structure

  **Acceptance Criteria**:
  - [x] `tests/` directory exists at project root
  - [x] `tests/__init__.py` file exists

  **QA Scenarios**:

  ```
  Scenario: Verify tests directory exists
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: test -d tests && test -f tests/__init__.py && echo "PASS: tests directory exists"
      2. Check exit code is 0
      3. Check output contains "PASS"
    Expected Result: Exit code 0, output contains "PASS"
    Failure Indicators: Exit code 1 (directory or file missing)
    Evidence: .sisyphus/evidence/task-2-verify-tests-dir.txt
  ```

  **Evidence to Capture**:
  - [x] Test command output showing directory exists

  **Commit**: YES (groups with 1)
  - Message: `test(cli): create tests directory structure`
  - Files: `tests/__init__.py`
  - Pre-commit: None needed

- [x] 3. Write Version Command Test (TDD RED Phase)

  **What to do**:
  - Create `tests/test_cli.py` with version command test using Typer's CliRunner
  - Test should verify: exit_code == 0, output is non-empty string
  - Do NOT implement cli.py yet (this is TDD RED phase - test should FAIL)
  - Use regex pattern for version check (not exact string - version changes)

  **Must NOT do**:
  - Do NOT implement src/madousho/cli.py (that's Task 4)
  - Do NOT assert exact version string (use regex or non-empty check)
  - Do NOT test edge cases yet (only happy path)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: Writing test code requires understanding Typer testing patterns
  - **Skills**: []
    - Standard pytest + Typer testing

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Wave 2)
  - **Blocks**: Task 4
  - **Blocked By**: Tasks 1, 2 (need typer installed and tests/ directory)

  **References**:
  - `https://typer.tiangolo.com/tutorial/testing/` - Official Typer testing docs
  - Pattern: Typer CliRunner pattern for invoking CLI commands
  - `pyproject.toml:44-50` - pytest configuration

  **Acceptance Criteria**:
  - [x] `tests/test_cli.py` exists with version command test
  - [x] Test uses `from typer.testing import CliRunner`
  - [x] Test imports app from `madousho.cli`
  - [x] Running test FAILS (module doesn't exist yet - this is correct TDD RED)

  **QA Scenarios**:

  ```
  Scenario: Verify test file created
    Tool: Bash
    Preconditions: Tasks 1, 2 complete
    Steps:
      1. Run: test -f tests/test_cli.py && echo "PASS: test file exists"
      2. Check exit code is 0
    Expected Result: Exit code 0, file exists
    Failure Indicators: Exit code 1 (file missing)
    Evidence: .sisyphus/evidence/task-3-test-exists.txt

  Scenario: TDD RED phase - test should fail
    Tool: Bash
    Preconditions: Test file created, cli.py NOT implemented yet
    Steps:
      1. Run: python -m pytest tests/test_cli.py::test_version_command -v 2>&1
      2. Check exit code is NON-ZERO (test fails - expected in TDD RED)
      3. Check output contains "ModuleNotFoundError" or "ImportError"
    Expected Result: Exit code 1 or 2, test fails due to missing cli module
    Failure Indicators: Exit code 0 (test passes - means cli.py already exists, wrong!)
    Evidence: .sisyphus/evidence/task-3-tdd-red-fail.txt
  ```

  **Evidence to Capture**:
  - [x] Test file existence verification
  - [x] TDD RED phase failure output (expected failure)

  **Commit**: YES (groups with 4)
  - Message: `test(cli): add version command TDD test`
  - Files: `tests/test_cli.py`
  - Pre-commit: `python -m pytest tests/test_cli.py -v` (expected: FAIL)

- [x] 4. Implement CLI Module (TDD GREEN Phase)

  **What to do**:
  - Create `src/madousho/cli.py` with Typer app instance
  - Implement `version` command that outputs version string
  - Add fallback handling for missing `_version.py` (return "0.0.0.dev0")
  - Use try/except for version import (handle PyPI install without git)
  - Verify test PASSES after implementation (TDD GREEN)

  **Must NOT do**:
  - Do NOT add additional subcommands beyond `version`
  - Do NOT add flags to version command (--short, --long)
  - Do NOT customize --help text
  - Do NOT add complex error handling

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: Implementing Typer CLI requires understanding framework patterns
  - **Skills**: []
    - Standard Typer CLI implementation

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Wave 2)
  - **Blocks**: Task 5
  - **Blocked By**: Task 3 (test must exist first for TDD)

  **References**:
  - `src/madousho/_version.py` - Version file generated by setuptools_scm
  - `src/madousho/__init__.py` - Module structure to follow
  - `https://typer.tiangolo.com/tutorial/` - Typer basics
  - Pattern: Typer multi-command app structure

  **Acceptance Criteria**:
  - [x] `src/madousho/cli.py` exists with Typer app
  - [x] `@app.command()` decorator for version function
  - [x] Version import with try/except fallback
  - [x] `python -m pytest tests/test_cli.py -v` PASSES (exit code 0)

  **QA Scenarios**:

  ```
  Scenario: TDD GREEN phase - test should pass
    Tool: Bash
    Preconditions: cli.py implemented
    Steps:
      1. Run: python -m pytest tests/test_cli.py -v
      2. Check exit code is 0
      3. Check output shows "1 passed"
    Expected Result: Exit code 0, all tests pass
    Failure Indicators: Exit code 1 (test still fails - implementation wrong)
    Evidence: .sisyphus/evidence/task-4-tdd-green-pass.txt

  Scenario: CLI module direct invocation
    Tool: Bash
    Preconditions: cli.py exists
    Steps:
      1. Run: python -m madousho.cli version
      2. Check exit code is 0
      3. Check output is non-empty string matching version pattern
    Expected Result: Exit code 0, output like "0.0.1.dev2" or "0.0.0.dev0"
    Failure Indicators: Exit code 1, ImportError, or empty output
    Evidence: .sisyphus/evidence/task-4-cli-direct.txt
  ```

  **Evidence to Capture**:
  - [x] pytest output showing test passes
  - [x] Direct CLI invocation output

  **Commit**: YES (groups with 3)
  - Message: `feat(cli): implement Typer CLI with version command`
  - Files: `src/madousho/cli.py`, `tests/test_cli.py`
  - Pre-commit: `python -m pytest tests/test_cli.py -v`

- [x] 5. Verify Entry Point Works

  **What to do**:
  - Run `pip install -e .` to install package in editable mode
  - Test `madousho version` command via entry point
  - Test `madousho --help` shows version subcommand
  - Verify both commands work correctly

  **Must NOT do**:
  - Do NOT modify any code (implementation complete)
  - Do NOT add new features during verification
  - Do NOT skip evidence capture

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Verification only, no implementation
  - **Skills**: []
    - Standard bash verification

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Wave 3)
  - **Blocks**: None (final verification)
  - **Blocked By**: Task 4 (CLI must be implemented)

  **References**:
  - `pyproject.toml:53-53` - Entry point configuration `madousho = "madousho.cli:app"`
  - Pattern: Standard pip editable install

  **Acceptance Criteria**:
  - [x] `pip install -e .` completes successfully
  - [x] `madousho version` outputs version string
  - [x] `madousho --help` shows "version" in subcommands list

  **QA Scenarios**:

  ```
  Scenario: Entry point installation
    Tool: Bash
    Preconditions: Task 4 complete, in activated venv
    Steps:
      1. Run: pip install -e . 2>&1
      2. Check exit code is 0
      3. Check output contains "Successfully installed"
    Expected Result: Exit code 0, package installed
    Failure Indicators: Exit code 1, installation error
    Evidence: .sisyphus/evidence/task-5-pip-install.txt

  Scenario: Entry point version command
    Tool: Bash
    Preconditions: pip install -e . complete
    Steps:
      1. Run: madousho version
      2. Check exit code is 0
      3. Check output is non-empty version string
    Expected Result: Exit code 0, output like "0.0.1.dev2"
    Failure Indicators: Exit code 1, command not found, empty output
    Evidence: .sisyphus/evidence/task-5-entry-version.txt

  Scenario: Entry point help command
    Tool: Bash
    Preconditions: pip install -e . complete
    Steps:
      1. Run: madousho --help
      2. Check exit code is 0
      3. Check output contains "version" subcommand
    Expected Result: Exit code 0, help shows version command
    Failure Indicators: Exit code 1, "version" not in output
    Evidence: .sisyphus/evidence/task-5-entry-help.txt
  ```

  **Evidence to Capture**:
  - [x] pip install output
  - [x] madousho version output
  - [x] madousho --help output

  **Commit**: NO (verification only, no code changes)

---

## Final Verification Wave

## Final Verification Wave

- [x] F1. **Plan Compliance Audit** — `oracle`
- [x] F2. **Code Quality Review** — `unspecified-high`
- [x] F3. **Real Manual QA** — `unspecified-high`
- [x] F4. **Scope Fidelity Check** — `deep`

---

## Commit Strategy

- **1**: `build(deps): add typer>=0.9.0 dependency` — pyproject.toml
- **2**: `test(cli): create tests directory structure` — tests/__init__.py
- **3**: `test(cli): add version command TDD test` — tests/test_cli.py, npm test
- **4**: `feat(cli): implement Typer CLI with version command` — src/madousho/cli.py, npm test
- **5**: `chore(cli): verify entry point installation` — (verification only)

---

## Success Criteria

### Verification Commands
```bash
# Verify typer in dependencies
grep -q 'typer>=' pyproject.toml && echo "PASS: typer in dependencies"

# Run tests
python -m pytest tests/test_cli.py -v

# Test CLI directly
python -m madousho.cli version

# Test entry point (after pip install -e .)
madousho version
madousho --help
```

### Final Checklist
- [x] All "Must Have" present
- [x] All "Must NOT Have" absent
- [x] All tests pass (exit code 0)
- [x] Version command outputs non-empty string
- [x] Help shows version subcommand
