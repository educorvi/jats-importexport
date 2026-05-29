"""Entrypoint API application module for jats-importexport."""

import argparse
import json
import logging
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import APIConfig
from .routers import export, status, upload

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""

    app = FastAPI(
        title=APIConfig.API_TITLE,
        description=APIConfig.API_DESCRIPTION,
        version=APIConfig.API_VERSION,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=APIConfig.CORS_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(status.router)
    app.include_router(upload.router)
    app.include_router(export.router)

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
