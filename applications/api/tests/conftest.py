import os

import pytest
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

# The list service creates its adapter while api.main is imported during test
# collection. Supply inert credentials so collection does not depend on a local
# .env file, which is intentionally excluded from version control.
os.environ.setdefault("PLONE_BASE_URL", "http://localhost:8080")
os.environ.setdefault("PLONE_USERNAME", "test")
os.environ.setdefault("PLONE_PASSWORD", "test")


@pytest.fixture(autouse=True)
def init_cache():
    FastAPICache.init(InMemoryBackend(), prefix="test-cache")
    yield
    FastAPICache.reset()
