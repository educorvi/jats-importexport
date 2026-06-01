"""API key authentication dependency."""

import secrets

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from .config import APIConfig

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Security(_api_key_header)) -> None:
    """Validate the X-API-Key header.

    When API_KEY is not configured the check is skipped (auth disabled).
    When API_KEY is configured the header must be present and match exactly.
    Raises HTTP 401 on failure.
    """
    if not APIConfig.API_KEY:
        return
    if not api_key or not secrets.compare_digest(api_key, APIConfig.API_KEY):
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
