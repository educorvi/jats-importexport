import asyncio

from fastapi import HTTPException, Response
from jats_storage_adapters.errors import DuplicateException, PathNotFoundExpection

from ..models import DeleteArticleResponse, UpdateArticlesResponse
from .common import get_adapter_instance


async def link_related_articles_service() -> UpdateArticlesResponse:
    adapter_instance = get_adapter_instance()

    try:
        urls = await asyncio.to_thread(adapter_instance.link_related_articles)
        return UpdateArticlesResponse(updated_articles=urls)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error linking related articles: {e}")


async def delete_article_service(path: str) -> DeleteArticleResponse | Response:
    adapter_instance = get_adapter_instance()

    try:
        errors = await asyncio.to_thread(adapter_instance.delete_article, path)
        if errors:
            return DeleteArticleResponse(errors=errors)
        return Response(status_code=204)
    except PathNotFoundExpection as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {e}")
    except DuplicateException as e:
        raise HTTPException(status_code=409, detail=f"More than one document found for {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting article: {e}")
