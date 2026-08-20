from fastapi import APIRouter

from api.config import APIConfig

router = APIRouter(tags=["Status"])


version = APIConfig.API_VERSION

@router.get("/status", operation_id="get_status")
async def health_status():
    return {"status": "healthy", "version": version}
