# Fix Config Test Failures - Missing default_model_group Field

## TL;DR

> **Quick Summary**: Fix 15 failing tests by adding the required `default_model_group` field to all Config instances in test files.
> 
> **Deliverables**: 
> - Updated tests/config/test_models.py with default_model_group in all Config creations
> - Updated tests/config/test_integration.py with default_model_group in all Config creations
> - All 15 previously failing tests now pass
> 
> **Estimated Effort**: Short (single file edits, same pattern repeated)
> **Parallel Execution**: NO - sequential (same files, related changes)
> **Critical Path**: Edit test_models.py → Edit test_integration.py → Run tests

---

## Context

### Original Request
User reported 15 test failures in config tests with validation errors.

### Interview Summary
**Key Findings**:
- Config model requires `default_model_group: str` field (src/madousho/config/models.py:40)
- Tests create Config instances without this required field
- Example config shows correct usage: `default_model_group: "example_group"` (config/madousho.example.yaml:17)
- Error: `Field required [type=missing, input_value={...}]`

### Root Cause
Tests were written before `default_model_group` was added as a required field, or the field was added without updating tests.

---

## Work Objectives

### Core Objective
Update all test files to include the required `default_model_group` field when creating Config instances.

### Concrete Deliverables
- tests/config/test_models.py: 4 test methods updated
- tests/config/test_integration.py: 8 test methods updated
- All 15 config tests passing

### Definition of Done
- `python -m pytest tests/config/` passes with 0 failures
- No new test failures introduced

### Must Have
- Every Config instantiation includes `default_model_group`
- The value references an existing key in `model_groups`

### Must NOT Have (Guardrails)
- DO NOT change the Config model structure
- DO NOT make default_model_group optional
- DO NOT modify tests unrelated to Config creation

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: YES (pytest)
- **Automated tests**: Tests already exist, just fixing them
- **Framework**: pytest
- **Verification**: Run pytest on config test files

### QA Policy
Every task MUST include agent-executed QA scenarios.

- **Test verification**: Use Bash (pytest) — Run test commands, assert exit code 0, check output

---

## Execution Strategy

### Sequential Execution

```
Wave 1 (Fix test_models.py):
└── Task 1: Update test_models.py Config instantiations [quick]

Wave 2 (Fix test_integration.py):
└── Task 2: Update test_integration.py Config instantiations [quick]

Wave 3 (Verification):
└── Task 3: Run all config tests and verify pass [quick]
```

### Dependency Matrix
- **1**: — → 2
- **2**: 1 → 3
- **3**: 2 → Final

---

## TODOs

- [x] 1. Update test_models.py - Add default_model_group to all Config instances

  **What to do**:
  - Read tests/config/test_models.py
  - Find all Config(...) instantiations
  - Add `default_model_group` parameter with a value that references an existing model_groups key
  - Affected tests:
    - test_valid_config (line ~116)
    - test_config_multiple_providers (line ~137)
    - test_config_empty_provider_dict (line ~183)
    - test_config_dict_conversion (line ~240)
  
  **Must NOT do**:
  - Do not change Config model definition
  - Do not modify other test assertions
  - Do not add new tests

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple, repetitive pattern addition across multiple locations in one file
  - **Skills**: [`git-master`]
    - `git-master`: For atomic commits after changes

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (first file to edit)
  - **Blocks**: Task 2, 3
  - **Blocked By**: None

  **References**:
  - `src/madousho/config/models.py:33-41` - Config model definition showing required fields
  - `config/madousho.example.yaml:17-20` - Example of correct default_model_group usage

  **Acceptance Criteria**:
  - [ ] All Config instantiations in test_models.py include default_model_group
  - [ ] python -m pytest tests/config/test_models.py returns exit code 0

  **QA Scenarios**:

  ```
  Scenario: Run test_models.py and verify all tests pass
    Tool: Bash (pytest)
    Preconditions: In project root directory
    Steps:
      1. Run: python -m pytest tests/config/test_models.py -v
      2. Check exit code: echo $?
      3. Verify output contains "passed" and no "FAILED"
    Expected Result: Exit code 0, all tests pass
    Failure Indicators: Exit code non-zero, any FAILED in output
    Evidence: .sisyphus/evidence/task-1-test_models-pytest.txt
  ```

  **Commit**: YES
  - Message: `test(config): add default_model_group to Config instances in test_models.py`
  - Files: `tests/config/test_models.py`
  - Pre-commit: `python -m pytest tests/config/test_models.py`

---

- [x] 2. Update test_integration.py - Add default_model_group to all Config instances

  **What to do**:
  - Read tests/config/test_integration.py
  - Find all Config(...) instantiations and YAML configs missing default_model_group
  - Add `default_model_group` to Config calls and `default_model_group:` to YAML strings
  - Affected tests:
    - test_normalize_then_validate (line ~60) - YAML content
    - test_env_override_then_validate (line ~95) - YAML content
    - test_deep_merge_with_model_validation (line ~125) - dict literal
    - test_full_load_config_workflow (line ~161) - YAML content
    - test_hyphen_conversion_full_chain (line ~211) - YAML content
    - test_config_model_dump_roundtrip (line ~242) - YAML content
    - test_complete_config_lifecycle (line ~287) - YAML content
    - test_production_like_scenario (line ~373) - YAML content

  **Must NOT do**:
  - Do not change Config model definition
  - Do not modify other test logic
  - Do not add new tests

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Same pattern as Task 1, just different file
  - **Skills**: [`git-master`]
    - `git-master`: For atomic commits after changes

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (depends on Task 1)
  - **Blocks**: Task 3
  - **Blocked By**: Task 1

  **References**:
  - `src/madousho/config/models.py:33-41` - Config model definition
  - `config/madousho.example.yaml:17-20` - Example usage pattern
  - Task 1 output - Same pattern applied to test_models.py

  **Acceptance Criteria**:
  - [ ] All Config instantiations in test_integration.py include default_model_group
  - [ ] All YAML strings in tests include default_model_group key
  - [ ] python -m pytest tests/config/test_integration.py returns exit code 0

  **QA Scenarios**:

  ```
  Scenario: Run test_integration.py and verify all tests pass
    Tool: Bash (pytest)
    Preconditions: In project root directory
    Steps:
      1. Run: python -m pytest tests/config/test_integration.py -v
      2. Check exit code: echo $?
      3. Verify output contains "passed" and no "FAILED"
    Expected Result: Exit code 0, all tests pass
    Failure Indicators: Exit code non-zero, any FAILED in output
    Evidence: .sisyphus/evidence/task-2-test_integration-pytest.txt
  ```

  **Commit**: YES
  - Message: `test(config): add default_model_group to Config instances in test_integration.py`
  - Files: `tests/config/test_integration.py`
  - Pre-commit: `python -m pytest tests/config/test_integration.py`

---

- [x] 3. Run all config tests and verify complete fix

  **What to do**:
  - Run full config test suite
  - Verify all 15 previously failing tests now pass
  - Check for any new failures introduced

  **Must NOT do**:
  - Do not modify any code in this task
  - Do not skip failing tests

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple test execution and verification
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (final verification)
  - **Blocks**: Final verification wave
  - **Blocked By**: Task 1, 2

  **References**:
  - None needed

  **Acceptance Criteria**:
  - [ ] python -m pytest tests/config/ returns exit code 0
  - [ ] All tests in test_models.py pass
  - [ ] All tests in test_integration.py pass
  - [ ] No new test failures in other test files

  **QA Scenarios**:

  ```
  Scenario: Run full config test suite
    Tool: Bash (pytest)
    Preconditions: In project root directory, all fixes applied
    Steps:
      1. Run: python -m pytest tests/config/ -v
      2. Check exit code: echo $?
      3. Count passed tests in output
    Expected Result: Exit code 0, all config tests pass
    Failure Indicators: Exit code non-zero, any FAILED in output
    Evidence: .sisyphus/evidence/task-3-all-config-tests-pytest.txt
  ```

  **Commit**: NO (verification only)

---

## Final Verification Wave

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Verify all Config instantiations include default_model_group. Check evidence files exist.

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run pytest, check for any linting issues in modified test files.

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Execute all QA scenarios from tasks 1-3, capture evidence.

- [ ] F4. **Scope Fidelity Check** — `deep`
  Verify only config tests were modified, no unrelated changes.

---

## Commit Strategy

- **1**: `test(config): add default_model_group to Config instances in test_models.py` — tests/config/test_models.py
- **2**: `test(config): add default_model_group to Config instances in test_integration.py` — tests/config/test_integration.py
- **3**: NO commit (verification only)

---

## Success Criteria

### Verification Commands
```bash
python -m pytest tests/config/test_models.py -v  # Expected: all pass
python -m pytest tests/config/test_integration.py -v  # Expected: all pass
python -m pytest tests/config/ -v  # Expected: 0 failures
```

### Final Checklist
- [ ] All Config instantiations include default_model_group
- [ ] All YAML test configs include default_model_group key
- [ ] test_models.py passes (4 previously failing tests now pass)
- [ ] test_integration.py passes (8 previously failing tests now pass)
- [ ] No new test failures introduced
- [ ] Evidence files captured in .sisyphus/evidence/
