from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/health")
def health_check():
    """健康检查端点"""
    return {"status": "ok"}
