from typing import Annotated

from fastapi import APIRouter, Query

from api.models import HTTP500InternalServerError, ListArticlesResponse
from api.services import list as list_service

router = APIRouter(tags=["List"], prefix="/list")


@router.get(
    "/",
    operation_id="list_articles",
    response_model=ListArticlesResponse,
    responses={
        500: {"model": HTTP500InternalServerError},
    },
    description="List articles in the storage system. Filtering is supported.",
)
async def list_articles(
    fachbereiche: Annotated[list[str] | None, Query()] = None,
    sachgebiete: Annotated[list[str] | None, Query()] = None,
    organisationseinheiten: Annotated[list[str] | None, Query()] = None,
    rubriken: Annotated[list[str] | None, Query()] = None,
):
    articles = await list_service.list_articles(fachbereiche, sachgebiete, organisationseinheiten, rubriken)
    return ListArticlesResponse(articles=articles, count=len(articles))
