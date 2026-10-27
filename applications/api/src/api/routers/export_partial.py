import logging

from fastapi import APIRouter, Depends, Response

from api.models import (
    HtmlDocumentPartialResponse,
    HTTP400BadRequest,
    HTTP404NotFound,
    HTTP409Conflict,
    HTTP422UnprocessableEntity,
    JatsDocumentResponse,
    MarkdownDocumentResponse,
)
from api.services.common import resolve_path_with_sub_path
from api.services.export_partial import html_export, jats_export, md_export, pdf_export

router = APIRouter(prefix="/export/partial", tags=["Partial Export"])

logger = logging.getLogger(__name__)


@router.get(
    "/jats",
    operation_id="export_partial_jats",
    response_model=JatsDocumentResponse,
    responses={
        400: {"model": HTTP400BadRequest},
        404: {"model": HTTP404NotFound},
        409: {"model": HTTP409Conflict},
        422: {"model": HTTP422UnprocessableEntity},
    },
)
async def export_jats(path_tuple: tuple[str, str] = Depends(resolve_path_with_sub_path)):
    path, sub_path = path_tuple
    return await jats_export(path, sub_path)


@router.get(
    "/html",
    operation_id="export_partial_html",
    response_model=HtmlDocumentPartialResponse,
    responses={
        400: {"model": HTTP400BadRequest},
        404: {"model": HTTP404NotFound},
        409: {"model": HTTP409Conflict},
        422: {"model": HTTP422UnprocessableEntity},
    },
)
async def export_html(
    path_tuple: tuple[str, str] = Depends(resolve_path_with_sub_path), include_edit_links: bool = False
):
    path, sub_path = path_tuple
    return await html_export(path, sub_path, include_edit_links)


@router.get(
    "/md",
    operation_id="export_partial_md",
    response_model=MarkdownDocumentResponse,
    responses={
        400: {"model": HTTP400BadRequest},
        404: {"model": HTTP404NotFound},
        409: {"model": HTTP409Conflict},
        422: {"model": HTTP422UnprocessableEntity},
    },
)
async def export_md(
    path_tuple: tuple[str, str] = Depends(resolve_path_with_sub_path), include_edit_links: bool = False
):
    path, sub_path = path_tuple
    return await md_export(path, sub_path, include_edit_links)


@router.get(
    "/pdf",
    operation_id="export_partial_pdf",
    response_class=Response,
    responses={
        200: {
            "content": {"application/pdf": {"schema": {"type": "string", "format": "binary"}}},
            "description": "PDF file",
        },
        400: {"model": HTTP400BadRequest},
        404: {"model": HTTP404NotFound},
        409: {"model": HTTP409Conflict},
        422: {"model": HTTP422UnprocessableEntity},
    },
)
async def export_pdf(path_tuple: tuple[str, str] = Depends(resolve_path_with_sub_path)):
    path, sub_path = path_tuple
    pdf_content, filename = await pdf_export(path, sub_path)
    return Response(
        content=pdf_content,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        media_type="application/pdf",
    )
