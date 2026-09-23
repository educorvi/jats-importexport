import os

import pytest

# The list service creates its adapter while api.main is imported during test
# collection. Supply inert credentials so collection does not depend on a local
# .env file, which is intentionally excluded from version control.
os.environ.setdefault("PLONE_BASE_URL", "http://localhost:8080")
os.environ.setdefault("PLONE_USERNAME", "test")
os.environ.setdefault("PLONE_PASSWORD", "test")

# Unit tests must not use or clear a cache configured by the local environment.
# In-memory caches also work across the fixture and TestClient event loops.
os.environ["CACHE_IMPLEMENTATION"] = "inmemory"


@pytest.fixture(autouse=True)
async def init_cache():
    from api.services.keyval_implementations import ALL_CACHES

    for cache in ALL_CACHES:
        await cache.init()
    try:
        yield
    finally:
        for cache in ALL_CACHES:
            await cache.delete_all()
            await cache.close()
