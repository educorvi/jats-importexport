import logging

from fastapi import APIRouter, Depends
from fastapi.exceptions import RequestValidationError

from api.auth import require_permission
from api.models import CacheClearedResponse, CacheStatus, CacheStatusResponse
from api.services.export import get_path_from_webcode
from api.services.keyval_implementations import EXPORT_CACHE, EXPORT_STATE_CACHE

router = APIRouter(prefix="/cache", tags=["Cache Management"])
logger = logging.getLogger(__name__)


@router.get("/", operation_id="get_cache_status", response_model=CacheStatusResponse)
async def get_cache_status():
    export_data = await EXPORT_CACHE.get_cache_status()
    export_state_data = await EXPORT_STATE_CACHE.get_cache_status()
    return CacheStatusResponse.model_validate(
        {
            EXPORT_CACHE.cache_name: CacheStatus(
                implementation=export_data.implementation, items_in_cache=export_data.items_in_cache
            ),
            EXPORT_STATE_CACHE.cache_name: CacheStatus(
                implementation=export_state_data.implementation, items_in_cache=export_state_data.items_in_cache
            ),
        }
    )


@router.delete(
    "/",
    operation_id="clear_export_cache",
    response_model=CacheClearedResponse,
    description="Clear the export cache for a given path or webcode",
    dependencies=[Depends(require_permission("manage"))],
)
async def clear_export_cache(path: str | None = None, webcode: str | None = None):
    """
    Clear the export cache for a given path or webcode
    """
    if path is not None and webcode is not None:
        raise RequestValidationError("Provide either path or webcode, not both")
    if path is None and webcode is None:
        await EXPORT_CACHE.delete_all()
    else:
        if path is None:
            path = await get_path_from_webcode(webcode or "")
        await EXPORT_CACHE.delete(path, None)
    return CacheClearedResponse(message="Cache cleared")
