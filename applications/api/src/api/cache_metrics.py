"""Prometheus instrumentation for cached export responses."""

from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, Protocol

from prometheus_client import Counter




# class _ExportFunction(Protocol):
#     __name__: str
#
#     def __call__(self, *args: Any, **kwargs: Any) -> Awaitable[Any]: ...
#
#
# def export_cache(**options: Any) -> Callable[[_ExportFunction], Callable[..., Awaitable[Any]]]:
#     """Count the cache decorator's HIT/MISS, including standalone PDF responses."""
#
#     def decorate(func: _ExportFunction) -> Callable[..., Awaitable[Any]]:
#         cached = cache(**options)(func)
#         endpoint = f"/export/{func.__name__.removeprefix('export_')}"
#         for result in ("hit", "miss"):
#             EXPORT_CACHE_REQUESTS.labels(endpoint=endpoint, result=result)
#
#         @wraps(cached)
#         async def instrumented(*args: Any, **kwargs: Any) -> Any:
#             result = await cached(*args, **kwargs)
#             # FastAPI injects this response using the signature added by @cache.
#             # It carries cache status even when the endpoint returns its own Response.
#             response = kwargs.get("__fastapi_cache_response")
#             if response is not None:
#                 status = response.headers.get(FastAPICache.get_cache_status_header())
#                 if status in ("HIT", "MISS"):
#                     EXPORT_CACHE_REQUESTS.labels(endpoint=endpoint, result=status.lower()).inc()
#             return result
#
#         return instrumented
#
#     return decorate
