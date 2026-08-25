from fastapi import APIRouter, Request

from ..models import (
    UpdateArticlesResponse,
    HTTP400BadRequest,
    HTTP500InternalServerError,
)

from ..services.modify import link_related_articles_service

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
