# CLI 入口实现 - Typer 框架

## TL;DR

> **Quick Summary**: 为 madousho 项目实现基于 Typer 的 CLI 入口，支持配置文件读取和 3 个子命令（run/validate/show-config）。
> 
> **Deliverables**:
> - `src/madousho/cli.py` - CLI 入口文件
> - `pyproject.toml` 更新 - 添加 typer 依赖和命令行入口点
> 
> **Estimated Effort**: Short (2-3 小时)
> **Parallel Execution**: NO - sequential (依赖链清晰)
> **Critical Path**: 安装依赖 → 创建 CLI 框架 → 实现配置查找 → 实现子命令 → 注册入口点

---

## Context

### Original Request
用户需要一个 CLI 程序入口，使用 Typer 框架，实现配置文件读取和子命令支持。

### Interview Summary
**Key Discussions**:
- **CLI Framework**: 选择 Typer，与现有 Pydantic 完美集成
- **Global Options**: --config, --verbose/-v, --version（去掉 --debug，verbose 即输出 debug 日志）
- **Subcommands**: run, validate, show-config 三个基础子命令
- **Config Search**: 多位置查找策略

**Research Findings**:
- 现有配置模块 API：`load_config(config_path: str) -> Config`
- 配置模型：`Config`, `APIConfig`, `ProviderConfig` (Pydantic v2)
- Typer 最佳实践：callback 实现全局选项，ctx.obj 传递状态

### Metis Review
**Identified Gaps** (addressed):
- 子命令行为定义：run(stub)/validate(验证)/show-config(YAML 输出)
- 配置查找失败处理：报错退出（配置必需）
- Verbose 行为：控制日志级别，无独立 debug 选项

---

## Work Objectives

### Core Objective
实现一个功能完整的 CLI 入口框架，支持配置加载和基础子命令，为后续业务逻辑扩展打下基础。

### Concrete Deliverables
- `src/madousho/cli.py` - 完整的 CLI 实现（约 150-200 行）
- `pyproject.toml` - 添加 typer 依赖和 `[project.scripts]` 入口点
- `src/madousho/__init__.py` - 确保 `__version__` 导出

### Definition of Done
- [x] `python -m madousho --help` 显示帮助信息
- [x] `madousho --version` 输出 "0.1.0"
- [x] `madousho --config /path/to/config.yaml run` 可执行
- [x] 所有子命令响应 `--help`
- [x] `pip install -e .` 后 `madousho` 命令可用

### Must Have
- Typer callback 实现全局选项
- 配置文件多位置查找（CLI → ENV → cwd → home）
- 3 个子命令的基础结构
- 错误处理和用户友好的错误信息

### Must NOT Have (Guardrails)
- 不实现 run 的真实业务逻辑（仅 stub）
- 不添加 Rich 美化（用 Typer 默认输出）
- 不支持 TOML 等其他配置格式
- 不实现 shell completion 脚本
- 不编写测试（单独任务）

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest)
- **Automated tests**: NO (本次不包含单元测试)
- **Framework**: N/A
- **Agent-Executed QA**: ALWAYS (mandatory for all tasks)

### QA Policy
每个任务必须包含 agent-executed QA 场景：
- **CLI Commands**: 使用 Bash 运行命令，验证输出和 exit code
- **Evidence**: 保存到 `.sisyphus/evidence/task-{N}-{scenario}.{ext}`

---

## Execution Strategy

### Sequential Execution Flow

```
Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6

依赖链：
1. 安装依赖 (typer)
   ↓
2. 创建 CLI 框架 (cli.py 骨架 + callback)
   ↓
3. 实现配置查找逻辑 (find_config_file)
   ↓
4. 实现子命令 (run/validate/show-config)
   ↓
5. 注册入口点 (pyproject.toml)
   ↓
6. 最终验证 (所有命令测试)
```

### Agent Dispatch Summary
- **Task 1**: quick - 安装依赖
- **Task 2**: quick - CLI 骨架
- **Task 3**: unspecified-high - 配置查找逻辑
- **Task 4**: unspecified-high - 子命令实现
- **Task 5**: quick - 注册入口点
- **Task 6**: unspecified-high - 最终验证

---

## TODOs

- [x] 1. 安装 Typer 依赖

  **What to do**:
  - 在 `pyproject.toml` 的 `[project]` 部分添加 `dependencies` 列表
  - 添加 typer 依赖：`typer>=0.9.0,<1.0.0` (兼容 Pydantic v2)
  - 运行 `pip install -e .` 安装依赖
  - 验证安装：`python -c "import typer; print(typer.__version__)"`

  **Must NOT do**:
  - 不要修改其他依赖版本
  - 不要安装额外的富文本库（如 rich，typer 已内置）

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `[]`
  - **Reason**: 简单的依赖配置和安装

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (第一个任务)
  - **Blocks**: Task 2-6
  - **Blocked By**: None

  **References**:
  - `pyproject.toml` - 当前项目配置，需要添加 dependencies 字段
  - Typer 官方文档：https://typer.tiangolo.com/ - 版本兼容性参考

  **Acceptance Criteria**:
  - [x] `pyproject.toml` 包含 `dependencies` 字段
  - [x] dependencies 包含 `typer>=0.9.0,<1.0.0`
  - [x] `pip install -e .` 成功执行
  - [x] `python -c "import typer"` 无错误

  **QA Scenarios**:

  ```
  Scenario: 验证 typer 安装成功
    Tool: Bash
    Preconditions: 虚拟环境已激活
    Steps:
      1. 运行：pip install -e .
      2. 运行：python -c "import typer; print(typer.__version__)"
    Expected Result: 输出 typer 版本号（如 0.9.0）
    Failure Indicators: ImportError 或无输出
    Evidence: .sisyphus/evidence/task-1-install-success.txt
  ```

  **Commit**: YES (groups with 5)
  - Message: `feat(cli): add typer dependency`
  - Files: `pyproject.toml`
  - Pre-commit: `python -c "import typer"`

---

- [x] 2. 创建 CLI 入口骨架

  **What to do**:
  - 创建文件 `src/madousho/cli.py`
  - 实现 Typer app 实例化
  - 实现全局 callback（--config, --verbose, --version）
  - 使用 `ctx.obj` 存储全局状态
  - 添加 `if __name__ == "__main__": app()` 入口

  **Must NOT do**:
  - 不要实现配置查找逻辑（Task 3）
  - 不要实现子命令（Task 4）
  - 不要添加额外的全局选项

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `[]`
  - **Reason**: 标准 Typer 模板代码

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 3-4
  - **Blocked By**: Task 1

  **References**:
  - Typer callback 文档：https://typer.tiangolo.com/tutorial/options/callback/
  - 现有配置模块：`src/madousho/config/loader.py` - 了解 load_config API
  - `src/madousho/__init__.py` - 获取版本号

  **Acceptance Criteria**:
  - [x] `src/madousho/cli.py` 文件创建
  - [x] 包含 `app = typer.Typer()` 实例化
  - [x] 包含 `@app.callback()` 装饰的函数
  - [x] callback 接收 --config, --verbose, --version 参数
  - [x] 包含 `if __name__ == "__main__": app()`

  **QA Scenarios**:

  ```
  Scenario: 验证 CLI 骨架可运行
    Tool: Bash
    Preconditions: typer 已安装
    Steps:
      1. 运行：python src/madousho/cli.py --help
    Expected Result: 显示帮助信息，包含 --config, --verbose, --version 选项
    Failure Indicators: 报错或无输出
    Evidence: .sisyphus/evidence/task-2-skeleton-help.txt
  ```

  **Commit**: NO (groups with 5)

---

- [x] 3. 实现配置文件查找逻辑

  **What to do**:
  - 在 `cli.py` 中实现 `find_config_file(custom_path: Optional[str] = None) -> Path` 函数
  - 查找顺序：
    1. `custom_path` (CLI --config 参数)
    2. 环境变量 `MADOUSHO_CONFIG`
    3. `./madousho.yaml` 或 `./config/madousho.yaml`
    4. `~/.config/madousho/madousho.yaml`
  - 如果都找不到，抛出 `FileNotFoundError` 并显示用户友好的错误信息
  - 使用 `pathlib.Path` 实现跨平台兼容

  **Must NOT do**:
  - 不要修改现有 `src/madousho/config/loader.py`
  - 不要改变查找顺序
  - 不要支持其他配置文件格式（如 TOML）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`
  - **Reason**: 需要实现完整的路径查找逻辑和错误处理

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 4
  - **Blocked By**: Task 2

  **References**:
  - `src/madousho/config/loader.py` - 现有 load_config 函数
  - `config/madousho.yaml` - 示例配置文件位置
  - `config/madousho.example.yaml` - 示例配置文件位置

  **Acceptance Criteria**:
  - [x] `find_config_file` 函数实现
  - [x] 支持 4 层查找顺序
  - [x] 找不到文件时抛出清晰的错误信息
  - [x] 使用 pathlib.Path 处理路径

  **QA Scenarios**:

  ```
  Scenario: 验证 --config 参数指定路径
    Tool: Bash
    Preconditions: config/madousho.yaml 存在
    Steps:
      1. 运行：python src/madousho/cli.py --config config/madousho.yaml run
    Expected Result: 成功加载配置，不报错
    Failure Indicators: FileNotFoundError
    Evidence: .sisyphus/evidence/task-3-config-cli-arg.txt

  Scenario: 验证默认路径查找
    Tool: Bash
    Preconditions: config/madousho.yaml 存在，未指定 --config
    Steps:
      1. 运行：python src/madousho/cli.py run
    Expected Result: 自动找到 config/madousho.yaml 并加载
    Failure Indicators: 配置未找到错误
    Evidence: .sisyphus/evidence/task-3-config-default.txt

  Scenario: 验证配置不存在时的错误处理
    Tool: Bash
    Preconditions: 不存在的配置文件路径
    Steps:
      1. 运行：python src/madousho/cli.py --config /nonexistent/config.yaml run
      2. 检查 exit code
    Expected Result: 显示友好的错误信息，exit code != 0
    Failure Indicators: 无错误或错误信息不清晰
    Evidence: .sisyphus/evidence/task-3-config-error.txt
  ```

  **Commit**: NO (groups with 5)

---

- [x] 4. 实现 3 个子命令

  **What to do**:
  - 实现 `@app.command("run")` 函数：
    - 读取配置
    - 打印 "Starting madousho service..." (stub)
    - 如果 verbose，打印配置摘要
  - 实现 `@app.command("validate")` 函数：
    - 读取配置
    - 验证 YAML 语法和 Pydantic 模型
    - 输出 "✓ Configuration is valid" 或错误信息
  - 实现 `@app.command("show-config")` 函数：
    - 读取配置
    - 以 YAML 格式打印到 stdout
    - 便于调试

  **Must NOT do**:
  - 不要实现 run 的真实业务逻辑（仅 stub）
  - 不要添加额外的子命令
  - 不要修改现有配置模型

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`
  - **Reason**: 需要实现 3 个子命令的逻辑和输出格式

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 5-6
  - **Blocked By**: Task 3

  **References**:
  - `src/madousho/config/loader.py:load_config()` - 配置加载 API
  - `src/madousho/config/models.py:Config` - 配置模型
  - Typer 子命令文档：https://typer.tiangolo.com/tutorial/commands/
  - `config/madousho.yaml` - 示例配置内容

  **Acceptance Criteria**:
  - [x] `run` 子命令实现（stub）
  - [x] `validate` 子命令实现（验证配置）
  - [x] `show-config` 子命令实现（YAML 输出）
  - [x] 所有子命令响应 `--help`
  - [x] 错误时显示清晰的错误信息

  **QA Scenarios**:

  ```
  Scenario: run 子命令帮助信息
    Tool: Bash
    Preconditions: cli.py 已创建
    Steps:
      1. 运行：python src/madousho/cli.py run --help
    Expected Result: 显示 run 命令的帮助信息
    Failure Indicators: 报错或无输出
    Evidence: .sisyphus/evidence/task-4-run-help.txt

  Scenario: validate 子命令验证有效配置
    Tool: Bash
    Preconditions: config/madousho.yaml 存在且有效
    Steps:
      1. 运行：python src/madousho/cli.py validate
    Expected Result: 输出 "✓ Configuration is valid"
    Failure Indicators: 报错或验证失败
    Evidence: .sisyphus/evidence/task-4-validate-success.txt

  Scenario: validate 子命令验证无效配置
    Tool: Bash
    Preconditions: 创建临时无效配置文件
    Steps:
      1. 创建无效 YAML 文件 /tmp/invalid.yaml
      2. 运行：python src/madousho/cli.py --config /tmp/invalid.yaml validate
    Expected Result: 输出具体错误信息，exit code != 0
    Failure Indicators: 无错误或错误不清晰
    Evidence: .sisyphus/evidence/task-4-validate-error.txt

  Scenario: show-config 子命令输出配置
    Tool: Bash
    Preconditions: config/madousho.yaml 存在
    Steps:
      1. 运行：python src/madousho/cli.py show-config
    Expected Result: 以 YAML 格式输出配置内容
    Failure Indicators: 输出格式错误或乱码
    Evidence: .sisyphus/evidence/task-4-show-config.txt

  Scenario: run 子命令 verbose 模式
    Tool: Bash
    Preconditions: config/madousho.yaml 存在
    Steps:
      1. 运行：python src/madousho/cli.py --verbose run
      2. 检查输出包含配置摘要
    Expected Result: 输出包含配置摘要信息
    Failure Indicators: 无额外输出
    Evidence: .sisyphus/evidence/task-4-run-verbose.txt
  ```

  **Commit**: NO (groups with 5)

---

- [x] 5. 注册命令行入口点

  **What to do**:
  - 在 `pyproject.toml` 添加 `[project.scripts]` 部分
  - 注册入口点：`madousho = madousho.cli:app`
  - 确保 `src/madousho/__init__.py` 导出 `__version__`
  - 运行 `pip install -e .` 重新安装
  - 验证 `madousho --help` 可用

  **Must NOT do**:
  - 不要修改其他 pyproject.toml 配置
  - 不要添加额外的入口点

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `[]`
  - **Reason**: 简单的配置修改

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 6
  - **Blocked By**: Task 4

  **References**:
  - `pyproject.toml` - 当前项目配置
  - `src/madousho/__init__.py` - 版本导出
  - PEP 621 规范：https://peps.python.org/pep-0621/#entry-points

  **Acceptance Criteria**:
  - [x] `pyproject.toml` 包含 `[project.scripts]` 部分
  - [x] 入口点格式正确：`madousho = madousho.cli:app`
  - [x] `src/madousho/__init__.py` 包含 `__version__ = "0.1.0"`
  - [x] `pip install -e .` 成功执行
  - [x] `madousho --help` 命令可用

  **QA Scenarios**:

  ```
  Scenario: 验证命令行入口点注册
    Tool: Bash
    Preconditions: pyproject.toml 已更新
    Steps:
      1. 运行：pip install -e .
      2. 运行：madousho --help
    Expected Result: 显示帮助信息，与 python src/madousho/cli.py --help 相同
    Failure Indicators: 命令不存在或报错
    Evidence: .sisyphus/evidence/task-5-entrypoint-help.txt

  Scenario: 验证版本号
    Tool: Bash
    Preconditions: 入口点已注册
    Steps:
      1. 运行：madousho --version
    Expected Result: 输出 "0.1.0"
    Failure Indicators: 版本号错误或无输出
    Evidence: .sisyphus/evidence/task-5-version.txt
  ```

  **Commit**: YES (与 Task 1-4 一起)
  - Message: `feat(cli): add typer CLI entry point`
  - Files: `src/madousho/cli.py`, `pyproject.toml`, `src/madousho/__init__.py`
  - Pre-commit: `madousho --help`

---

- [x] 6. 最终验证

  **What to do**:
  - 运行所有 QA 场景，确保所有功能正常
  - 验证所有子命令的 help 信息
  - 验证配置查找逻辑的所有路径
  - 验证错误处理的用户友好性
  - 捕获所有证据文件

  **Must NOT do**:
  - 不要修改代码（代码问题应返回前面任务修复）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`
  - **Reason**: 需要全面验证所有功能

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (最后一个任务)
  - **Blocks**: None
  - **Blocked By**: Task 5

  **References**:
  - 所有前述任务的 QA Scenarios
  - `.sisyphus/evidence/` - 证据文件存储目录

  **Acceptance Criteria**:
  - [x] 所有 QA 场景通过
  - [x] 所有证据文件存在
  - [x] 无未处理的异常
  - [x] 错误信息清晰友好

  **QA Scenarios**:

  ```
  Scenario: 完整功能验证
    Tool: Bash
    Preconditions: 所有代码已实现并安装
    Steps:
      1. 验证 --help: madousho --help
      2. 验证 --version: madousho --version
      3. 验证 run: madousho run
      4. 验证 validate: madousho validate
      5. 验证 show-config: madousho show-config
      6. 验证 --verbose: madousho --verbose run
      7. 验证 --config: madousho --config config/madousho.yaml validate
    Expected Result: 所有命令成功执行，输出符合预期
    Failure Indicators: 任何命令失败或输出异常
    Evidence: .sisyphus/evidence/task-6-final-verification.txt
  ```

  **Commit**: NO (已在 Task 5 提交)

---

## Final Verification Wave

- [x] F1. **Plan Compliance Audit** — `oracle`
  验证所有 "Must Have" 已实现，所有 "Must NOT Have" 未出现。

- [x] F2. **Code Quality Review** — `unspecified-high`
  运行类型检查和代码审查，确保无 `as any`、空 catch、未使用导入等。

- [x] F3. **Real Manual QA** — `unspecified-high`
  执行所有 QA 场景，验证 CLI 功能完整性。

- [x] F4. **Scope Fidelity Check** — `deep`
  验证实现与计划 1:1 匹配，无范围蔓延。

---

## Commit Strategy

- **Task 1-5**: `feat(cli): add typer CLI entry point`
  - Files: `src/madousho/cli.py`, `pyproject.toml`, `src/madousho/__init__.py`
  - Pre-commit: `madousho --help && madousho --version`

---

## Success Criteria

### Verification Commands
```bash
madousho --help              # Expected: 显示帮助信息
madousho --version           # Expected: 输出 "0.1.0"
madousho run                 # Expected: 显示启动信息
madousho validate            # Expected: 显示验证结果
madousho show-config         # Expected: 输出 YAML 配置
madousho --verbose run       # Expected: 显示详细输出
```

### Final Checklist
- [x] 所有 "Must Have" 已实现
- [x] 所有 "Must NOT Have" 未出现
- [x] 所有 QA 场景通过
- [x] 证据文件完整
