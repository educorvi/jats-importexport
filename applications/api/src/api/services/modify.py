from ..models import UpdateArticlesResponse
from .common import get_adapter_instance


async def link_related_articles_service() -> UpdateArticlesResponse:
    adapter_instance = get_adapter_instance()
    urls = adapter_instance.link_related_articles()
    return UpdateArticlesResponse(updated_articles=urls)
