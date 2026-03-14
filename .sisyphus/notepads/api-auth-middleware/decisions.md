# Decisions Log

## Auth Implementation
- 选择 FastAPI Depends() 而非 Starlette Middleware
- 双 router 架构：public_router + protected_router
- 双 header 支持：Authorization: Bearer 优先，X-API-Token fallback
- 统一错误格式：{"error": "...", "message": "..."}
- 常量时间比较：secrets.compare_digest()
- OPTIONS 请求跳过鉴权
