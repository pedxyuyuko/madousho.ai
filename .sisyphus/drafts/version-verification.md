# 验证版本管理配置

## TL;DR

> 确认 `_version.py` 不应该被 git 追踪，CI build 时会自动生成

---

## 验证步骤

### 1. 确认 `.gitignore` 已配置

```bash
grep "_version.py" .gitignore
# 应输出：src/madousho/_version.py
```

### 2. 确认文件未被追踪

```bash
git status --short src/madousho/_version.py
# 应输出：空（无输出表示未被追踪）
```

### 3. 验证 build 时自动生成

```bash
# 删除现有 _version.py
rm -f src/madousho/_version.py

# 重新 build
python -m build

# 验证生成
ls -la src/madousho/_version.py  # 应存在
python -c "import madousho; print(madousho.__version__)"  # 应输出版本号
```

---

## 结论

✅ **`_version.py` 不应该被 git 追踪**
- `.gitignore` 已正确配置
- CI/CD build 时会自动生成
- 版本来自 git tags，不是文件本身
