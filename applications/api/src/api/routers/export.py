import logging

from fastapi import APIRouter, Depends, HTTPException, Response

from api.models import (
    HtmlDocumentResponse,
    HTTP404NotFound,
    HTTP409Conflict,
    HTTP422UnprocessableEntity,
    JatsDocumentResponse,
    MarkdownDocumentResponse,
    MetadataResponse,
)
from api.services.export import get_path_from_webcode

from ..services.export import html_export, jats_export, md_export, metadata_export, pdf_export

router = APIRouter(prefix="/export", tags=["Export"])

logger = logging.getLogger(__name__)


async def _resolve_path(path: str | None = None, webcode: str | None = None) -> str:
    def exists(param: str | None) -> bool:
        if param is not None and param != "":
            return True
        return False

    if exists(path) == exists(webcode):
        raise HTTPException(status_code=422, detail="Exactly one of 'path' or 'webcode' must be provided.")
    if path:
        return path
    if webcode:
        return await get_path_from_webcode(webcode)
    return ""  # unreachable code, but to ensure type checker knows a string is returned


@router.get(
    "/jats",
    operation_id="export_jats",
    response_model=JatsDocumentResponse,
    responses={
        404: {"model": HTTP404NotFound},
        409: {"model": HTTP409Conflict},
        422: {"model": HTTP422UnprocessableEntity},
    },
)
async def export_jats(path: str = Depends(_resolve_path)):
    return await jats_export(path)


@router.get(
    "/html",
    operation_id="export_html",
    response_model=HtmlDocumentResponse,
    responses={
        404: {"model": HTTP404NotFound},
        409: {"model": HTTP409Conflict},
        422: {"model": HTTP422UnprocessableEntity},
    },
)
async def export_html(path: str = Depends(_resolve_path), include_edit_links: bool = False):
    return await html_export(path, include_edit_links)


@router.get(
    "/md",
    operation_id="export_md",
    response_model=MarkdownDocumentResponse,
    responses={
        404: {"model": HTTP404NotFound},
        409: {"model": HTTP409Conflict},
        422: {"model": HTTP422UnprocessableEntity},
    },
)
async def export_md(path: str = Depends(_resolve_path), include_edit_links: bool = False):
    return await md_export(path, include_edit_links)


@router.get(
    "/pdf",
    operation_id="export_pdf",
    response_class=Response,
    responses={
        200: {
            "content": {"application/pdf": {"schema": {"type": "string", "format": "binary"}}},
            "description": "PDF file",
        },
        404: {"model": HTTP404NotFound},
        409: {"model": HTTP409Conflict},
        422: {"model": HTTP422UnprocessableEntity},
    },
)
async def export_pdf(path: str = Depends(_resolve_path)):
    pdf_content, filename = await pdf_export(path)
    return Response(
        content=pdf_content,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        media_type="application/pdf",
    )


@router.get(
    "/metadata",
    operation_id="export_metadata",
    response_model=MetadataResponse,
    responses={
        404: {"model": HTTP404NotFound},
        409: {"model": HTTP409Conflict},
        422: {"model": HTTP422UnprocessableEntity},
    },
)
async def export_metadata(path: str = Depends(_resolve_path)):
    front = await metadata_export(path)
    return MetadataResponse(metadata=front)
