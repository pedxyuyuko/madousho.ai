## 2026-03-14 - 修改 serve 命令添加 uvicorn HTTP 服务器

### 修改内容

在 `src/madousho/commands/serve.py` 中添加了 uvicorn HTTP 服务器启动逻辑：

1. **添加导入**: `import uvicorn` (第 7 行)
2. **添加 reload 参数**: 
   ```python
   def serve(
       ctx: typer.Context,
       reload: bool = typer.Option(False, "--reload", help="Enable auto-reload mode"),
   ):
   ```
3. **在 init_database() 后启动服务器**:
   ```python
   config = get_config()
   logger.info(f"Starting HTTP server on http://{config.api.host}:{config.api.port}")
   uvicorn.run(
       "madousho.api.main:app",
       host=config.api.host,
       port=config.api.port,
       reload=reload,
   )
   ```

### 关键点

- 使用 `"madousho.api.main:app"` 作为 uvicorn 应用路径（不是 `src.madousho`）
- `reload` 参数默认值为 `False`
- host 和 port 从配置读取 (`config.api.host` 和 `config.api.port`)
- 保留所有现有数据库初始化逻辑
- 启动前输出日志显示服务器地址

### 验证结果

```bash
# 1. 模块导入成功
python -c "from madousho.commands.serve import serve; print('OK')"
# 输出：OK

# 2. 帮助信息显示 --reload 选项
madousho serve --help
# 输出：--reload  Enable auto-reload mode

# 3. 配置可访问
python -c "from madousho.config import get_config; c = get_config(); print(c.api.host, c.api.port)"
# 输出：0.0.0.0 8000
```

### 注意事项

- uvicorn 已在 `pyproject.toml` 的 dependencies 中声明：`uvicorn[standard]>=0.27.0`
- LSP 可能在 uv sync 之前报告导入错误，这是正常的
- 确保在 `init_database()` **之后** 启动 uvicorn，保证数据库已初始化
