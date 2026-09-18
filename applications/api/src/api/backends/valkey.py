"""Valkey backend for FastAPI Cache."""

from typing import Any

from fastapi_cache.types import Backend


class ValkeyBackend(Backend):
    """Store FastAPI Cache entries in Valkey."""

    def __init__(self, valkey: Any) -> None:
        self.valkey = valkey

    async def get_with_ttl(self, key: str) -> tuple[int, bytes | None]:
        async with self.valkey.pipeline(transaction=True) as pipeline:
            return await pipeline.ttl(key).get(key).execute()

    async def get(self, key: str) -> bytes | None:
        return await self.valkey.get(key)

    async def set(self, key: str, value: bytes, expire: int | None = None) -> None:
        await self.valkey.set(key, value, ex=expire)

    async def clear(self, namespace: str | None = None, key: str | None = None) -> int:
        if namespace:
            script = f"for _, name in ipairs(redis.call('KEYS', '{namespace}:*')) do redis.call('DEL', name); end"
            return await self.valkey.eval(script, 0)
        if key:
            return await self.valkey.delete(key)
        return 0
