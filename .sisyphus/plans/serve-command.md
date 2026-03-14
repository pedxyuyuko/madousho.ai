# 实现 madousho serve CLI 命令

## TL;DR

> **Quick Summary**: 在现有 CLI 框架中添加 `serve` 子命令，作为未来 API 服务器的主入口。当前阶段仅实现配置加载和日志初始化。
> 
> **Deliverables**:
> - `src/madousho/cli.py` - 添加 `serve` 命令
> - `src/madousho/commands/serve.py` - serve 命令实现模块
> - `tests/test_serve_command.py` - 命令测试
> 
> **Estimated Effort**: Quick (单任务，<30 分钟)
> **Parallel Execution**: NO - 单一任务
> **Critical Path**: Task 1

---

## Context

### Original Request
用户要求创建 `madousho serve` CLI 命令作为程序主入口，未来会作为 API 服务器运行。当前阶段只需要：
1. 加载配置
2. 初始化 logger

### Interview Summary
**技术栈确认**：
- **CLI 框架**: Typer (已在 pyproject.toml 中配置)
- **配置系统**: Pydantic + YAML (已完成)
- **日志系统**: Loguru (已完成)

**现有代码**：
- `cli.py` 已有基础 Typer app 结构和 `version` 命令
- `config/loader.py` 提供 `init_config()` 和 `get_config()` 
- `logging/config.py` 提供 `configure_logging()`
- `logging/__init__.py` 导出 `get_logger` 和 `configure_logging`

### Metis Review
**识别的潜在问题**（已解决）：
- **配置加载时机**: `config/loader.py` 中的 `config` 全局变量会在模块导入时自动加载配置，可能导致重复初始化 → **解决**: serve 命令应显式调用 `init_config()` 确保可控
- **日志重复初始化**: Loguru 的 `configure_logging()` 应只调用一次 → **解决**: serve 命令负责调用，避免在模块导入时自动配置

---

## Work Objectives

### Core Objective
实现 `madousho serve` CLI 命令，完成配置加载和日志初始化，为未来 API 服务器提供主入口。

### Concrete Deliverables
- `src/madousho/commands/serve.py` - serve 命令实现
- `src/madousho/cli.py` - 注册 serve 命令
- `tests/test_serve_command.py` - 测试用例

### Definition of Done
- [x] `madousho serve --help` 显示帮助信息
- [x] `madousho serve` 成功执行，无报错
- [x] 配置文件正确加载
- [x] 日志系统正确初始化
- [x] 测试通过

### Must Have
- [x] 使用 Typer 框架实现
- [x] 调用 `config.loader.init_config()` 加载配置
- [x] 调用 `logging.config.configure_logging()` 初始化日志
- [x] 添加成功启动的日志输出

### Must NOT Have (Guardrails)
- [x] **不要**实现 API 服务器逻辑（未来任务）
- [x] **不要**添加额外的命令行参数（当前不需要）
- [x] **不要**修改现有配置加载器或日志配置模块
- [x] **不要**在模块导入时自动初始化配置或日志

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: YES (TDD)
- **Framework**: pytest (已在 pyproject.toml 配置)
- **测试策略**: 使用 `typer.testing.CliRunner` 测试 CLI 命令

### QA Policy
**Agent-Executed QA**:
- **CLI 命令**: 使用 `interactive_bash` 运行命令，验证输出和退出码
- **测试**: 使用 `Bash` 运行 `pytest tests/test_serve_command.py -v`

---

## Execution Strategy

### Sequential Execution (单一任务)

```
Wave 1:
└── Task 1: 实现 serve 命令 + 测试 [quick]
```

### Agent Dispatch Summary
- **1**: **1** — T1 → `quick`

---

## TODOs

- [x] 1. 实现 madousho serve 命令

  **What to do**:
  1. 创建 `src/madousho/commands/` 目录（如不存在）
  2. 创建 `src/madousho/commands/__init__.py`（空文件）
  3. 创建 `src/madousho/commands/serve.py` 实现 serve 命令：
     - 导入 `typer`, `config.loader`, `logging.config`
     - 创建 `serve()` 函数，使用 `@app.command()` 装饰
     - 函数体内：
       - 调用 `init_config()` 加载配置
       - 调用 `configure_logging()` 初始化日志
       - 获取 logger 并输出 "Server starting..." 信息
       - 输出 "Configuration loaded from: {config_path}"
       - 输出 "Madousho serve is ready (API server not yet implemented)"
  4. 修改 `src/madousho/cli.py`：
     - 导入 `serve` 命令
     - 将 `serve` 注册到 `app`
  5. 创建 `tests/test_serve_command.py`：
     - 测试 `serve --help` 显示帮助
     - 测试 `serve` 命令执行成功（exit_code == 0）
     - 测试输出包含预期信息

  **Must NOT do**:
  - 不要实现 API 服务器逻辑
  - 不要添加额外的命令行参数
  - 不要修改 config/loader.py 或 logging/config.py

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 单一任务，范围明确，代码量小（<100 行）
  - **Skills**: `[]`
    - Reason: 不需要特殊技能，标准 Python + Typer 实现

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (唯一任务)
  - **Blocks**: None
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `src/madousho/cli.py:21-25` - 现有 `version` 命令的 Typer 实现模式
  - `tests/test_cli.py:8-12` - CLI 命令的 pytest 测试模式

  **API/Type References**:
  - `src/madousho/config/loader.py:85-98` - `init_config()` 函数签名和行为
  - `src/madousho/logging/config.py:23-80` - `configure_logging()` 函数签名和行为

  **External References**:
  - Typer docs: `https://typer.tiangolo.com/tutorial/commands/` - 命令装饰器模式

  **WHY Each Reference Matters**:
  - `cli.py:21-25` - 展示如何定义 Typer 命令和 docstring（作为 help 文本）
  - `test_cli.py:8-12` - 展示如何使用 `CliRunner.invoke()` 测试命令
  - `config/loader.py:85-98` - 明确配置加载的返回值和异常行为
  - `logging/config.py:23-80` - 明确日志配置的参数和副作用

  **Acceptance Criteria**:

  **测试文件创建**:
  - [x] `tests/test_serve_command.py` 创建
  - [x] `src/madousho/commands/__init__.py` 创建
  - [x] `src/madousho/commands/serve.py` 创建

  **测试通过**:
  - [x] `pytest tests/test_serve_command.py -v` → PASS (2 测试，0 失败)
  - [x] `pytest tests/ -v` → PASS (包含现有测试)

  **QA Scenarios**:

  ```
  Scenario: serve --help 显示帮助信息
    Tool: interactive_bash
    Preconditions: 项目已安装 (pip install -e .)
    Steps:
      1. 运行：madousho serve --help
      2. 验证输出包含："Madousho.ai API server"
      3. 验证退出码为 0
    Expected Result: 帮助文本正确显示，退出码 0
    Failure Indicators: 命令不存在、帮助文本缺失、退出码非 0
    Evidence: .sisyphus/evidence/task-1-serve-help.txt

  Scenario: serve 命令成功执行
    Tool: interactive_bash
    Preconditions: 配置文件 config/madousho.yaml 存在
    Steps:
      1. 运行：madousho serve
      2. 验证输出包含："Server starting..."
      3. 验证输出包含："Configuration loaded from:"
      4. 验证输出包含："Madousho serve is ready"
      5. 验证退出码为 0
    Expected Result: 命令执行成功，输出预期日志信息
    Failure Indicators: 报错、配置加载失败、输出缺失
    Evidence: .sisyphus/evidence/task-1-serve-execution.txt

  Scenario: serve 命令在缺失配置文件时报错
    Tool: interactive_bash
    Preconditions: 临时移动配置文件
    Steps:
      1. 运行：mv config/madousho.yaml config/madousho.yaml.bak
      2. 运行：madousho serve
      3. 验证输出包含错误信息
      4. 验证退出码非 0
      5. 运行：mv config/madousho.yaml.bak config/madousho.yaml
    Expected Result: 命令优雅失败，提示配置文件缺失
    Failure Indicators: 崩溃无提示、退出码为 0
    Evidence: .sisyphus/evidence/task-1-serve-missing-config.txt
  ```

  **Evidence to Capture**:
  - [x] `.sisyphus/evidence/task-1-serve-help.txt` - help 输出
  - [x] `.sisyphus/evidence/task-1-serve-execution.txt` - 执行输出
  - [x] `.sisyphus/evidence/task-1-serve-missing-config.txt` - 错误输出

  **Commit**: YES
  - Message: `feat(cli): add serve command as API server entry point`
  - Files: `src/madousho/commands/serve.py`, `src/madousho/commands/__init__.py`, `src/madousho/cli.py`, `tests/test_serve_command.py`
  - Pre-commit: `pytest tests/test_serve_command.py -v && pytest tests/ -v`

---

## Final Verification Wave

- [x] F1. **Plan Compliance Audit** — `oracle`
  验证 `serve` 命令存在、配置加载调用、日志初始化调用、测试文件存在。

- [x] F2. **Code Quality Review** — `unspecified-high`
  运行 `pytest` 验证测试通过，检查代码风格。

- [x] F3. **Real Manual QA** — `unspecified-high`
  执行所有 QA 场景，验证输出和退出码。

- [x] F4. **Scope Fidelity Check** — `deep`
  验证没有实现 API 服务器逻辑，没有添加额外参数。

---

## Commit Strategy

- **1**: `feat(cli): add serve command as API server entry point`
  - Files: `src/madousho/commands/serve.py`, `src/madousho/commands/__init__.py`, `src/madousho/cli.py`, `tests/test_serve_command.py`
  - Pre-commit: `pytest tests/test_serve_command.py -v && pytest tests/ -v`

---

## Success Criteria

### Verification Commands
```bash
madousho serve --help  # Expected: 显示帮助信息，退出码 0
madousho serve         # Expected: 输出启动日志，退出码 0
pytest tests/test_serve_command.py -v  # Expected: 2 测试全部通过
```

### Final Checklist
- [x] `serve` 命令可执行
- [x] 配置正确加载
- [x] 日志正确初始化
- [x] 测试通过
- [x] 没有实现 API 服务器逻辑（符合当前范围）
