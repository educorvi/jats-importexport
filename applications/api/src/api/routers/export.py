from typing import Annotated

from fastapi import APIRouter, Header

from api.services.export import html_export

from ..models import JatsDocumentResponse
from ..services.export import ReturnType, jats_export

router = APIRouter(prefix="/export", tags=["Export"])


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
async def export_jats(path: str, accept: Annotated[ReturnType | None, Header()] = None):
    return_type = accept or ReturnType.JSON
    return jats_export(path, return_type)


@router.get(
    "/html",
    response_model=JatsDocumentResponse,
    responses={200: {"content": {"text/html": {"schema": {"type": "string"}}}}},
)
async def export_html(path: str, accept: Annotated[ReturnType | None, Header()] = None):
    return_type = accept or ReturnType.JSON
    return html_export(path, return_type)
