"""Entrypoint API application module for jats-importexport.

Provides a simple CLI startup for verifying the API environment.
"""

from typing import Annotated

import uvicorn
from fastapi import FastAPI, File, Header, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from .config import APIConfig
from .models import (
    HTTP400BadRequest,
    HTTP413PayloadTooLarge,
    HTTP415UnsupportedMediaType,
    HTTP500InternalServerError,
    JatsDocumentResponse,
    UploadFileResponse,
)
from .services.export import ReturnType, jats_export
from .services.upload import upload_xml as upload_xml_service
from .services.upload import upload_zip as upload_zip_service


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

    @app.get("/status")
    async def health_status():
        return {"status": "healthy"}

    @app.post(
        "/upload/zip",
        response_model=UploadFileResponse,
        responses={
            400: {"model": HTTP400BadRequest},
            413: {"model": HTTP413PayloadTooLarge},
            415: {"model": HTTP415UnsupportedMediaType},
            500: {"model": HTTP500InternalServerError},
        },
        summary="Upload a JATS Document (ZIP-file) to the storage",
        description=("This endpoint accepts a ZIP file containing a JATS document (XML file)"
                     " and optional referenced files and uploads it to the storage backend."),
    )
    async def upload_zip(zip_file: UploadFile = File(...)):
        return await upload_zip_service(zip_file)

    @app.post(
        "/upload/xml",
        response_model=UploadFileResponse,
        responses={
            400: {"model": HTTP400BadRequest},
            415: {"model": HTTP415UnsupportedMediaType},
            500: {"model": HTTP500InternalServerError},
        },
        summary="Upload a JATS Document (XML) to the storage",
        description=("This endpoint accepts a JATS document as an XML file upload and uploads it to the"
                     " storage backend."
                     " Note that this endpoint does not support uploading referenced files, so it should"
                     " only be used for simple JATS documents without external file references."),
    )
    async def upload_xml(xml_file: UploadFile = File(...)):
        return await upload_xml_service(xml_file)

    @app.get(
        "/export/jats",
        response_model=JatsDocumentResponse,
        responses={
            200: {
                "content": {
                    "application/xml": {
                        "schema": {"type": "string"},
                        "example": "<article>...</article>",
                    }
                }
            }
        },
    )
    async def export_jats(
        path: str, accept: Annotated[ReturnType | None, Header()] = None
    ):
        return_type = accept or ReturnType.JSON
        result = jats_export(path, return_type)
        if return_type == ReturnType.XML:
            return Response(content=result, media_type="application/xml")
        return result

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
