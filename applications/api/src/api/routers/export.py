import logging
import urllib.parse
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi_cache import FastAPICache
from fastapi_cache.coder import PickleCoder
from fastapi_cache.decorator import cache

from api.models import (
    CacheClearedResponse,
    CacheStatusResponse,
    HtmlDocumentResponse,
    HTTP404NotFound,
    HTTP409Conflict,
    HTTP422UnprocessableEntity,
    JatsDocumentResponse,
    MarkdownDocumentResponse,
    MetadataResponse,
)

from ..auth import require_permission
from ..services.export import get_path_from_webcode, html_export, jats_export, md_export, metadata_export, pdf_export

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


async def export_cache_key_builder(
    func: Callable[..., Any],
    namespace: str = "",
    *,
    request: Request | None = None,
    response: Response | None = None,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    # The endpoint parameters (like 'path') are explicitly inside the 'kwargs' dictionary
    path = await _get_path(kwargs.get(_CACHE_PATH, ""), kwargs.get("webcode", ""))
    path = _get_cache_key_path(path)
    param = _get_cache_query_param(kwargs)
    func_name = getattr(func, "__name__", _CACHE_UNKNOWN_FUNCTION)

    # Format: "namespace:function_name:path:param"
    return f"{namespace}:{func_name}:{path}:{param}"


async def _get_path(path: str | None, webcode: str | None) -> str:
    def exists(param: str | None) -> bool:
        if param is not None and param != "":
            return True
        return False

    if exists(path) == exists(webcode):
        raise HTTPException(status_code=422, detail="Exactly one of 'path' or 'webcode' must be provided.")
    if path:
        return path
    if webcode:
        path = await get_path_from_webcode(webcode)
        return path
    return ""  # unreachable code, but to ensure type checker knows a string is returned


@router.get(
    "/jats",
    operation_id="export_jats",
    response_model=JatsDocumentResponse,
    responses={
        422: {"model": HTTP422UnprocessableEntity},
        404: {"model": HTTP404NotFound},
        409: {"model": HTTP409Conflict},
    },
)
@cache(namespace=_CACHE_NAMESPACE, key_builder=export_cache_key_builder)
async def export_jats(path: str | None = None, webcode: str | None = None):
    return await jats_export(await _get_path(path, webcode))


@router.get(
    "/html",
    operation_id="export_html",
    response_model=HtmlDocumentResponse,
    responses={
        422: {"model": HTTP422UnprocessableEntity},
        404: {"model": HTTP404NotFound},
        409: {"model": HTTP409Conflict},
    },
)
@cache(namespace=_CACHE_NAMESPACE, key_builder=export_cache_key_builder)
async def export_html(path: str | None = None, webcode: str | None = None, include_edit_links: bool = False):
    return await html_export(await _get_path(path, webcode), include_edit_links)


@router.get(
    "/md",
    operation_id="export_md",
    response_model=MarkdownDocumentResponse,
    responses={
        422: {"model": HTTP422UnprocessableEntity},
        404: {"model": HTTP404NotFound},
        409: {"model": HTTP409Conflict},
    },
)
@cache(namespace=_CACHE_NAMESPACE, key_builder=export_cache_key_builder)
async def export_md(path: str | None = None, webcode: str | None = None, include_edit_links: bool = False):
    return await md_export(await _get_path(path, webcode), include_edit_links)


@router.get(
    "/pdf",
    operation_id="export_pdf",
    response_class=Response,
    responses={
        200: {
            "content": {"application/pdf": {"schema": {"type": "string", "format": "binary"}}},
            "description": "PDF file",
        },
        422: {"model": HTTP422UnprocessableEntity},
        404: {"model": HTTP404NotFound},
        409: {"model": HTTP409Conflict},
    },
)
@cache(namespace=_CACHE_NAMESPACE, key_builder=export_cache_key_builder, coder=PickleCoder)
async def export_pdf(path: str | None = None, webcode: str | None = None):
    pdf_content, filename = await pdf_export(await _get_path(path, webcode))
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
        422: {"model": HTTP422UnprocessableEntity},
        404: {"model": HTTP404NotFound},
        409: {"model": HTTP409Conflict},
    },
)
@cache(namespace=_CACHE_NAMESPACE, key_builder=export_cache_key_builder)
async def export_metadata(path: str | None = None, webcode: str | None = None):
    front = await metadata_export(await _get_path(path, webcode))
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
