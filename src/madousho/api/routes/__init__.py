"""API 路由定义 - 公开路由和受保护路由"""

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from madousho.api.auth import verify_token

bearer_scheme = HTTPBearer(description="API Token", auto_error=False)

public_router = APIRouter()

protected_router = APIRouter(
    dependencies=[Depends(bearer_scheme), Depends(verify_token)]
)


@public_router.get("/health")
def health_check():
    """健康检查端点"""
    return {"status": "ok"}


@protected_router.get("/protected")
def protected_endpoint():
    """受保护端点示例（验证鉴权功能）"""
    return {"message": "authenticated"}
