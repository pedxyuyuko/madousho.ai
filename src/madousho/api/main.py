"""FastAPI application entry point for Madousho.ai API."""

from fastapi import FastAPI
from fastapi.responses import FileResponse
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

# 挂载 API 路由
app.include_router(public_router, prefix="/api/v1")
app.include_router(protected_router, prefix="/api/v1")

public_dir = "public/"
index_html = os.path.join(public_dir, "index.html")

if os.path.exists(public_dir):
    assets_dir = os.path.join(public_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/favicon.ico")
    async def favicon():
        favicon_path = os.path.join(public_dir, "favicon.ico")
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path)
        return FileResponse(index_html)

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        return FileResponse(index_html, media_type="text/html")
