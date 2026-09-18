from api.services.export import get_path_from_webcode
from api.services.export_async.keyval_implementations import KeyValImplementation, ASYNC_EXPORT_CACHE
import logging
import urllib.parse
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi_cache import FastAPICache
from fastapi_cache.coder import PickleCoder

from api.cache_metrics import export_cache
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
    path = _get_cache_key_path(kwargs.get(_CACHE_PATH, ""))
    param = _get_cache_query_param(kwargs)
    func_name = getattr(func, "__name__", _CACHE_UNKNOWN_FUNCTION)

    # Format: "namespace:function_name:path:param"
    return f"{namespace}:{func_name}:{path}:{param}"


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
        return webcode
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
@export_cache(namespace=_CACHE_NAMESPACE, key_builder=export_cache_key_builder)
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
@export_cache(namespace=_CACHE_NAMESPACE, key_builder=export_cache_key_builder)
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
@export_cache(namespace=_CACHE_NAMESPACE, key_builder=export_cache_key_builder)
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
@export_cache(namespace=_CACHE_NAMESPACE, key_builder=export_cache_key_builder, coder=PickleCoder)
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
@export_cache(namespace=_CACHE_NAMESPACE, key_builder=export_cache_key_builder)
async def export_metadata(path: str = Depends(_resolve_path)):
    front = await metadata_export(path)
    return MetadataResponse(metadata=front)


@router.delete(
    "/cache",
    operation_id="clear_export_cache",
    response_model=CacheClearedResponse,
    dependencies=[Depends(require_permission("manage"))],
)
async def clear_export_cache(path: str | None = None, webcode: str | None = None):
    """
    Clear the export cache for a given path and / or webcode
    """
    if path is not None or webcode is not None:
        key_list = []
        message = "Cleared cache for "
        if path is not None:
            key_list.extend(_get_clear_keys(path))
            message += f"path={path} "
        if webcode is not None:
            key_list.extend(_get_clear_keys(webcode))
            message += f"webcode={webcode}"

        for key in key_list:
            await FastAPICache.clear(key=key)
        
        if not path and webcode is not None:
            path = await get_path_from_webcode(webcode)
        if path:
            ASYNC_EXPORT_CACHE.delete(path, None)

        return CacheClearedResponse(message=message.strip())
    else:
        await FastAPICache.clear(namespace=_CACHE_NAMESPACE)
        return CacheClearedResponse(message="Cleared cache")


@router.get("/cache", operation_id="get_cache_status", response_model=CacheStatusResponse)
async def get_cache_status():
    return CacheStatusResponse(enabled=FastAPICache.get_enable(), prefix=FastAPICache.get_prefix())
