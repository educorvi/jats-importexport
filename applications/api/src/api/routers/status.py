from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def health_status():
    return {"status": "healthy"}
