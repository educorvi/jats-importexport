from typing import Annotated

from fastapi import APIRouter, Request, Query

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
async def list_all_articles(
    fachbereiche: Annotated[list[str] | None, Query()] = None,
    sachgebiete: Annotated[list[str] | None, Query()] = None,
    organisationseinheiten: Annotated[list[str] | None, Query()] = None,
):
    articles = await list_articles(fachbereiche, sachgebiete, organisationseinheiten)
    return ListArticlesResponse(articles=articles, count=len(articles))
