"""统一错误响应模块 - RESTful 格式错误返回"""

from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """RESTful 错误响应模型。

    Attributes:
        error: 机器可读的错误码（如 "unauthorized", "invalid_token"）
        message: 人可读的错误描述
    """

    error: str
    message: str


# 预定义错误常量 (error_code, message)
AUTH_REQUIRED = ("authentication_required", "Valid API token required")
INVALID_TOKEN = ("invalid_token", "Invalid API token")


def error_response(status_code: int, error_code: str, message: str) -> JSONResponse:
    """返回统一格式的错误 JSONResponse。

    Args:
        status_code: HTTP 状态码
        error_code: 机器可读错误码
        message: 人可读错误描述

    Returns:
        JSONResponse 包含 ErrorResponse 格式的内容
    """
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(error=error_code, message=message).model_dump(),
    )
