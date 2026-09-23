from fastapi import APIRouter, BackgroundTasks, Depends, Response
from fastapi.responses import JSONResponse

from api.models import AsyncExportAccepted, HtmlDocumentResponse
from api.services.common import resolve_path
from api.services.export_async.export_async import async_export_status, html_export_async, pdf_export_async
from api.services.keyval_implementations import ExportState, ExportType

router = APIRouter(prefix="/export/async", tags=["Export Async"])


@router.get(
    "/status",
    operation_id="export_status_async",
    response_model=AsyncExportAccepted,
    responses={
        202: {"model": AsyncExportAccepted, "description": "In Progress"},
        500: {"description": "Failed"},
        404: {"description": "No export was started yet"},
    },
)
async def export_status(export_type: ExportType, path: str = Depends(resolve_path)):
    state = await async_export_status(path, export_type)
    if state is None:
        return JSONResponse(
            status_code=404,
            content={"status": "Not Found"},
        )
    if state == ExportState.FAILED:
        return JSONResponse(
            status_code=500,
            content={"status": "Failed"},
        )
    if state == ExportState.RUNNING:
        return JSONResponse(
            status_code=202,
            content=AsyncExportAccepted(status="In Progress").model_dump(mode="json"),
        )
    return JSONResponse(
        status_code=200,
        content=AsyncExportAccepted(status="Completed").model_dump(mode="json"),
    )


@router.get(
    "/html",
    operation_id="export_html_async",
    response_model=HtmlDocumentResponse,
    responses={202: {"model": AsyncExportAccepted, "description": "In Progress"}},
)
async def export_html(
    background_tasks: BackgroundTasks, path: str = Depends(resolve_path), include_edit_links: bool = False
):
    result = await html_export_async(path, background_tasks, include_edit_links)
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
async def export_pdf(background_tasks: BackgroundTasks, path: str = Depends(resolve_path)):
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
