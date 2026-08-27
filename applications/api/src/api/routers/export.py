import logging
import urllib.parse
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends, Request, Response
from fastapi_cache import FastAPICache
from fastapi_cache.coder import PickleCoder
from fastapi_cache.decorator import cache

from api.models import (
    CacheClearedResponse,
    CacheStatusResponse,
    HtmlDocumentResponse,
    JatsDocumentResponse,
    MarkdownDocumentResponse,
    MetadataResponse,
)

from ..auth import require_permission
from ..services.export import html_export, jats_export, md_export, metadata_export, pdf_export

router = APIRouter(prefix="/export", tags=["Export"])

logger = logging.getLogger(__name__)


_CACHE_NAMESPACE = "export"
_CACHE_UNKNOWN_FUNCTION = "unknown_function"
_CACHE_FUNCTIONS = ["export_jats", "export_html", "export_md", "export_pdf", "export_metadata"] + [
    _CACHE_UNKNOWN_FUNCTION
]
_CACHE_PATH = "path"
_CACHE_QUERY_PARAM = "include_edit_links"


def _get_cache_key_path(path: str) -> str:
    path = path.lstrip("/").rstrip("/")
    return urllib.parse.quote_plus(path)


def _get_cache_query_param(kwargs: dict[str, Any]) -> str:
    param = {_CACHE_QUERY_PARAM: kwargs.get(_CACHE_QUERY_PARAM, False)}
    return urllib.parse.urlencode(param)


def _get_clear_keys(path: str) -> list[str]:
    path = _get_cache_key_path(path)
    prefix = FastAPICache.get_prefix()
    keys = []
    for func_name in _CACHE_FUNCTIONS:
        key = f"{prefix}:{_CACHE_NAMESPACE}:{func_name}:{path}:"
        keys.append(f"{key}{_get_cache_query_param({_CACHE_QUERY_PARAM: True})}")
        keys.append(f"{key}{_get_cache_query_param({_CACHE_QUERY_PARAM: False})}")
    return keys


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
    path = _get_cache_key_path(kwargs.get(_CACHE_PATH, ""))
    param = _get_cache_query_param(kwargs)
    func_name = getattr(func, "__name__", _CACHE_UNKNOWN_FUNCTION)

    # Format: "namespace:function_name:path:param"
    return f"{namespace}:{func_name}:{path}:{param}"


@router.get(
    "/jats",
    operation_id="export_jats",
    response_model=JatsDocumentResponse,
)
@cache(namespace=_CACHE_NAMESPACE, key_builder=export_cache_key_builder)
async def export_jats(path: str):
    return await jats_export(path)


@router.get("/html", operation_id="export_html", response_model=HtmlDocumentResponse)
@cache(namespace=_CACHE_NAMESPACE, key_builder=export_cache_key_builder)
async def export_html(path: str, include_edit_links: bool = False):
    return await html_export(path, include_edit_links)


@router.get("/md", operation_id="export_md", response_model=MarkdownDocumentResponse)
@cache(namespace=_CACHE_NAMESPACE, key_builder=export_cache_key_builder)
async def export_md(path: str, include_edit_links: bool = False):
    return await md_export(path, include_edit_links)


@router.get(
    "/pdf",
    operation_id="export_pdf",
    response_class=Response,
    responses={
        200: {
            "content": {"application/pdf": {"schema": {"type": "string", "format": "binary"}}},
            "description": "PDF file",
        }
    },
)
@cache(namespace=_CACHE_NAMESPACE, key_builder=export_cache_key_builder, coder=PickleCoder)
async def export_pdf(path: str):
    pdf_content, filename = await pdf_export(path)
    return Response(
        content=pdf_content,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        media_type="application/pdf",
    )


@router.get("/metadata", operation_id="export_metadata", response_model=MetadataResponse)
@cache(namespace=_CACHE_NAMESPACE, key_builder=export_cache_key_builder)
async def export_metadata(path: str):
    front = await metadata_export(path)
    return MetadataResponse(metadata=front)


@router.delete(
    "/cache",
    operation_id="clear_export_cache",
    response_model=CacheClearedResponse,
    dependencies=[Depends(require_permission("manage"))],
)
async def clear_export_cache(path: str | None = None):
    if path is not None:
        key_list = _get_clear_keys(path)
        for key in key_list:
            await FastAPICache.clear(key=key)
        return CacheClearedResponse(message=f"Cleared cache for {path}")
    else:
        await FastAPICache.clear(namespace=_CACHE_NAMESPACE)
        return CacheClearedResponse(message="Cleared cache")


@router.get("/cache", operation_id="get_cache_status", response_model=CacheStatusResponse)
async def get_cache_status():

    return CacheStatusResponse(enabled=FastAPICache.get_enable(), prefix=FastAPICache.get_prefix())
