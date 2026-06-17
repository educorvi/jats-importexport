"""Entrypoint API application module for jats-importexport."""

import argparse
import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import redis.asyncio as aioredis
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends.redis import RedisBackend

from api.config import StorageConfig

from .auth import verify_api_key
from .config import APIConfig
from .routers import export, status, upload

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""

    logging.basicConfig(level=logging.INFO)

    if not APIConfig.API_KEY:
        logger.warning(
            "API_KEY is not set — authentication is DISABLED for /upload/* and /export/* endpoints. "
            "Set the API_KEY environment variable to require the X-API-Key header."
        )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        redis = aioredis.from_url(f"redis://{StorageConfig.REDIS_HOST}", encoding="utf8", decode_responses=False)
        try:
            await redis.ping()
            FastAPICache.init(RedisBackend(redis), prefix=StorageConfig.CACHE_PREFIX)
        except Exception as e:
            logger.error(f"Failed to connect to Redis, falling back to In-Memory cache: {str(e)}")
            FastAPICache.init(InMemoryBackend(), prefix=StorageConfig.CACHE_PREFIX)
        yield
        await redis.close()

    app = FastAPI(
        title=APIConfig.API_TITLE,
        description=APIConfig.API_DESCRIPTION,
        version=APIConfig.API_VERSION,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=APIConfig.CORS_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(status.router)
    app.include_router(upload.router, dependencies=[Depends(verify_api_key)])
    app.include_router(export.router, dependencies=[Depends(verify_api_key)])

    return app


app = create_app()


def start() -> None:
    """Console script entry point – run with ``uv run start-api``."""
    uvicorn.run(
        "api.main:app",
        host=APIConfig.HOST,
        port=APIConfig.PORT,
        reload=APIConfig.RELOAD,
        workers=APIConfig.WORKERS,
    )


def export_openapi() -> None:
    """Console script entry point – run with ``uv run export-openapi``."""
    parser = argparse.ArgumentParser(description="Export the FastAPI OpenAPI schema as JSON.")
    parser.add_argument(
        "output",
        nargs="?",
        default="openapi.json",
        help="Output file path for the generated OpenAPI JSON.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation to use for the generated schema.",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(f"{json.dumps(app.openapi(), indent=args.indent)}\n", encoding="utf-8")
