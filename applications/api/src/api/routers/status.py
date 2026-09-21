from fastapi import APIRouter

from api.config import APIConfig

router = APIRouter(tags=["Status"])


version = APIConfig.API_VERSION


@router.get("/", operation_id="get_status")
async def health_status():
    return {"status": "healthy", "version": version}


@router.get("/status", operation_id="get_status_old", deprecated=True)
async def health_status_old():
    return {"status": "healthy", "version": version}
