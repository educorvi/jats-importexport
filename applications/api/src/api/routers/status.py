from fastapi import APIRouter

router = APIRouter(tags=["Status"])


@router.get("/status", operation_id="get_status")
async def health_status():
    return {"status": "healthy"}
