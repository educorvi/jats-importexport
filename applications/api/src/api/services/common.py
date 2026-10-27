import asyncio
import base64
import logging
import os
from collections.abc import Callable
from urllib.parse import parse_qs, urlparse

from fastapi import HTTPException
from jats_storage_adapters.errors import DuplicateException, PathNotFoundExpection
from jats_storage_adapters.interface import AvailableStorageAdapters, StorageAdapter

from api.config import StorageConfig

logger = logging.getLogger(__name__)

STORAGE_ADAPTER = StorageConfig.STORAGE_ADAPTER


def get_adapter_instance() -> StorageAdapter:
    try:
        return AvailableStorageAdapters.create_instance_by_name(STORAGE_ADAPTER)
    except ValueError:
        logger.error("Could not connect to the storage adapter.", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not connect to the storage adapter.")


async def get_path_from_webcode(webcode: str, adapter: StorageAdapter | None = None) -> str:
    try:
        adapter = adapter or get_adapter_instance()
        path = await asyncio.to_thread(adapter.get_path_from_webcode, webcode)
        if not path:
            raise HTTPException(status_code=404, detail=f"Document not found for webcode: {webcode}")
        return path
    except HTTPException:
        raise
    except PathNotFoundExpection:
        raise HTTPException(status_code=404, detail=f"Document not found for webcode: {webcode}")
    except DuplicateException:
        raise HTTPException(status_code=409, detail=f"Multiple documents found for webcode: {webcode}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading document: {e}")


async def resolve_path(path: str | None = None, webcode: str | None = None) -> str:
    def exists(param: str | None) -> bool:
        if param is not None and param != "":
            return True
        return False

    if exists(path) == exists(webcode):
        raise HTTPException(status_code=422, detail="Exactly one of 'path' or 'webcode' must be provided.")
    if path:
        return path
    if webcode:
        return await get_path_from_webcode(webcode)
    return ""  # unreachable code, but to ensure type checker knows a string is returned


async def resolve_path_with_sub_path(
    path: str | None = None, webcode: str | None = None, sub_path: str = ""
) -> tuple[str, str]:
    resolved_path = await resolve_path(path, webcode)
    if not sub_path:
        raise HTTPException(status_code=422, detail="Sub-path must be provided and non-empty.")
    return resolved_path, sub_path


def get_media_downloader(storage_adapter: StorageAdapter) -> Callable[[str], tuple[bytes, str]]:
    """Returns a callable that downloads media from the signed API URL or a StorageAdapter URL."""
    IEH_BASE_URL = os.environ.get("IEH_BASE_URL")
    if IEH_BASE_URL is None:
        raise OSError("IEH_BASE_URL environment variable is not set.")
    parsed_base_url = urlparse(IEH_BASE_URL)

    def downloader(url: str) -> tuple[bytes, str]:
        parsed_url = urlparse(url)
        if (
            parsed_url.scheme == parsed_base_url.scheme
            and parsed_url.netloc == parsed_base_url.netloc
            and parsed_url.path.startswith(parsed_base_url.path)
        ):
            query = parse_qs(parsed_url.query)
            required = ("path", "filename", "signature")
            values = {key: query.get(key, []) for key in required}
            if any(len(value) != 1 or not value[0] for value in values.values()):
                raise ValueError(f"Media URL is missing required signed parameters: {url}")
            return storage_adapter.get_media(
                values["path"][0],
                values["filename"][0],
                values["signature"][0],
            )
        else:
            return storage_adapter.download_file(url)

    return downloader


def pdf_replace_media_links_callback(url: str, media: tuple[bytes, str] | None = None) -> str:
    """Replaces media links in PDF exports with base64-encoded data URLs."""
    if media is None:
        logger.warning(f"No media content available for URL: {url}")
        return url
    content, content_type = media
    encoded = base64.b64encode(content).decode("utf-8")
    return f"data:{content_type};base64,{encoded}"
