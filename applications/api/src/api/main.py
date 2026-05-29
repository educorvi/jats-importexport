"""Entrypoint API application module for jats-importexport.

Provides a simple CLI startup for verifying the API environment.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import APIConfig
from .routers import export, status, upload


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
