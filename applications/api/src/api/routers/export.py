import logging

from fastapi import APIRouter, Depends, Response

from api.models import (
    HtmlDocumentResponse,
    HTTP404NotFound,
    HTTP409Conflict,
    HTTP422UnprocessableEntity,
    JatsDocumentResponse,
    MarkdownDocumentResponse,
    MetadataResponse,
    StructureTreeResponse,
)
from api.services.common import resolve_path
from api.services.export import (
    html_export,
    jats_export,
    md_export,
    metadata_export,
    pdf_export,
    structure_tree_export,
    zip_export,
)

router = APIRouter(prefix="/export", tags=["Export"])

logger = logging.getLogger(__name__)


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
async def export_jats(path: str = Depends(resolve_path)):
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
async def export_html(path: str = Depends(resolve_path), include_edit_links: bool = False):
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
async def export_md(path: str = Depends(resolve_path), include_edit_links: bool = False):
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
async def export_pdf(path: str = Depends(resolve_path)):
    pdf_content, filename = await pdf_export(path)
    return Response(
        content=pdf_content,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        media_type="application/pdf",
    )


@router.get(
    "/zip",
    operation_id="export_zip",
    response_class=Response,
    responses={
        200: {
            "content": {"application/zip": {"schema": {"type": "string", "format": "binary"}}},
            "description": "ZIP file",
        },
        404: {"model": HTTP404NotFound},
        409: {"model": HTTP409Conflict},
        422: {"model": HTTP422UnprocessableEntity},
    },
    summary="Export a ZIP file containing the assets (if present) and all export formats",
    description=(
        "The assets (media files) are exported to a media directory (if present)."
        " In the exported JATS, HTML and Markdown files, the links to media files are replaced"
        " with the corresponding paths in the media directory."
        " In the PDF file, the media files are embedded directly."
    ),
)
async def export_zip(path: str = Depends(resolve_path)):
    zip_content, filename = await zip_export(path)
    return Response(
        content=zip_content,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        media_type="application/zip",
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
async def export_metadata(path: str = Depends(resolve_path)):
    front = await metadata_export(path)
    return MetadataResponse(metadata=front)


@router.get(
    "/structure-tree",
    operation_id="structure_tree",
    response_model=StructureTreeResponse,
    responses={
        404: {"model": HTTP404NotFound},
        409: {"model": HTTP409Conflict},
        422: {"model": HTTP422UnprocessableEntity},
    },
)
async def structure_tree(path: str = Depends(resolve_path), max_level: int | None = None):
    toc_entries = await structure_tree_export(path, max_level)
    return StructureTreeResponse.model_validate({"tree": toc_entries})
