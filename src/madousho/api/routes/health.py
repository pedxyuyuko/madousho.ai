from fastapi import APIRouter
from madousho._version import __version__

router = APIRouter()

@router.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "version": __version__}