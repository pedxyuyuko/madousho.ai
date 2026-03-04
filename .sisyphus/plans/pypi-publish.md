# PyPI Publishing Setup for Madousho-ai

## TL;DR

> **Quick Summary**: Set up automated PyPI publishing for the madousho-ai package using GitHub Actions with Trusted Publisher (OIDC) authentication.
> 
> **Deliverables**:
> - Complete pyproject.toml with all PyPI-required metadata
> - GitHub Actions workflow file for automated publishing
> - PyPI Trusted Publisher configuration guide
> - Version management from single source (pyproject.toml)
> 
> **Estimated Effort**: Short
> **Parallel Execution**: NO - sequential (2 waves)
> **Critical Path**: Task 1 → Task 2 → Task 3

---

## Context

### Original Request
用户要在 PyPI 上注册 madousho 包，使用 GitHub Actions 自动发布（Trusted Publisher/OIDC 方式）。

### Interview Summary
**Key Discussions**:
- Package name: madousho → **madousho-ai** (PEP 8 best practice, matches GitHub repo madousho.ai)
- Author: pedxyuyuko <uuz@sakurauuz.moe> (confirmed)
- CLI entry point: madousho = "madousho.cli:app"
- Package structure: src/madousho/ (correct src-layout)
- User has PyPI account, repository is on GitHub
- Chose GitHub Actions auto-publishing with Trusted Publisher (OIDC) - no long-lived API tokens needed

**Research Findings**:
- pyproject.toml missing required PyPI metadata fields
- Version defined in both pyproject.toml and __init__.py (currently in sync at 0.1.0)
- Python requirement >=3.14 (need to verify this is realistic)
- Best practice: use Trusted Publisher (OIDC) instead of API tokens

### Metis Review
**Identified Gaps** (addressed in plan):
- **Author info**: Confirmed - pedxyuyuko <uuz@sakurauuz.moe>
- **Description**: Will expand based on architecture.md content
- **Classifiers**: Will auto-recommend based on project characteristics
- **Version strategy**: Manual updates for now (semantic versioning)
- **Test publish**: Will include test.pypi.org publishing step
- **Python 3.14**: Will keep as-is (user's choice, 3.14 expected by 2026)
### User Decisions (Confirmed)
- **PyPI Package Name**: `madousho-ai` (changed from `madousho`, PEP 8 best practice)
- **Author**: pedxyuyuko <uuz@sakurauuz.moe> (confirmed)
- **Description**: Expand based on architecture.md content
- **Classifiers**: Auto-recommended (see Task 1)

### Metis Review
---

## Work Objectives

### Core Objective
Configure the madousho-ai package for automated PyPI publishing with proper metadata, GitHub Actions workflow, and Trusted Publisher (OIDC) authentication.

### Concrete Deliverables
- Updated `pyproject.toml` with complete PyPI metadata
- New `.github/workflows/pypi-publish.yml` workflow file
- Updated `README.md` with PyPI-ready description
- PyPI Trusted Publisher configuration completed by user

### Definition of Done
- [x] `python -m build` succeeds locally
- [x] GitHub Actions workflow validates on push
- [x] Test publish to test.pypi.org succeeds
- [x] Production publish to pypi.org succeeds on tag creation

### Must Have
- Trusted Publisher (OIDC) authentication - no API tokens
- Semantic versioning (manual updates to pyproject.toml)
- Complete PyPI metadata (authors, license, classifiers, readme)
- GitHub Actions workflow triggers on GitHub Release

### Must NOT Have (Guardrails)
- **NO** long-lived PyPI API tokens in GitHub Secrets
- **NO** package restructuring (keep src/madousho/)
- **NO** new dependencies beyond build tools
- **NO** code refactoring beyond publishing requirements
- **NO** comprehensive test suite addition (out of scope)

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (no test infrastructure detected)
- **Automated tests**: NO (out of scope for publishing setup)
- **Framework**: N/A
- **Agent-Executed QA**: ALWAYS (mandatory for all tasks)

### QA Policy
Every task MUST include agent-executed QA scenarios:
- **Build verification**: Run `python -m build` and verify artifacts
- **Metadata validation**: Use `twine check` to validate package metadata
- **Workflow validation**: Verify YAML syntax and GitHub Actions compliance

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - metadata + build config):
├── Task 1: Complete pyproject.toml metadata [quick]
├── Task 2: Update README.md with PyPI-ready description [quick]
└── Task 3: Verify build configuration [quick]

Wave 2 (After Wave 1 - GitHub Actions workflow):
├── Task 4: Create GitHub Actions publish workflow [quick]
├── Task 5: Create test.pypi.org workflow [quick]
└── Task 6: Document PyPI Trusted Publisher setup [quick]

Wave FINAL (After ALL tasks - verification):
├── Task F1: Build verification [quick]
├── Task F2: Metadata validation [quick]
└── Task F3: Workflow syntax check [quick]

Critical Path: Task 1 → Task 4 → F1
Parallel Speedup: ~50% faster than sequential
Max Concurrent: 3 (Waves 1 & 2)
```

### Dependency Matrix

- **1-3**: — — 4-6, F1
- **4-6**: 1-3 — F2, F3
- **F1-F3**: All tasks — Complete

### Agent Dispatch Summary

- **Wave 1**: **3** — T1 → `quick`, T2 → `quick`, T3 → `quick`
- **Wave 2**: **3** — T4 → `quick`, T5 → `quick`, T6 → `quick`
- **FINAL**: **3** — F1 → `quick`, F2 → `quick`, F3 → `quick`

---

## TODOs

- [x] 1. Complete pyproject.toml with PyPI metadata

  **User Decisions**:
  - **PyPI Package Name**: `madousho-ai` (PEP 8 best practice)
  - **Author**: pedxyuyuko (email needed)
  - **Description**: Expand based on architecture.md
  - **Classifiers**: Auto-recommended below

  **What to do**:
  - Update `name` field to `madousho-ai`
  - Add `authors` field: `[{name = "pedxyuyuko", email = "USER_EMAIL_HERE"}]`
  - Add `maintainers` field (can be same as authors)
  - Add `license` field: `{text = "MIT"}`
  - Add `readme` field: `{file = "README.md", content-type = "text/markdown"}`
  - Add `classifiers` array (recommended below)
  - Add `urls` section: Homepage, Repository, Bug Tracker
  - Expand `description` based on architecture.md



  **Must NOT do**:
  - Do NOT change package structure
  - Do NOT add unnecessary dependencies
  - Do NOT change Python version requirement without user confirmation

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Straightforward metadata addition, no complex logic
  - **Skills**: []
    - No specialized skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Tasks 4, 5, F1, F2
  - **Blocked By**: None (can start immediately)

  **References**:
  **References**:
  - `pyproject.toml:1-25` - Current minimal metadata that needs expansion
  - `.sisyphus/plans/madousho-architecture.md:1-50` - Project overview for description
  - Official docs: `https://packaging.python.org/en/latest/specifications/declaring-project-metadata/` - PyPI metadata specification
  - Official docs: `https://pypi.org/classifiers/` - Available PyPI classifiers

  **Recommended Classifiers** (based on project):
  ```
  "Development Status :: 3 - Alpha",
  "Intended Audience :: Developers",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.14",
  "Topic :: Scientific/Engineering :: Artificial Intelligence",
  "Topic :: Software Development :: Libraries :: Python Modules",
  ```
  - Official docs: `https://packaging.python.org/en/latest/specifications/declaring-project-metadata/` - PyPI metadata specification
  - Official docs: `https://pypi.org/classifiers/` - Available PyPI classifiers

  **WHY Each Reference Matters**:
  - Current pyproject.toml shows what fields are missing
  - Packaging guide provides the exact format for each metadata field
  - Classifier list helps choose appropriate categories

  **Acceptance Criteria**:
  - [x] pyproject.toml contains: authors, maintainers, license, readme, classifiers, urls
  - [x] `python -m build` succeeds without errors
  - [x] `twine check dist/*` passes metadata validation

  **QA Scenarios**:

  ```
  Scenario: Build package successfully
    Tool: Bash
    Preconditions: In project root directory
    Steps:
      1. Run: python -m build
      2. Verify: dist/ directory contains .tar.gz and .whl files
      3. Verify: Exit code is 0
    Expected Result: Build completes with 2 artifacts in dist/
    Failure Indicators: Build error, missing artifacts, non-zero exit code
    Evidence: .sisyphus/evidence/task-1-build-output.txt

  Scenario: Validate PyPI metadata
    Tool: Bash
    Preconditions: dist/ directory contains built artifacts
    Steps:
      1. Run: twine check dist/*
      2. Verify: Output contains "PASSED"
      3. Verify: Exit code is 0
    Expected Result: twine check reports PASSED
    Failure Indicators: Metadata warnings/errors, non-zero exit code
    Evidence: .sisyphus/evidence/task-1-twine-check.txt
  ```

  **Commit**: YES (groups with 2, 3)
  - Message: `chore(packaging): add PyPI metadata to pyproject.toml`
  - Files: `pyproject.toml`
  - Pre-commit: `python -m build && twine check dist/*`

- [x] 2. Update README.md for PyPI

  **What to do**:
  - Expand description beyond "Systematic Agent I guess"
  - Add installation instructions (pip install madousho)
  - Add basic usage examples
  - Add CLI commands documentation
  - Ensure README is PyPI-ready (renders correctly on PyPI page)
  - Use long_description_content_type: "text/markdown" in pyproject.toml

  **Must NOT do**:
  - Do NOT completely rewrite README
  - Do NOT add extensive documentation (out of scope)
  - Do NOT change README format (keep Markdown)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Documentation update, straightforward expansion
  - **Skills**: []
    - No specialized skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: None
  - **Blocked By**: None (can start immediately)

  **References**:
  - `README.md:1-15` - Current minimal README
  - `pyproject.toml:5-13` - Project description and dependencies
  - `.sisyphus/plans/madousho-architecture.md:286-294` - CLI commands list

  **WHY Each Reference Matters**:
  - Current README shows what needs expansion
  - pyproject.toml provides project context for description
  - Architecture doc has CLI commands to document

  **Acceptance Criteria**:
  - [x] README.md contains: description, installation, usage, CLI commands
  - [x] README renders correctly on PyPI (valid Markdown)
  - [x] pyproject.toml has `readme = "README.md"` field

  **QA Scenarios**:

  ```
  Scenario: Validate README Markdown syntax
    Tool: Bash
    Preconditions: README.md updated
    Steps:
      1. Run: pip install readme-renderer
      2. Run: python -m readme_renderer README.md -o /dev/null
      3. Verify: Exit code is 0 (no rendering errors)
    Expected Result: README renders without errors
    Failure Indicators: Markdown syntax errors, rendering failures
    Evidence: .sisyphus/evidence/task-2-readme-render.txt
  ```

  **Commit**: YES (groups with 1, 3)
  - Message: `chore(packaging): add PyPI metadata to pyproject.toml`
  - Files: `pyproject.toml`
  - Pre-commit: `python -m build && twine check dist/*`

- [x] 3. Verify build configuration

  **What to do**:
  - Ensure build-system is correctly configured
  - Verify setuptools can find packages in src/ layout
  - Test local build produces correct artifacts
  - Verify package can be installed from local wheel

  **Must NOT do**:
  - Do NOT change build backend unless necessary
  - Do NOT restructure package directories

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Build verification is straightforward
  - **Skills**: []
    - No specialized skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: Tasks 4, 5, F1
  - **Blocked By**: None (can start immediately)

  **References**:
  - `pyproject.toml:1-3` - Current build-system configuration
  - `src/madousho/` - Package source directory structure

  **WHY Each Reference Matters**:
  - Build-system config must match the build backend
  - Package structure affects how setuptools discovers packages

  **Acceptance Criteria**:
  - [x] `python -m build` produces .tar.gz and .whl in dist/
  - [x] `pip install dist/*.whl` succeeds
  - [x] `madousho --help` works after installation

  **QA Scenarios**:

  ```
  Scenario: Build and install package locally
    Tool: Bash
    Preconditions: pyproject.toml updated
    Steps:
      1. Run: python -m build
      2. Run: pip install dist/madousho-*.whl
      3. Run: madousho --help
      4. Verify: CLI help output appears
    Expected Result: Package installs and CLI is accessible
    Failure Indicators: Build fails, install fails, CLI not found
    Evidence: .sisyphus/evidence/task-3-install-test.txt
  ```

  **Commit**: YES (groups with 1, 2)
  - Message: `chore(packaging): add PyPI metadata to pyproject.toml`
  - Files: `pyproject.toml`
  - Pre-commit: `python -m build && twine check dist/*`

- [x] 4. Create GitHub Actions PyPI publish workflow

  **What to do**:
  - Create `.github/workflows/pypi-publish.yml`
  - Configure workflow to trigger on GitHub Release
  - Use Trusted Publisher (OIDC) for PyPI authentication
  - Build package and publish to pypi.org
  - Include permissions for OIDC token generation

  **Must NOT do**:
  - Do NOT use PYPI_API_TOKEN secret (use OIDC instead)
  - Do NOT trigger on every push (only on releases)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Standard workflow template, well-documented pattern
  - **Skills**: []
    - No specialized skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 6)
  - **Blocks**: F2, F3
  - **Blocked By**: Task 1 (pyproject.toml must be complete)

  **References**:
  - Official docs: `https://docs.pypi.org/trusted-publishers/` - PyPI Trusted Publishers guide
  - Official docs: `https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect` - GitHub OIDC guide
  - Example: `https://github.com/astral-sh/ruff/blob/main/.github/workflows/publish.yml` - Real-world example

  **WHY Each Reference Matters**:
  - PyPI docs explain Trusted Publisher setup steps
  - GitHub docs explain OIDC configuration
  - Example shows production-ready workflow pattern

  **Acceptance Criteria**:
  - [x] Workflow file created at `.github/workflows/pypi-publish.yml`
  - [x] Workflow triggers on release published
  - [x] Uses `pypa/gh-action-pypi-publish@release/v1` with Trusted Publisher
  - [x] Includes `permissions: id-token: write` for OIDC
  - [x] Workflow YAML passes syntax validation

  **QA Scenarios**:

  ```
  Scenario: Validate workflow YAML syntax
    Tool: Bash
    Preconditions: Workflow file created
    Steps:
      1. Run: pip install yamllint
      2. Run: yamllint .github/workflows/pypi-publish.yml
      3. Verify: No syntax errors
    Expected Result: YAML is valid
    Failure Indicators: Syntax errors, indentation issues
    Evidence: .sisyphus/evidence/task-4-yamllint.txt

  Scenario: Verify workflow permissions
    Tool: Bash
    Preconditions: Workflow file exists
    Steps:
      1. Run: grep -A5 "permissions:" .github/workflows/pypi-publish.yml
      2. Verify: Contains "id-token: write"
      3. Verify: Contains "contents: read"
    Expected Result: Correct OIDC permissions present
    Failure Indicators: Missing id-token permission, overly broad permissions
    Evidence: .sisyphus/evidence/task-4-permissions-check.txt
  ```

  **Commit**: YES (groups with 5, 6)
  - Message: `ci(packaging): add GitHub Actions PyPI publish workflow`
  - Files: `.github/workflows/pypi-publish.yml`
  - Pre-commit: `yamllint .github/workflows/pypi-publish.yml`

- [x] 5. Create test.pypi.org publish workflow

  **What to do**:
  - Create `.github/workflows/pypi-test-publish.yml`
  - Configure workflow to trigger on push to main branch
  - Use Trusted Publisher for test.pypi.org
  - Build package and publish to test.pypi.org
  - This allows testing before production release

  **Must NOT do**:
  - Do NOT publish to pypi.org from test workflow
  - Do NOT use same Trusted Publisher as production

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Similar to Task 4, just different target
  - **Skills**: []
    - No specialized skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4, 6)
  - **Blocks**: None
  - **Blocked By**: Task 1 (pyproject.toml must be complete)

  **References**:
  - Official docs: `https://docs.pypi.org/trusted-publishers/using-a-publisher/` - Test PyPI setup
  - Task 4 workflow - Similar structure, different configuration

  **WHY Each Reference Matters**:
  - Test PyPI uses same Trusted Publisher mechanism
  - Can reuse production workflow structure

  **Acceptance Criteria**:
  - [x] Workflow file created at `.github/workflows/pypi-test-publish.yml`
  - [x] Workflow triggers on push to main branch
  - [x] Publishes to test.pypi.org (not pypi.org)
  - [x] Uses Trusted Publisher with correct repository URL

  **QA Scenarios**:

  ```
  Scenario: Verify test PyPI target
    Tool: Bash
    Preconditions: Test workflow file created
    Steps:
      1. Run: grep -A10 "pypi-publish" .github/workflows/pypi-test-publish.yml
      2. Verify: Contains "--repository-url https://test.pypi.org/legacy/"
      3. Verify: Does NOT contain pypi.org (production)
    Expected Result: Correctly targets test.pypi.org
    Failure Indicators: Wrong repository URL, missing repository-url flag
    Evidence: .sisyphus/evidence/task-5-test-target-check.txt
  ```

  **Commit**: YES (groups with 4, 6)
  - Message: `ci(packaging): add GitHub Actions PyPI publish workflow`
  - Files: `.github/workflows/pypi-test-publish.yml`
  - Pre-commit: `yamllint .github/workflows/pypi-test-publish.yml`

- [x] 6. Document PyPI Trusted Publisher setup

  **What to do**:
  - Create setup guide for PyPI Trusted Publisher configuration
  - Document steps to add GitHub as Trusted Publisher on PyPI
  - Document steps to add PyPI as Trusted Publisher on GitHub (if needed)
  - Include verification steps
  - Save as `.sisyphus/PYPI_SETUP.md` or add to README

  **Must NOT do**:
  - Do NOT skip verification steps
  - Do NOT assume user knows PyPI interface

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Documentation task, straightforward instructions
  - **Skills**: []
    - No specialized skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4, 5)
  - **Blocks**: None
  - **Blocked By**: None (can start immediately)

  **References**:
  - Official docs: `https://docs.pypi.org/trusted-publishers/adding-a-publisher/` - Step-by-step guide
  - Task 4, 5 workflows - Reference what needs to be configured

  **WHY Each Reference Matters**:
  - Official PyPI docs have exact UI steps
  - Workflows show what OIDC configuration is needed

  **Acceptance Criteria**:
  - [x] Documentation created with step-by-step instructions
  - [x] Includes PyPI Trusted Publisher addition steps
  - [x] Includes GitHub repository verification steps
  - [x] Includes test publish verification steps

  **QA Scenarios**:

  ```
  Scenario: Verify documentation completeness
    Tool: Bash
    Preconditions: Documentation file created
    Steps:
      1. Read documentation file
      2. Verify: Contains "Add trusted publisher" steps
      3. Verify: Contains "test.pypi.org" setup
      4. Verify: Contains "pypi.org" production setup
    Expected Result: All required sections present
    Failure Indicators: Missing setup steps, unclear instructions
    Evidence: .sisyphus/evidence/task-6-doc-check.txt
  ```

  **Commit**: YES (groups with 4, 5)
  - Message: `ci(packaging): add GitHub Actions PyPI publish workflow`
  - Files: `.github/workflows/pypi-test-publish.yml`
  - Pre-commit: `yamllint .github/workflows/pypi-test-publish.yml`

---

## Final Verification Wave

> 3 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [x] F1. **Build Verification** — `quick`
  Run `python -m build` from clean state. Verify dist/ contains both .tar.gz and .whl. Install from wheel and test CLI. Check no build warnings.
  Output: `Build [PASS/FAIL] | Artifacts [N/N] | Install [PASS/FAIL] | CLI [WORKS/FAILS] | VERDICT: APPROVE/REJECT`

- [x] F2. **Metadata Validation** — `quick`
  Run `twine check dist/*`. Verify all required PyPI metadata fields present. Check classifiers are valid. Verify README renders correctly.
  Output: `Twine [PASS/FAIL] | Metadata [COMPLETE/INCOMPLETE] | README [VALID/INVALID] | VERDICT`

- [x] F3. **Workflow Syntax Check** — `quick`
  Validate both workflow files with yamllint. Verify OIDC permissions present. Check trigger conditions correct. Verify action versions are pinned.
  Output: `YAML [VALID/INVALID] | Permissions [CORRECT/INCORRECT] | Triggers [CORRECT/INCORRECT] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `chore(packaging): add PyPI metadata to pyproject.toml` — pyproject.toml, README.md
- **Wave 2**: `ci(packaging): add GitHub Actions PyPI publish workflow` — .github/workflows/pypi-publish.yml, .github/workflows/pypi-test-publish.yml, .sisyphus/PYPI_SETUP.md

---

## Success Criteria

### Verification Commands
```bash
python -m build                    # Expected: dist/ contains .tar.gz and .whl
twine check dist/*                 # Expected: PASSED
pip install dist/*.whl             # Expected: Successfully installed
madousho --help                    # Expected: CLI help output
yamllint .github/workflows/*.yml   # Expected: No errors
```

### Final Checklist
- [x] All "Must Have" present (metadata, workflows, documentation)
- [x] All "Must NOT Have" absent (no API tokens, no restructuring)
- [x] Build succeeds locally
- [x] Twine check passes
- [x] Workflows are syntactically valid
- [x] PyPI Trusted Publisher setup documented
