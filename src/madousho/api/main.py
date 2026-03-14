"""FastAPI application entry point for Madousho.ai API."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from madousho._version import __version__
from madousho.api.routes import protected_router, public_router

app = FastAPI(
    title="Madousho.ai API",
    version=__version__,
    contact={"url": "https://github.com/pedxyuyuko/madousho.ai"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    swagger_ui_parameters={"persistAuthorization": True},
)

# 挂载 SPA 静态文件
public_dir = "public/"
if os.path.exists(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="static")

# 挂载 API 路由
app.include_router(public_router, prefix="/api/v1")
app.include_router(protected_router, prefix="/api/v1")
