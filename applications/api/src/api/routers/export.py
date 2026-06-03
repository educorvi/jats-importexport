from api.models import HtmlDocumentResponse, JatsDocumentResponse
import logging
from collections.abc import Callable
from typing import Any, Optional

from fastapi import APIRouter, Request, Response
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

from ..services.export import html_export, jats_export

router = APIRouter(prefix="/export", tags=["Export"])

logger = logging.getLogger(__name__)

def export_cache_key_builder(
    func: Callable[..., Any],
    namespace: str = "",
    *,
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    # The endpoint parameters (like 'path') are explicitly inside the 'kwargs' dictionary
    path = kwargs.get("path", "")

    # Format: "namespace:function_name:path"
    func_name = getattr(func, "__name__", "unknown_function")

    return f"{namespace}:{func_name}:{path}"

@router.get(
    "/jats",
    operation_id="export_jats",
    response_model=JatsDocumentResponse,
)
@cache(namespace="export", key_builder=export_cache_key_builder)
async def export_jats(path: str):
    return await jats_export(path)


@router.get(
    "/html",
    operation_id="export_html",
    response_model=HtmlDocumentResponse
)
@cache(namespace="export", key_builder=export_cache_key_builder)
async def export_html(path: str):
    return await html_export(path)


@router.delete("/cache", operation_id="clear_export_cache")
async def clear_export_cache(path: Optional[str] = None):
    if path:
        prefix = FastAPICache.get_prefix()
        # Clear JATS export cache for the specific path
        await FastAPICache.clear(key=f"{prefix}:export:export_jats:{path}")
        # Clear HTML export cache for the specific path
        await FastAPICache.clear(key=f"{prefix}:export:export_html:{path}")
        return {"message": f"Export cache cleared for path: {path}"}
    else:
        await FastAPICache.clear(namespace="export")
        return {"message": "Export cache cleared"}


@router.get("/cache", operation_id="get_cache_status")
async def get_cache_status():
    cache_info = {
        "enabled": FastAPICache.get_enable(),
        "prefix": FastAPICache.get_prefix(),
        "backend_type": FastAPICache._backend.__class__.__name__ if FastAPICache._backend else "None",
    }

    return cache_info

