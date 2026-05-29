from api.models import HtmlDocumentResponse
from fastapi import APIRouter, Request

from api.services.export import get_return_type, html_export

from ..models import JatsDocumentResponse
from ..services.export import jats_export

router = APIRouter(prefix="/export", tags=["Export"])


@router.get(
    "/jats",
    operation_id="export_jats",
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
async def export_jats(request: Request, path: str):
    return jats_export(path, get_return_type(request))


@router.get(
    "/html",
    operation_id="export_html",
    response_model=HtmlDocumentResponse,
    responses={200: {"content": {"text/html": {"schema": {"type": "string"}}}}},
)
async def export_html(request: Request, path: str):
    return html_export(path, get_return_type(request))
