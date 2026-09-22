import pytest

from api.services.keyval_implementations import (
    EXPORT_CACHE_REQUESTS,
    ExportType,
    InMemoryCache,
)


@pytest.mark.parametrize("export_type", list(ExportType))
@pytest.mark.parametrize("value", ["cached export", ""])
async def test_export_cache_metrics(export_type, value):
    cache = InMemoryCache(1, cache_name="TEST_EXPORT_CACHE")
    await cache.init()

    def count(result):
        return EXPORT_CACHE_REQUESTS.labels(
            type=export_type.value, result=result, cache_id=cache.cache_id
        )._value.get()

    hits, misses = count("hit"), count("miss")
    assert await cache.get("/article/", export_type) is None
    assert count("miss") == misses + 1
    assert count("hit") == hits

    await cache.set("article", export_type, value)
    assert await cache.get("/article/", export_type) == value
    assert count("hit") == hits + 1
    assert count("miss") == misses + 1

    await cache.delete("article", export_type)
    assert await cache.get("article", export_type) is None
    assert count("miss") == misses + 2
    assert count("hit") == hits + 1
