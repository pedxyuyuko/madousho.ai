"""API Token 鉴权模块"""

import secrets

from fastapi import HTTPException, Request

from madousho.api.errors import AUTH_REQUIRED, INVALID_TOKEN
from madousho.config import get_config


class AuthError(HTTPException):
    """鉴权异常，携带统一错误格式 detail。"""

    def __init__(self, status_code: int, error_code: str, message: str) -> None:
        super().__init__(
            status_code=status_code, detail={"error": error_code, "message": message}
        )
        self.error_code = error_code
        self.error_message = message


async def verify_token(request: Request) -> None:
    """依赖注入：API Token 鉴权

    从请求头提取 token 并与配置中的 api.token 比较。
    支持 Authorization: Bearer <token> 和 X-API-Token 两种方式。
    OPTIONS 请求（CORS preflight）自动跳过鉴权。

    Raises:
        AuthError: 鉴权失败时抛出 401 异常
    """
    if request.method == "OPTIONS":
        return

    config = get_config()
    config_token = config.api.token

    incoming_token = _extract_bearer(request)
    if incoming_token is None:
        incoming_token = request.headers.get("X-API-Token")

    if incoming_token is None:
        raise AuthError(401, *AUTH_REQUIRED)

    if not secrets.compare_digest(incoming_token, config_token):
        raise AuthError(401, *INVALID_TOKEN)


def _extract_bearer(request: Request) -> str | None:
    """从 Authorization header 提取 Bearer token。"""
    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        return None

    parts = auth_header.split(" ", 1)
    if len(parts) != 2:
        return None

    scheme, token = parts
    if scheme.lower() != "bearer":
        return None

    return token if token else None
