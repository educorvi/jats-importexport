from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse

from api.models import HtmlDocumentResponse, AsyncExportAccepted
from api.routers.export import _resolve_path
from api.services.export_async.export_async import html_export_async

router = APIRouter(prefix="/export/async", tags=["Export Async"])


@router.get(
    "/html",
    operation_id="export_html_async",
    response_model=HtmlDocumentResponse,
    responses={
        202: {"model": AsyncExportAccepted, "description": "In Progress"}
    },
)
async def export_html(background_tasks: BackgroundTasks, path: str = Depends(_resolve_path)):
    result = await html_export_async(path, background_tasks)
    if result:
        return result
    return JSONResponse(
        status_code=202,
        content=AsyncExportAccepted(status="In Progress").model_dump(mode="json"),
    )
