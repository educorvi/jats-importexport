"""Entrypoint API application module for jats-importexport."""

import argparse
import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from api.services.keyval_implementations import close_caches, init_caches

from .auth import require_permission
from .config import APIConfig
from .logging import setup_logging
from .routers import cache_management, export, export_async, list, modify, status, upload

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""

    setup_logging()

    if not APIConfig.API_KEY:
        logger.warning(
            "API_KEY is not set — authentication is DISABLED for /upload/* and /export/* endpoints. "
            "Set the API_KEY environment variable to require the X-API-Key header."
        )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        await init_caches()
        yield
        await close_caches()

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
    app.include_router(list.router, dependencies=[Depends(require_permission("read"))])
    app.include_router(export.router, dependencies=[Depends(require_permission("read"))])
    app.include_router(export_async.router, dependencies=[Depends(require_permission("read"))])
    app.include_router(upload.router, dependencies=[Depends(require_permission("write"))])
    app.include_router(modify.router, dependencies=[Depends(require_permission("write"))])
    app.include_router(cache_management.router, dependencies=[Depends(require_permission("read"))])
    return app


app = create_app()
Instrumentator().instrument(
    app,
    metric_namespace="vur",
    metric_subsystem="hub",
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
