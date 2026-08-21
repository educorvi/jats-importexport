from typing import Annotated

from fastapi import APIRouter, Query, Request

from api.config import APIConfig
from api.models import HTTP500InternalServerError, ListArticlesResponse, ListBatching
from api.services import list as list_service

router = APIRouter(tags=["List"], prefix="/list")


@router.get(
    "/",
    operation_id="list_articles",
    response_model=ListArticlesResponse,
    responses={
        500: {"model": HTTP500InternalServerError},
    },
    description="List articles in the storage system. Filtering and batching are supported.",
)
async def list_articles(
    request: Request,
    fachbereiche: Annotated[list[str] | None, Query()] = None,
    sachgebiete: Annotated[list[str] | None, Query()] = None,
    organisationseinheiten: Annotated[list[str] | None, Query()] = None,
    rubriken: Annotated[list[str] | None, Query()] = None,
    batch_start: Annotated[int, Query(ge=0, description="Zero-based index of the first article in the batch")] = 0,
    batch_size: Annotated[
        int,
        Query(
            ge=1,
            le=APIConfig.LIST_BATCH_SIZE,
            description="Number of articles to return",
        ),
    ] = APIConfig.LIST_BATCH_SIZE,
):
    articles, count = await list_service.list_articles(
        fachbereiche,
        sachgebiete,
        organisationseinheiten,
        rubriken,
        batch_start,
        batch_size,
    )
    last_batch_start = ((count - 1) // batch_size) * batch_size if count else 0

    def batch_url(start: int) -> str:
        base_url = request.url.remove_query_params(["batch_start", "batch_size"])
        return str(base_url.include_query_params(batch_start=start, batch_size=batch_size))

    batching = ListBatching(
        current=batch_url(batch_start),
        next=batch_url(batch_start + batch_size) if batch_start + batch_size < count else None,
        previous=batch_url(max(0, batch_start - batch_size)) if batch_start > 0 else None,
        first=batch_url(0),
        last=batch_url(last_batch_start),
    )
    return ListArticlesResponse(
        articles=articles,
        count=count,
        batching=batching,
    )
