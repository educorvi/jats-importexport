from typing import Annotated

from fastapi import APIRouter, Header
from fastapi.responses import Response

from ..models import JatsDocumentResponse
from ..services.export import ReturnType, jats_export

router = APIRouter(prefix="/export")


@router.get(
    "/jats",
    response_model=JatsDocumentResponse,
    responses={
        200: {
            "content": {
                "application/xml": {
                    "schema": {"type": "string"},
                    "example": "<article>...</article>",
                }
            }
        }
    },
)
async def export_jats(
    path: str, accept: Annotated[ReturnType | None, Header()] = None
):
    return_type = accept or ReturnType.JSON
    result = jats_export(path, return_type)
    if return_type == ReturnType.XML:
        return Response(content=result, media_type="application/xml")
    return result
