import asyncio

from fastapi import HTTPException

from ..models import UpdateArticlesResponse
from .common import get_adapter_instance


async def link_related_articles_service() -> UpdateArticlesResponse:
    adapter_instance = get_adapter_instance()

    try:
        urls = await asyncio.to_thread(adapter_instance.link_related_articles)
        return UpdateArticlesResponse(updated_articles=urls)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error linking related articles: {e}")
