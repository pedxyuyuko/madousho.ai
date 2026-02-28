# Madousho.ai (魔导书) - 系统性 AI Agent 框架

## 项目概述

**名称**: Madousho.ai (真導将 / 魔导书)

**核心理念**: 程序控制流程 + AI 执行步骤 = 可控的 AI Agent

**解决的问题**: 现有 AI Agent 让模型自己决定下一步，随机性太大

**解决方案**: 固定流程，模型只执行指令

---

## 核心技术决策

| 模块 | 决策 |
|------|------|
| **语言** | Python |
| **框架** | LangChain |
| **后端 API** | FastAPI |
| **前端** | Vue.js SPA |
| **存储** | TinyDB (嵌入式 NoSQL，类似 MongoDB) |
| **实时** | SSE (Server-Sent Events) |
| **CLI** | Click (子命令模式) |
| **测试** | pytest |
| **认证** | 简单 Token 鉴权 |

---

## 流程控制模型

- **顺序**: 步骤按定义顺序执行
- **并行**: `spawn=True` 时创建子任务并行执行
- **条件**: if/else 分支，基于 context 决策
- **循环**: while/for 循环，支持 break
- **子任务**: Flow → Step → Sub-step，并行处理，结果带 tag

---

## 上下文管理 (out)

```python
class Context:
    @property
    def out(self) -> list[StepResult]:
        """返回所有结果，按顺序"""
        ...
    
    # 访问方式
    out[-1]           # 最后一项
    out[0:3]           # 切片
    out["step_id"]     # 按 ID
    out[-1].output     # 字段访问
```

**自动裁剪**: 当 context 超过 LLM 限制时，自动裁剪最老的输出

---

## 插件系统

### 项目结构

```
plugins/                    # 插件存储目录
└── 插件名/
    ├── manifest.yaml       # 插件元信息
    ├── __init__.py         # 入口
    ├── flows/              # 流程定义
    ├── tools/              # 工具
    ├── prompts/            # 默认 Prompt
    └── requirements.txt     # 依赖
```

### manifest.yaml 格式

```yaml
name: @example/search-flow
version: 1.0.0
description: Search and report flow

flows:
  - search_report
  - deep_search

tools:
  - web_search
  - content_parser

dependencies:
  - requests
  - beautifulsoup4
```

### 安装方式

```bash
madousho install https://github.com/user/plugin-repo
```

程序会:
1. `git clone` 仓库到 plugins/ 目录
2. 解析 `manifest.yaml` 获取依赖
3. 安装依赖 (`pip install -r requirements.txt`)
4. 注册流程/工具到系统

### 隔离方式

- **目录隔离**: 每个插件有独立目录
- **Import 隔离**: 动态 import
- **安全**: 信任插件代码 (用户最佳实践是 Docker 中运行)

---

## Prompt 管理机制

```
用户覆盖优先级:
1. prompts/插件ID/步骤名.md    (用户自定义)
2. 插件自带的 prompts/步骤名.md  (默认)

get_prompt(插件ID, 步骤名):
    1. 检查 prompts/插件ID/步骤名.md 是否存在
    2. 若存在，返回用户自定义的 prompt
    3. 否则，读取插件自带的 prompts/步骤名.md
    4. 若仍不存在，使用内置默认 prompt

示例:
    prompts/my-search/search_step.md  → 用户覆盖
    plugins/my-search/prompts/search_step.md  → 插件默认
```

---

## LLM Tool Exposure

在 prompt 里暴露 tools 给 LLM，提供让 LLM 直接输出的选项:

```
Prompt 中暴露 tools:
- 搜索工具 (web_search)
- 读取工具 (read_file)
- 输出工具 (output_report)  ← LLM 可以直接输出产物

Example:
你是一个研究助手。请使用提供的工具搜索信息，并生成报告。
完成后使用 output_report 工具输出最终产物。
```

---

## Artifact System (CI/CD 风格)

流程可以产出报告/文件，类似 Jenkins/GitLab CI/GitHub Actions:

- 产物类型: 报告/文件/截图/JSON/Markdown/HTML/PDF
- 存储位置: `data/artifacts/`
- 可下载、可视化

---

## 项目目录结构

```
madousho.ai/                         # 项目根目录
├── madousho/                        # Python 核心包 (简化结构)
│   ├── __init__.py                  # 包入口，导出主要 API
│   ├── auth.py                      # 简单 Token 鉴权
│   ├── config.py                    # 配置管理
│   ├── cli.py                       # CLI 入口
│   ├── api.py                       # FastAPI 入口
│   ├── core.py                      # 核心: types, context, engine, errors
│   ├── decorators.py                # @flow, @step 装饰器
│   ├── storage.py                   # TinyDB 存储
│   ├── plugins.py                   # 插件系统 + Prompt 管理
│   │   └── prompts.py               # get_prompt(插件ID, 步骤名) 支持用户覆盖
│   └── tools.py                     # 内置工具 (LLM, output_report)

├── frontend/                        # Vue.js 前端
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.ts
│   │   ├── views/
│   │   │   ├── Flows.vue            # 流程列表
│   │   │   ├── Run.vue              # 流程运行
│   │   │   └── Settings.vue         # 设置
│   │   ├── components/
│   │   │   ├── FlowCard.vue
│   │   │   ├── StepProgress.vue
│   │   │   └── ArtifactViewer.vue   # 产物查看器
│   │   ├── api/
│   │   │   └── client.ts
│   │   └── stores/
│   │       └── flow.ts
│   └── package.json

├── plugins/                         # 插件存储目录
│   └── .gitkeep

├── prompts/                         # 用户自定义 Prompt 覆盖
│   └── .gitkeep                      # 格式: prompts/插件ID/步骤名.md

├── data/                            # 数据存储目录 (运行时生成)
│   ├── madousho.db                   # TinyDB 数据库:
│   │   # - 流程定义
│   │   # - 运行历史 (每次运行的输入/输出/状态)
│   │   # - 产物元数据
│   │   # - 用户配置
│   ├── artifacts/                    # 流程产物: 报告/文件/截图 (可下载)
│   └── config.yaml                   # 配置文件

├── tests/                           # 测试
│   ├── core/
│   ├── plugins/
│   └── api/

├── pyproject.toml
├── README.md
└── .env.example
```

---

## 框架大体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Madousho (魔导书)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Python Core                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │  │
│  │  │   @flow     │  │  Context    │  │   Flow Engine   │  │  │
│  │  │  Decorator  │  │  Manager    │  │  (DAG Executor) │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │  │
│  │                                                          │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │  │
│  │  │   Plugin    │  │   Storage   │  │     Tools       │  │  │
│  │  │   System    │  │  (TinyDB)   │  │   (LLM etc.)    │  │  │
│  │  │  + Prompts  │  │  + History  │  │                 │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│         ┌────────────────────┼────────────────────┐            │
│         │                    │                    │            │
│  ┌──────┴──────┐     ┌──────┴──────┐     ┌──────┴──────┐     │
│  │    CLI      │     │  FastAPI    │     │   Vue.js    │     │
│  │  (Click)    │     │ + Auth     │     │     SPA     │     │
│  │             │     │    + SSE    │     │             │     │
│  └─────────────┘     └─────────────┘     └─────────────┘     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Artifact System (CI/CD 风格)                  │  │
│  │   流程产出: 报告/文件/截图 → 存储在 data/artifacts/         │  │
│  │   可下载/可视化                                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## API 端点

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | /api/flows | 列出所有流程 | Token |
| POST | /api/flows | 创建流程 | Token |
| GET | /api/flows/{id} | 获取流程详情 | Token |
| DELETE | /api/flows/{id} | 删除流程 | Token |
| POST | /api/flows/{id}/run | 执行流程 | Token |
| GET | /api/flows/{id}/status | 获取状态 | Token |
| POST | /api/flows/{id}/pause | 暂停 | Token |
| POST | /api/flows/{id}/resume | 恢复 | Token |
| GET | /api/flows/{id}/events | SSE 实时进度 | Token |
| GET | /api/flows/{id}/artifacts | 获取产物列表 | Token |
| GET | /api/flows/{id}/artifacts/{artifact_id}/download | 下载产物 | Token |
| GET | /api/plugins | 列出插件 | Token |
| POST | /api/plugins/install | 安装插件 | Token |

---

## CLI 命令

```bash
madousho run <flow-id>           # 运行流程
madousho run --file <path>      # 运行流程文件
madousho install <git-url>      # 安装插件
madousho config                  # 查看配置
madousho config set <key> <val> # 设置配置
madousho list                    # 列出流程
```

---

## 核心类型定义

```python
class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class StepResult(BaseModel):
    step_id: str
    status: StepStatus
    output: Any = None
    error: str | None = None
    metadata: dict = {}
    created_at: datetime
    completed_at: datetime | None = None

class TaskResult(BaseModel):
    task_id: str
    tag: str | None = None  # 支持打 tag
    status: StepStatus
    output: Any = None
    error: str | None = None

class FlowState(BaseModel):
    flow_id: str
    name: str
    status: StepStatus
    steps: list[StepResult] = []
    context: dict = {}
    created_at: datetime
    updated_at: datetime
```

---

## 错误类定义

```python
class MadoushoError(Exception): ...
class StepError(MadoushoError): ...
class FlowError(MadoushoError): ...
class PluginError(MadoushoError): ...
class ConfigError(MadoushoError): ...
```

---

## 开发阶段

### Phase 1: 核心框架
- Flow Engine (顺序 + 并行 + 条件 + 循环)
- Context Manager (out 访问 + 自动裁剪)
- Plugin System (git clone + pip install)
- Prompt Override System
- REST API + Token Auth + SSE
- CLI
- Vue.js UI
- TinyDB History Storage

### Phase 2: 搜索流程插件 (后续)
- 搜索将通过 Chrome Remote Debugger 抓取网页
- 工具与流程与项目解耦

---

## 示例流程

```python
@flow
def search_report(topic: str):
    keywords = step("generate_keywords", model="haiku", prompt=f"生成关于 {topic} 的搜索关键词")
    results = step("web_search", query=keywords.out[-1])
    summaries = step("parallel_summarize", inputs=results.out, spawn=True)
    return step("generate_report", context=out[-5:])
```

---

## 讨论记录

### Q: 流程定义的首选方式是什么？
A: 混合模式 - 用户可以在 Python 文件中用装饰器定义，也可以在 YAML 中引用 Python 函数

### Q: 上下文传递机制怎么设计？
A: 所有都支持 - 既可以使用 out 全部传入，也可以 out[-1]/out[0:3] 这样精确切片

### Q: 多 Agent/多 Session 协调？
A: 流程决定需要开个新的子任务

### Q: 上下文存储？
A: 内存 + SQLite → 改为 TinyDB (嵌入式 NoSQL)

### Q: 流程持久化？
A: 是，需要 (可暂停/恢复执行)

### Q: 步骤失败时的策略？
A: 由流程制定者自己写错误恢复机制

### Q: 搜索数据源？
A: 后面再做，通过 Chrome Remote Debugger 抓取网页

### Q: Web UI 框架？
A: Vue.js SPA + REST API 后端

### Q: 步骤如何定义？
A: 使用 @step 装饰器定义

### Q: spawn 子任务的并发模型？
A: 一个流程下面有多个步骤，一个步骤支持多个子步骤

### Q: 上下文的数据模型？
A: 流程决定

### Q: 子任务结果如何回到主流程？
A: 提供工具，让流程作者决定

### Q: 实时进度用 SSE 还是 WebSocket？
A: SSE (Server-Sent Events) - 对反代友好

### Q: 插件之间的代码隔离？
A: 目录 + import 隔离

### Q: 插件的依赖管理？
A: pip (requirements.txt)

### Q: step 函数的返回值格式？
A: 显式对象 (StepResult)

### Q: LLM 调用是作为工具还是内置？
A: 工具化 (作为 tool 供 step 调用)

### Q: CLI 命令风格？
A: 子命令模式

### Q: 当 out 超过 LLM context 限制时？
A: 自动裁剪最老的输出

### Q: 流程需要支持哪些控制流？
A: 并行 + 条件 + 循环 + 都要 (完整 DAG)

### Q: 10个并行子任务完成后如何访问结果？
A: TaskResult 数组/Map，支持打 tag

### Q: 插件安全策略？
A: 目录隔离 (用户最佳实践: Docker 中运行)

### Q: 步骤失败时框架如何处理？
A: 作者控制 (框架提供错误类)

### Q: 多个流程可以同时运行吗？
A: 支持并发