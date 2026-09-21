from fastapi import APIRouter, BackgroundTasks, Depends, Response
from fastapi.responses import JSONResponse

from api.models import AsyncExportAccepted, HtmlDocumentResponse
from api.routers.export import _resolve_path
from api.services.export_async.export_async import html_export_async, pdf_export_async

router = APIRouter(prefix="/export/async", tags=["Export Async"])


@router.get(
    "/html",
    operation_id="export_html_async",
    response_model=HtmlDocumentResponse,
    responses={202: {"model": AsyncExportAccepted, "description": "In Progress"}},
)
async def export_html(background_tasks: BackgroundTasks, path: str = Depends(_resolve_path)):
    # TODO Add support for edit links
    result = await html_export_async(path, background_tasks)
    if result:
        return result
    return JSONResponse(
        status_code=202,
        content=AsyncExportAccepted(status="In Progress").model_dump(mode="json"),
    )


@router.get(
    "/pdf",
    operation_id="export_pdf_async",
    response_class=Response,
    responses={
        200: {
            "content": {"application/pdf": {"schema": {"type": "string", "format": "binary"}}},
            "description": "PDF file",
        },
        202: {"model": AsyncExportAccepted, "description": "In Progress"},
    },
)
async def export_pdf(background_tasks: BackgroundTasks, path: str = Depends(_resolve_path)):
    result = await pdf_export_async(path, background_tasks)
    if result is not None:
        content, filename = result
        return Response(
            content=content,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            media_type="application/pdf",
        )
    return JSONResponse(
        status_code=202,
        content=AsyncExportAccepted(status="In Progress").model_dump(mode="json"),
    )
