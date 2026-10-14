from fastapi import APIRouter, Response

from api.config import APIConfig
from api.models import HTTP400BadRequest, HTTP500InternalServerError
from api.services.media import get_media as download_media

router = APIRouter(prefix="/media", tags=["Media"])


version = APIConfig.API_VERSION


@router.get(
    "/",
    operation_id="get_media",
    response_class=Response,
    responses={
        200: {
            "content": {"image/*": {"schema": {"type": "string", "format": "binary"}}},
            "description": "Media file",
        },
        400: {"model": HTTP400BadRequest},
        500: {"model": HTTP500InternalServerError},
    },
)
async def get_media(path: str, filename: str, signature: str):
    content, content_type = await download_media(path, filename, signature)
    return Response(content=content, media_type=content_type)
