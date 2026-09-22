from fastapi import APIRouter, Depends, Request

from ..models import (
    DeleteArticleResponse,
    HTTP400BadRequest,
    HTTP404NotFound,
    HTTP409Conflict,
    HTTP422UnprocessableEntity,
    HTTP500InternalServerError,
    UpdateArticlesResponse,
)
from ..services.modify import delete_article_service, link_related_articles_service
from .common import resolve_path

router = APIRouter(prefix="/modify", tags=["Modify"])


@router.post(
    "/link-related-articles",
    operation_id="link_related_articles",
    response_model=UpdateArticlesResponse,
    responses={
        400: {"model": HTTP400BadRequest},
        500: {"model": HTTP500InternalServerError},
    },
    summary="Link related articles IDs to the real articles in the storage",
    description=(""),
)
async def link_related_articles(request: Request):
    return await link_related_articles_service()


@router.delete(
    "/article",
    operation_id="delete_article",
    responses={
        200: {"model": DeleteArticleResponse},
        204: {},
        404: {"model": HTTP404NotFound},
        409: {"model": HTTP409Conflict},
        422: {"model": HTTP422UnprocessableEntity},
    },
    summary="Delete an article from the storage",
    description=("Deletes an article and all its associated data from the storage"),
)
async def delete_article(path_tuple: tuple[str, bool] = Depends(resolve_path)):
    path, is_path = path_tuple
    return await delete_article_service(path, is_path)
