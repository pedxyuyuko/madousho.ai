# 修复 PEP 440 版本管理

## TL;DR

> **目标**: 修复版本管理，使其完全符合 PEP 440 规范
> 
> **修改**: 
> - `src/madousho/__init__.py` - 从 `_version.py` 导入版本
> - Git tag 修复（用户手动执行）
> 
> **预计时间**: 快速

---

## Context

### 当前问题

1. **`__init__.py` 硬编码版本**: `__version__ = "0.1.0"` 与 setuptools_scm 生成的 `0.0.1.dev29` 不一致
2. **Git tag 不规范**: `v0.0.1.dev0` 不应带 `.dev0` 后缀，应该是 `v0.0.1`

### PEP 440 要求

- 开发版本格式：`N.N.N.devN`
- Tag 不应包含 `.devN` 后缀
- 版本应从 `_version.py` 导入，不应硬编码

---

## Work Objectives

### 核心目标
修复版本导入逻辑，使 `__version__` 从 setuptools_scm 生成的 `_version.py` 导入

### 具体交付物
- `src/madousho/__init__.py` - 正确的版本导入逻辑
- Git tag 修复指南

---

## Verification Strategy

### 测试决策
- **基础设施**: pytest 已配置
- **测试**: 无（简单修改，通过导入验证）

### QA 场景

**场景 1: 验证版本导入成功**
```
工具: Bash
步骤:
  1. cd /home/yuyuko/OtherProjects/madousho_ai
  2. python -c "import madousho; print(madousho.__version__)"
预期: 输出版本号如 `0.0.1.dev29`（不是硬编码的 `0.1.0`）
```

**场景 2: 验证 `_version.py` 存在**
```
工具: Bash
步骤:
  1. ls -la src/madousho/_version.py
预期: 文件存在
```

---

## Execution Strategy

### 单任务执行

**Task 1: 修复 `__init__.py` 版本导入**

**What to do**:
- 修改 `src/madousho/__init__.py`
- 添加 try/except 导入逻辑
- 回退到 `"unknown"` 当 `_version.py` 不可用时

**Recommended Agent Profile**:
- **Category**: `quick` - 单文件小修改
- **Skills**: `[]` - 不需要特殊技能

**Parallelization**:
- **Can Run In Parallel**: NO
- **Sequential**: 唯一任务

**References**:
- `src/madousho/__init__.py` - 当前文件（1 行，硬编码版本）
- `src/madousho/_version.py` - setuptools_scm 生成的版本文件

**Acceptance Criteria**:
- [ ] `__init__.py` 包含 try/except 导入逻辑
- [ ] 导入 `_version.__version__`
- [ ] 有回退到 `"unknown"`

**QA Scenarios**:

```
Scenario: 验证版本导入
  Tool: Bash
  Steps:
    1. python -c "from madousho import __version__; print(__version__)"
  Expected Result: 输出版本号（如 `0.0.1.dev29`），不是 `0.1.0`
  Evidence: .sisyphus/evidence/task-1-version-import.txt
```

---

## Final Verification

- [ ] F1. 版本导入验证 - `python -c "import madousho; print(__version__)"`
- [ ] F2. 代码无语法错误 - `python -m py_compile src/madousho/__init__.py`

---

## Commit Strategy

- **1**: `fix(version): import version from _version.py instead of hardcoded`
  - Files: `src/madousho/__init__.py`
  - Pre-commit: `python -m py_compile src/madousho/__init__.py`

---

## Success Criteria

### 验证命令
```bash
python -c "import madousho; print(madousho.__version__)"  # 应输出 0.0.1.devN
```

### 最终检查清单
- [ ] `__init__.py` 使用 try/except 导入
- [ ] 版本不是硬编码的 `0.1.0`
- [ ] 有回退逻辑

---

## Git Tag 修复指南（用户手动执行）

```bash
# 1. 删除错误的 tag
git tag -d v0.0.1.dev0
git push origin :refs/tags/v0.0.1.dev0

# 2. 创建正确的 tag（不带 .dev0）
git tag v0.0.1

# 3. 推送 tag
git push origin v0.0.1

# 4. 验证版本
python -c "import madousho; print(madousho.__version__)"  # 应输出 0.0.1
```
