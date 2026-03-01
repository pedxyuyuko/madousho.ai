# madousho.ai
Madousho.ai (魔导书) - Systematic AI Agent Framework

**Madousho.ai** (魔导书) is a systematic AI agent framework designed to solve the problem of random behaviors in traditional AI agents. Unlike existing agents that let the model decide its next step (which leads to unpredictable behavior), Madousho fixes the flow control while letting the model execute predefined steps. This creates controllable AI agents with predictable behavior.

## Setup

To set up this project for development:

1. Create a virtual environment: `python -m venv venv`
2. Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
3. Install in development mode: `pip install -e .`
4. Install development dependencies: `pip install pytest`

## Running Tests

Run tests with: `python -m pytest`

## Installation

Install the package from PyPI:

```bash
pip install madousho-ai
```

## Features

- Fixed flow control with AI-executed steps
- Sequential, parallel, conditional, and loop constructs
- Plugin system with Git-based installation
- Context management with automatic trimming
- Flow persistence with pause/resume functionality
- Real-time progress updates via Server-Sent Events
- Artifact system similar to CI/CD pipelines
- REST API with token authentication
- Web UI with Vue.js

## CLI Commands

The framework provides a comprehensive CLI for managing flows and plugins:

```bash
madousho run <flow-id>           # Run a flow
madousho run --file <path>      # Run a flow from a file
madousho install <git-url>      # Install a plugin
madousho config                  # View configuration
madousho config set <key> <val> # Set configuration
madousho list                    # List available flows
```

## Basic Usage

Define flows using decorators:

```python
@flow
def search_report(topic: str):
    keywords = step("generate_keywords", model="haiku", prompt=f"Generate search keywords for {topic}")
    results = step("web_search", query=keywords.out[-1])
    summaries = step("parallel_summarize", inputs=results.out, spawn=True)
    return step("generate_report", context=out[-5:])
```

## Architecture

Madousho follows a modular architecture:

- **Core Engine**: Flow execution with DAG support

- **Context Manager**: Handles state and output access with automatic trimming

- **Plugin System**: Git-based plugin installation with dependency management

- **Storage**: TinyDB for flow persistence

- **API Layer**: FastAPI with authentication and SSE

- **Frontend**: Vue.js SPA for flow management

## Development

To contribute to this project, follow the setup instructions below. This will install the package in development mode with all dependencies.

### Prerequisites

- Python 3.10+
- Git

### Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install in development mode: `pip install -e .`
5. Install development dependencies: `pip install pytest`

## Running Tests

Run tests with: `python -m pytest`
