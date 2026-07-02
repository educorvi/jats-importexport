"""API key authentication dependency."""
import secrets

import httpx
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from api.logging import logger

from .config import APIConfig

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_permission(permission: str = "write"):
    """Return a FastAPI dependency that checks the given permission level.

    Usage::

        @router.get("/items", dependencies=[Depends(require_permission("read"))])
        @router.post("/items", dependencies=[Depends(require_permission("write"))])
        @router.delete("/items", dependencies=[Depends(require_permission("manage"))])
    """

    async def verify_api_key(api_key: str | None = Security(_api_key_header)) -> None:
        """Validate the X-API-Key header for the requested permission.

        When API_KEY is not configured the check is skipped (auth disabled).
        When API_KEY is configured the header must be present and match exactly.
        Raises HTTP 401 on failure.
        """
        if not APIConfig.API_KEY:
            return
        if api_key and secrets.compare_digest(api_key, APIConfig.API_KEY):
            return
        if APIConfig.API_KEY_MANAGER_URL and APIConfig.API_KEY_MANAGER_API_ID:
            request = httpx.post(
                APIConfig.API_KEY_MANAGER_URL.rstrip("/") + "/api/key/check",
                json={"api_id": APIConfig.API_KEY_MANAGER_API_ID, "api_key": api_key, "permission": permission},
            )
            if request.status_code >= 400:
                logger.error("API key check failed: %s", request.json())
                raise HTTPException(status_code=500, detail="Internal error while checking API key")
            if request.json().get("valid") is True:
                return

        raise HTTPException(status_code=401, detail="Invalid or missing API key or insufficient privileges.")

    return verify_api_key
