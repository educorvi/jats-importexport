import logging
import urllib.parse
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends, Request, Response
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

from api.models import (
    CacheClearedResponse,
    CacheStatusResponse,
    HtmlDocumentResponse,
    JatsDocumentResponse,
    MarkdownDocumentResponse,
)

from ..auth import require_permission
from ..services.export import html_export, jats_export, md_export

router = APIRouter(prefix="/export", tags=["Export"])

logger = logging.getLogger(__name__)


def export_cache_key_builder(
    func: Callable[..., Any],
    namespace: str = "",
    *,
    request: Request | None = None,
    response: Response | None = None,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    # The endpoint parameters (like 'path') are explicitly inside the 'kwargs' dictionary
    path = kwargs.get("path", "").lstrip("/").rstrip("/")
    path = urllib.parse.quote_plus(path)

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


@router.get("/html", operation_id="export_html", response_model=HtmlDocumentResponse)
@cache(namespace="export", key_builder=export_cache_key_builder)
async def export_html(path: str):
    return await html_export(path)


@router.get("/md", operation_id="export_md", response_model=MarkdownDocumentResponse)
@cache(namespace="export", key_builder=export_cache_key_builder)
async def export_md(path: str):
    return await md_export(path)


@router.delete(
    "/cache",
    operation_id="clear_export_cache",
    response_model=CacheClearedResponse,
    dependencies=[Depends(require_permission("manage"))],
)
async def clear_export_cache(path: str | None = None):
    if path:
        path = path.lstrip("/").rstrip("/")
        path = urllib.parse.quote_plus(path)
        prefix = FastAPICache.get_prefix()
        # Clear JATS export cache for the specific path
        await FastAPICache.clear(key=f"{prefix}:export:export_jats:{path}")
        # Clear HTML export cache for the specific path
        await FastAPICache.clear(key=f"{prefix}:export:export_html:{path}")
        await FastAPICache.clear(key=f"{prefix}:export:export_md:{path}")
        return CacheClearedResponse(message=f"Cleared cache for {path}")
    else:
        await FastAPICache.clear(namespace="export")
        return CacheClearedResponse(message="Cleared cache")


@router.get("/cache", operation_id="get_cache_status", response_model=CacheStatusResponse)
async def get_cache_status():

    return CacheStatusResponse(enabled=FastAPICache.get_enable(), prefix=FastAPICache.get_prefix())
