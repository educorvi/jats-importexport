import asyncio
import logging

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
