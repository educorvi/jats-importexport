import asyncio
import logging

from fastapi import HTTPException

from api.services.common import get_adapter_instance

logger = logging.getLogger(__name__)


async def get_media(path: str) -> tuple[bytes, str]:
    try:
        adapter = get_adapter_instance()
        url = adapter.get_url_from_path(path)
        return await asyncio.to_thread(adapter.download_file, url)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid media path.") from e
    except Exception as e:
        logger.exception("Could not download media file.")
        raise HTTPException(status_code=500, detail="Could not download media file.") from e
