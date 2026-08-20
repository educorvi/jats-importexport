from fastapi import APIRouter

from api.models import HTTP500InternalServerError, ListArticlesResponse
from api.services.list import list_articles

router = APIRouter(tags=["list"], prefix="/list")

@router.get(
    "/",
    operation_id="list_all_articles",
    response_model=ListArticlesResponse,
    responses={
        500: {"model": HTTP500InternalServerError},
    },
)
async def list_all_articles():
    articles = await list_articles()
    return ListArticlesResponse(articles=articles)