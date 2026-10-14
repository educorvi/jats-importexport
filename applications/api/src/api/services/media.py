import asyncio
import logging

from fastapi import HTTPException

from api.services.common import get_adapter_instance

logger = logging.getLogger(__name__)


async def get_media(path: str, filename: str, signature: str) -> tuple[bytes, str]:
    try:
        adapter = get_adapter_instance()
        return await asyncio.to_thread(adapter.get_media, path, filename, signature)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid path, filename or signature.") from e
    except Exception as e:
        logger.exception("Could not download media file.")
        raise HTTPException(status_code=500, detail="An error occurred while downloading the media file.") from e
