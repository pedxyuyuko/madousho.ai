# Learnings Log

## [2026-03-14] Plan Init: api-auth-middleware
- 项目使用 FastAPI Depends() 模式做依赖注入（参考 get_db()）
- 现有测试用 TestClient(app) + pytest class-based 组织
- ApiConfig.token 空值时自动生成 32 字符 hex
- main.py 存在 import 路径 bug（src.madousho 应为 madousho）— 可选修复
