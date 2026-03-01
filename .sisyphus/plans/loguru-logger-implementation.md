# Madousho AI - Loguru 日志系统实施计划

## TL;DR

> **核心目标**: 为 madousho AI 框架引入 loguru 作为统一日志库，替换现有的 typer.echo 和 print，并添加 CLI 日志控制功能
> 
> **交付物**:
> - `src/madousho/logger.py` - 统一日志模块（支持动态级别和格式切换）
> - `src/madousho/cli.py` - 添加 --json 和 --verbose 全局 flag
> - `logs/` - 日志文件目录（JSON 格式）
> - 全项目替换 typer.echo/print 为结构化日志
> - pyproject.toml 添加 loguru 依赖
> 
> **预计工作量**: 小型（1-2 小时）
> **并行执行**: 是 - 2 个波次
> **关键路径**: 创建 logger 模块 → 添加 CLI flags → 替换现有输出 → 测试验证

---

## Context

### 原始需求
用户要求为 Python Web 应用（madousho AI 框架）选择一个统一的日志库，支持 JSON 和文本两种输出格式。

### 访谈总结
**关键讨论**:
- **项目类型**: CLI 应用 + Web 服务（madousho AI 框架）
- **当前状态**: 有 5 处 typer.echo（CLI 输出）和 1 处 print（调试）
- **核心需求**: 支持 JSON 和文本双格式输出
- **性能要求**: 用户明确表示"性能无所谓"

**技术选型对比**:
- structlog: 性能最优（12,101 logs/sec），但配置复杂
- loguru: API 极简，开箱即用，性能较差但用户接受
- 最终选择: **loguru**（用户决策）

### 调研发现
- 项目入口：`src/madousho/cli.py` (Typer CLI)
- 现有输出分散在 commands 目录下的各个子命令
- 无现有日志基础设施，是引入的好时机

---

## Work Objectives

### 核心目标
为 madousho AI 框架建立统一的日志系统，使用 loguru 实现结构化日志输出。

### 具体交付物
- `src/madousho/logger.py` - 统一日志配置和导出（支持动态级别和 JSON 切换）
- `src/madousho/cli.py` - 添加 --json 和 --verbose 全局 CLI flags
- `logs/app.json` - JSON 格式日志文件
- 控制台彩色文本输出（默认）或 JSON 输出（--json flag）
- 替换所有 typer.echo 和 print 为 logger 调用

### 完成定义
- [x] `python -c "from madousho.logger import logger"` 成功导入
- [x] 运行 CLI 命令能看到彩色日志输出
- [x] `madousho --json show-config` 输出 JSON 格式日志
- [x] `madousho --verbose show-config` 输出 DEBUG 级别日志
- [x] logs/app.json 文件包含 JSON 格式日志
- [x] 所有 typer.echo 和 print 已替换
- [x] pytest 测试通过

### Must Have
- [x] 控制台彩色输出（开发友好，默认）
- [x] JSON 文件输出（生产/审计）
- [x] 日志轮转（防止文件过大）
- [x] 统一 logger 模块，全项目导入使用
- [x] **CLI flag `--json`** - 启用 JSON 输出模式
- [x] **CLI flag `--verbose`** - 启用 DEBUG 日志级别

### Must NOT Have（防护栏）
- [x] 不要移除 typer - 保持 CLI 功能正常
- [x] 不要过度封装 - 直接导出 loguru 的 logger
- [x] 不要配置太复杂 - 保持简单直观
- [x] 不要破坏现有 CLI 命令功能
- [x] 不要硬编码日志级别 - 应该由 CLI flags 控制

---

## Verification Strategy

### 测试决策
- **基础设施存在**: NO（项目无测试基础设施）
- **自动化测试**: NO（用户未要求）
- **验证方式**: Agent-Executed QA Scenarios

### QA 策略
每个任务必须包含 Agent 执行的 QA 场景：
- **导入验证**: Python 导入测试
- **功能验证**: 运行 CLI 命令，检查日志输出
- **文件验证**: 检查 JSON 日志文件内容
- **替换验证**: 搜索代码确认无残留 typer.echo/print

---

## Execution Strategy

### 并行执行波次

```
Wave 1（基础设置 - 立即开始）:
├── Task 1: 安装 loguru 依赖 [quick]
├── Task 2: 创建 logger 模块 [quick]
└── Task 3: 配置日志目录和轮转 [quick]

Wave 2（CLI flags + 替换 - Wave 1 完成后）:
├── Task 4: 在 cli.py 添加 --json 和 --verbose 全局 flags [quick]
├── Task 5: 替换 commands/run.py 中的 typer.echo [quick]
├── Task 6: 替换 commands/validate.py 中的 typer.echo [quick]
├── Task 7: 替换 commands/show_config.py 中的 typer.echo [quick]
├── Task 8: 替换 config/__init__.py 中的 print [quick]
└── Task 9: 最终验证 - 测试 flags 和日志输出 [quick]

关键路径：Task 1 → Task 2 → Task 4 → Task 5-8 → Task 9
并行加速：~60% 快于顺序执行
最大并发：3（Wave 1）和 6（Wave 2）
```

### 依赖矩阵
- **1**: — → 2, 3
- **2**: 1 → 4, 5, 6, 7, 8
- **3**: 2 → 5, 6, 7, 8
- **4**: 2 → 5, 6, 7, 8
- **5-8**: 2, 3, 4 → 9
- **9**: 4, 5, 6, 7, 8 → 完成

### Agent 调度总结
- **Wave 1**: 3 任务 → `quick`
- **Wave 2**: 6 任务 → `quick`

---

## TODOs

- [x] 1. 安装 loguru 依赖

  **做什么**:
  - 在 pyproject.toml 添加 loguru>=0.7.0 依赖
  - 运行 pip install -e . 安装
  - 验证导入：python -c "from loguru import logger"

  **禁止做**:
  - 不要修改其他依赖版本
  - 不要升级现有包

  **推荐 Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **理由**: 简单的依赖添加和验证

  **并行化**:
  - **可并行**: YES
  - **并行组**: Wave 1（与 Task 2, 3）
  - **阻塞**: Task 2, 3
  - **被阻塞**: 无

  **参考**:
  - `pyproject.toml` - 查看现有依赖格式
  - Loguru 官方文档：https://loguru.readthedocs.io/en/stable/

  **验收标准**:
  - [x] pyproject.toml 包含 loguru>=0.7.0
  - [x] python -c "from loguru import logger" 无错误

  **QA 场景**:
  ```
  Scenario: 验证 loguru 可导入
    Tool: Bash
    步骤:
      1. 运行：python -c "from loguru import logger; print('OK')"
      2. 检查输出包含 "OK"
    预期结果：输出 "OK"，退出码 0
    证据：.sisyphus/evidence/task-1-import-test.txt
  ```

  **Commit**: YES（Wave 1 合并提交）
  - Message: `feat(logging): add loguru dependency`
  - Files: pyproject.toml


- [x] 2. 创建统一 logger 模块

  **做什么**:
  - 创建 `src/madousho/logger.py`
  - 配置 loguru：控制台彩色输出 + JSON 文件输出
  - 导出 logger 实例供全项目使用
  - 配置日志格式：时间、级别、模块、函数、行号、消息

  **禁止做**:
  - 不要过度封装 - 直接导出 loguru logger
  - 不要配置太复杂 - 保持简单

  **推荐 Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **理由**: 简单的模块创建和配置

  **并行化**:
  - **可并行**: YES
  - **并行组**: Wave 1（与 Task 1, 3）
  - **阻塞**: Task 4, 5, 6, 7
  - **被阻塞**: Task 1

  **参考**:
  - `src/madousho/cli.py` - 查看项目结构
  - Loguru 配置文档：https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.configure

  **验收标准**:
  - [x] 文件创建：src/madousho/logger.py
  - [x] 可从 madousho 包导入：from madousho.logger import logger
  - [x] 控制台输出带颜色
  - [x] JSON 文件输出到 logs/app.json

  **QA 场景**:
  ```
  Scenario: 验证 logger 模块可导入和使用
    Tool: Bash
    步骤:
      1. 运行：python -c "from madousho.logger import logger; logger.info('test')"
      2. 检查控制台有彩色输出
      3. 检查 logs/app.json 文件存在
    预期结果：控制台显示彩色日志，logs/app.json 包含 JSON 日志行
    证据：.sisyphus/evidence/task-2-logger-test.txt, .sisyphus/evidence/task-2-logger.json
  ```

  **Commit**: YES（Wave 1 合并提交）
  - Message: `feat(logging): create unified logger module`
  - Files: src/madousho/logger.py


- [x] 3. 配置日志目录和轮转

  **做什么**:
  - 在 logger.py 中配置日志轮转（rotation）
  - 配置日志压缩（compression）
  - 配置日志保留策略（retention）
  - 确保 logs 目录自动创建

  **禁止做**:
  - 不要手动创建 logs 目录 - 应该自动创建
  - 不要配置太激进的轮转策略

  **推荐 Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **理由**: 简单的配置任务

  **并行化**:
  - **可并行**: YES
  - **并行组**: Wave 1（与 Task 1, 2）
  - **阻塞**: Task 4, 5, 6, 7
  - **被阻塞**: Task 2

  **参考**:
  - Loguru 轮转文档：https://loguru.readthedocs.io/en/stable/api/logger.html#file-sink
  - Task 2 的 logger.py 配置

  **验收标准**:
  - [x] 日志轮转：文件大小超过 10MB 时轮转
  - [x] 日志压缩：轮转后压缩为 .gz
  - [x] 日志保留：保留最近 7 天
  - [x] logs 目录不存在时自动创建

  **QA 场景**:
  ```
  Scenario: 验证日志轮转配置
    Tool: Bash
    步骤:
      1. 运行：python -c "from madousho.logger import logger; logger.info('rotation test')"
      2. 检查 logs/ 目录包含 app.json
      3. 查看 logger.py 配置确认 rotation="10 MB", compression="gzip", retention="7 days"
    预期结果：logs/app.json 存在，配置包含轮转参数
    证据：.sisyphus/evidence/task-3-rotation-config.txt
  ```

  **Commit**: YES（Wave 1 合并提交）
  - Message: `feat(logging): configure log rotation and retention`
  - Files: src/madousho/logger.py


- [x] 4. 在 cli.py 添加 --json 和 --verbose 全局 flags

  **做什么**:
  - 打开 src/madousho/cli.py
  - 在 Typer app 添加全局 options：--json 和 --verbose
  - 根据 --json flag 配置 logger 输出格式（JSON 或控制台）
  - 根据 --verbose flag 配置 logger 级别（DEBUG 或 INFO）
  - 使用 typer.get_current_context() 或回调函数处理全局 flags

  **禁止做**:
  - 不要破坏现有子命令
  - 不要硬编码日志配置 - 应该动态响应 flags

  **推荐 Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **理由**: Typer CLI 配置任务

  **并行化**:
  - **可并行**: YES
  - **并行组**: Wave 2（与 Task 5, 6, 7, 8）
  - **阻塞**: Task 5, 6, 7, 8（需要 logger 支持 flags）
  - **被阻塞**: Task 2

  **参考**:
  - `src/madousho/cli.py` - 当前 Typer app 结构
  - Typer 全局 options 文档：https://typer.tiangolo.com/tutorial/options/callback/
  - Task 2 的 logger.py - logger 配置函数

  **验收标准**:
  - [x] cli.py 包含 --json 全局 flag
  - [x] cli.py 包含 --verbose 全局 flag
  - [x] madousho --help 显示这两个 flags
  - [x] madousho --json show-config 输出 JSON 格式
  - [x] madousho --verbose show-config 输出 DEBUG 级别日志

  **QA 场景**:
  ```
  Scenario: 验证 --json flag
    Tool: Bash
    步骤:
      1. 运行：madousho --help
      2. 检查输出包含 --json 和 --verbose
      3. 运行：madousho --json show-config 2>&1 | head -5
      4. 检查输出是 JSON 格式（包含 {）
    预期结果：--json flag 生效，输出 JSON 格式日志
    证据：.sisyphus/evidence/task-4-json-flag.txt

  Scenario: 验证 --verbose flag
    Tool: Bash
    步骤:
      1. 运行：madousho --verbose show-config 2>&1 | head -10
      2. 检查输出包含 DEBUG 级别日志
    预期结果：--verbose flag 生效，输出 DEBUG 日志
    证据：.sisyphus/evidence/task-4-verbose-flag.txt
  ```

  **Commit**: YES（Wave 2 合并提交）
  - Message: `feat(logging): add --json and --verbose CLI flags`
  - Files: src/madousho/cli.py


- [x] 5. 替换 commands/run.py 中的 typer.echo

  **做什么**:
  **做什么**:
  - 打开 src/madousho/commands/run.py
  - 找到所有 typer.echo 调用
  - 替换为 logger.info() 或 logger.success()
  - 添加适当的结构化字段（如 service_name, status 等）

  **禁止做**:
  - 不要删除 typer 导入（如果还有其他用途）
  - 不要改变消息内容 - 保持用户友好的文本

  **推荐 Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **理由**: 简单的代码替换

  **并行化**:
  - **可并行**: YES
  - **并行组**: Wave 2（与 Task 5, 6, 7）
  - **阻塞**: Task 8
  - **被阻塞**: Task 2, 3

  **参考**:
  - `src/madousho/commands/run.py` - 当前实现
  - Task 2 的 logger.py - logger 导入方式

  **验收标准**:
  - [x] 所有 typer.echo 替换为 logger.info/success
  - [x] 添加 logger 导入
  - [x] 代码语法正确
  - [x] 运行 madousho run 命令能看到日志

  **QA 场景**:
  ```
  Scenario: 验证 run 命令日志输出
    Tool: Bash
    步骤:
      1. 运行：madousho run --help
      2. 检查无 typer.echo 输出，只有 logger 输出
      3. 运行：grep -n "typer.echo" src/madousho/commands/run.py
      4. 确认无匹配结果
    预期结果：无 typer.echo 残留，日志正常输出
    证据：.sisyphus/evidence/task-4-run-logging.txt
  ```

  **Commit**: YES（Wave 2 合并提交）
  - Message: `refactor(logging): migrate run.py to loguru`
  - Files: src/madousho/commands/run.py


- [x] 6. 替换 commands/validate.py 中的 typer.echo

  **做什么**:
  - 打开 src/madousho/commands/validate.py
  - 找到所有 typer.echo 调用
  - 替换为 logger.info/success/warning/error
  - 添加结构化字段（如 validation_result, errors_count 等）

  **禁止做**:
  - 不要改变验证逻辑
  - 不要删除必要的 typer 导入

  **推荐 Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **理由**: 简单的代码替换

  **并行化**:
  - **可并行**: YES
  - **并行组**: Wave 2（与 Task 4, 6, 7）
  - **阻塞**: Task 8
  - **被阻塞**: Task 2, 3

  **参考**:
  - `src/madousho/commands/validate.py` - 当前实现
  - Task 2 的 logger.py

  **验收标准**:
  - [x] 所有 typer.echo 替换为 logger.*
  - [x] 添加 logger 导入
  - [x] 运行 madousho validate 能看到日志

  **QA 场景**:
  ```
  Scenario: 验证 validate 命令日志输出
    Tool: Bash
    步骤:
      1. 运行：grep -n "typer.echo" src/madousho/commands/validate.py
      2. 确认无匹配结果
      3. 运行：madousho validate --help
    预期结果：无 typer.echo 残留
    证据：.sisyphus/evidence/task-5-validate-logging.txt
  ```

  **Commit**: YES（Wave 2 合并提交）
  - Message: `refactor(logging): migrate validate.py to loguru`
  - Files: src/madousho/commands/validate.py


- [x] 7. 替换 commands/show_config.py 中的 typer.echo

  **做什么**:
  - 打开 src/madousho/commands/show_config.py
  - 替换所有 typer.echo 为 logger.info
  - 配置信息用 logger.debug 或 logger.info 输出

  **禁止做**:
  - 不要改变配置显示逻辑
  - 不要泄露敏感信息（如 API key）

  **推荐 Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **理由**: 简单的代码替换

  **并行化**:
  - **可并行**: YES
  - **并行组**: Wave 2（与 Task 4, 5, 7）
  - **阻塞**: Task 8
  - **被阻塞**: Task 2, 3

  **参考**:
  - `src/madousho/commands/show_config.py` - 当前实现
  - Task 2 的 logger.py

  **验收标准**:
  - [x] 所有 typer.echo 替换为 logger.*
  - [x] 添加 logger 导入
  - [x] 运行 madousho show-config 能看到日志

  **QA 场景**:
  ```
  Scenario: 验证 show-config 命令日志输出
    Tool: Bash
    步骤:
      1. 运行：grep -n "typer.echo" src/madousho/commands/show_config.py
      2. 确认无匹配结果
    预期结果：无 typer.echo 残留
    证据：.sisyphus/evidence/task-6-show-config-logging.txt
  ```

  **Commit**: YES（Wave 2 合并提交）
  - Message: `refactor(logging): migrate show_config.py to loguru`
  - Files: src/madousho/commands/show_config.py


- [x] 8. 替换 config/__init__.py 中的 print

  **做什么**:
  - 打开 src/madousho/config/__init__.py
  - 找到 print 语句
  - 替换为 logger.debug（调试信息）

  **禁止做**:
  - 不要改变配置加载逻辑
  - 不要在输出中泄露敏感配置

  **推荐 Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **理由**: 简单的代码替换

  **并行化**:
  - **可并行**: YES
  - **并行组**: Wave 2（与 Task 4, 5, 6）
  - **阻塞**: Task 8
  - **被阻塞**: Task 2, 3

  **参考**:
  - `src/madousho/config/__init__.py` - 当前实现
  - Task 2 的 logger.py

  **验收标准**:
  - [x] 所有 print 替换为 logger.debug
  - [x] 添加 logger 导入
  - [x] 配置加载正常

  **QA 场景**:
  ```
  Scenario: 验证 config 模块无 print
    Tool: Bash
    步骤:
      1. 运行：grep -n "^print(" src/madousho/config/__init__.py
      2. 确认无匹配结果
    预期结果：无 print 残留
    证据：.sisyphus/evidence/task-7-config-logging.txt
  ```

  **Commit**: YES（Wave 2 合并提交）
  - Message: `refactor(logging): migrate config module to loguru`
  - Files: src/madousho/config/__init__.py


- [x] 9. 最终验证 - 运行 CLI 检查日志

  **做什么**:
  - 运行所有 CLI 命令验证日志正常
  - 检查控制台彩色输出
  - 检查 logs/app.json 包含 JSON 日志
  - 验证无 typer.echo 和 print 残留

  **禁止做**:
  - 不要修改代码（除非发现严重问题）

  **推荐 Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **理由**: 验证任务

  **并行化**:
  - **可并行**: NO
  - **并行组**: Sequential（最后一步）
  - **阻塞**: 无
  - **被阻塞**: Task 4, 5, 6, 7

  **参考**:
  - 所有 commands 文件
  - logs/app.json

  **验收标准**:
  - [x] madousho --help 正常
  - [x] madousho run --help 正常
  - [x] madousho validate --help 正常
  - [x] madousho show-config 正常
  - [x] logs/app.json 包含有效的 JSON 日志行
  - [x] 全项目无 typer.echo 残留（commands 目录）
  - [x] 全项目无 print 残留（config 目录）

  **QA 场景**:
  ```
  Scenario: 全项目日志替换验证
    Tool: Bash
    步骤:
      1. 运行：grep -rn "typer.echo" src/madousho/commands/
      2. 运行：grep -rn "^print(" src/madousho/config/
      3. 运行：madousho show-config
      4. 检查 logs/app.json 最后 5 行
      5. 运行：python -c "import json; [json.loads(line) for line in open('logs/app.json')]"
    预期结果: 
      - grep 无输出（无残留）
      - CLI 命令正常执行
      - logs/app.json 每行都是有效 JSON
    证据：.sisyphus/evidence/task-8-final-verification.txt, .sisyphus/evidence/task-8-json-valid.txt
  ```

  **Commit**: YES
  - Message: `test(logging): verify CLI commands with new logger`
  - Files: N/A (验证任务)


---

## Final Verification Wave

- [x] F1. **计划合规审计** - `oracle`
  逐项检查"Must Have"是否实现，搜索"Must NOT Have"违规，验证证据文件存在。
  输出：`Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **代码质量审查** - `unspecified-high`
  运行代码检查：无 typer.echo/print 残留，loguru 导入正确，JSON 日志格式有效。
  输出：`Imports [OK] | Legacy [CLEAN] | JSON [VALID] | VERDICT`

- [x] F3. **真实手动 QA** - `unspecified-high`
  从干净状态执行所有 CLI 命令，验证日志输出，检查 JSON 文件内容。
  输出：`Commands [N/N pass] | Console [OK] | JSON [OK] | VERDICT`

- [x] F4. **范围保真检查** - `deep`
  检查每个任务：只替换了输出语句，未改变业务逻辑，无范围蔓延。
  输出：`Tasks [N/N compliant] | Logic [UNCHANGED] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `feat(logging): add loguru and create logger module`
  - Files: pyproject.toml, src/madousho/logger.py
  - Pre-commit: python -c "from madousho.logger import logger"

- **Wave 2**: `refactor(logging): migrate all commands to loguru`
  - Files: src/madousho/commands/*.py, src/madousho/config/__init__.py
  - Pre-commit: grep -rn "typer.echo" src/madousho/commands/ (should return nothing)

- **Final**: `chore(logging): cleanup and verification`
  - Files: N/A
  - Pre-commit: madousho --help && madousho show-config

---

## Success Criteria

### 验证命令
```bash
# 1. 验证 logger 可导入
python -c "from madousho.logger import logger; logger.info('OK')"

# 2. 验证 CLI 命令正常
madousho --help
madousho show-config

# 3. 验证无残留
grep -rn "typer.echo" src/madousho/commands/  # 应无输出
grep -rn "^print(" src/madousho/config/  # 应无输出

# 4. 验证 JSON 日志有效
python -c "import json; [json.loads(line) for line in open('logs/app.json')]"
```

### 最终检查清单
- [x] 所有 Must Have 已实现
- [x] 所有 Must NOT Have 未违反
- [x] 所有 CLI 命令正常工作
- [x] JSON 日志文件有效
- [x] 无 typer.echo/print 残留
- [x] 日志轮转配置正确
