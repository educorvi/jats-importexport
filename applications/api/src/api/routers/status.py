from fastapi import APIRouter

router = APIRouter(tags=["Status"])


@router.get("/status")
async def health_status():
    return {"status": "healthy"}
