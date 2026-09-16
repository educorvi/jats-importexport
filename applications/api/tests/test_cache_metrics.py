import pytest
from fastapi import FastAPI, Response
from httpx import ASGITransport, AsyncClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.coder import PickleCoder

from api.cache_metrics import EXPORT_CACHE_REQUESTS, export_cache


@pytest.mark.parametrize("standalone_response", [False, True])
@pytest.mark.asyncio
async def test_export_cache_metrics(standalone_response):
    FastAPICache.reset()
    FastAPICache.init(InMemoryBackend(), prefix=f"metrics-test-{standalone_response}")
    app = FastAPI()

    @app.get("/export/test")
    @export_cache(namespace="export", coder=PickleCoder)
    async def export_test():
        return Response(b"pdf", media_type="application/pdf") if standalone_response else {"ok": True}

    def count(result):
        return EXPORT_CACHE_REQUESTS.labels(endpoint="/export/test", result=result)._value.get()

    hits, misses = count("hit"), count("miss")
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            first = await client.get("/export/test")
            second = await client.get("/export/test")
            assert first.status_code == second.status_code == 200
            assert first.content == second.content
            assert count("hit") == hits + 1
            assert count("miss") == misses + 1
            await client.get("/export/test", headers={"Cache-Control": "no-cache"})
            assert count("miss") == misses + 2
            await client.get("/export/test", headers={"Cache-Control": "no-store"})
            assert count("hit") == hits + 1
            assert count("miss") == misses + 2
    finally:
        FastAPICache.reset()
