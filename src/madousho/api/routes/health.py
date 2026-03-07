from fastapi import APIRouter
from madousho._version import __version__

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok", "version": __version__}
