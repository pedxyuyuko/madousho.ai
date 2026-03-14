"""FastAPI application entry point for Madousho.ai API."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from src.madousho._version import __version__
from src.madousho.api.routes import api_router

app = FastAPI(
    title="Madousho.ai API",
    version=__version__,
    contact={"url": "https://github.com/pedxyuyuko/madousho.ai"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)

# 挂载 SPA 静态文件
public_dir = "public/"
if os.path.exists(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="static")

# 挂载 API 路由
app.include_router(api_router, prefix="/api/v1")
