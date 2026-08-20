import asyncio

from fastapi import HTTPException

from api.services.common import get_adapter_instance


async def list_articles(
    fachbereiche: list[str] | None = None,
    sachgebiete: list[str] | None = None,
    organisationseinheiten: list[str] | None = None,
) -> list[str]:
    try:
        adapter_instance = get_adapter_instance()
        return await asyncio.to_thread(
            adapter_instance.list_articles,
            fachbereiche,
            sachgebiete,
            organisationseinheiten,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing articles: {e}") from e
