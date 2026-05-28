"""Entrypoint API application module for jats-importexport.

Provides a simple CLI startup for verifying the API environment.
"""

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config import APIConfig
from .models import HTTP400BadRequest, HTTP404NotFound, HTTP413PayloadTooLarge, HTTP415UnsupportedMediaType, HTTP500InternalServerError, UploadFileResponse
from .services import jats_upload


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

    @app.post("/upload", response_model=UploadFileResponse,
        responses={
            400: {"model": HTTP400BadRequest},
            413: {"model": HTTP413PayloadTooLarge},
            415: {"model": HTTP415UnsupportedMediaType},
            500: {"model": HTTP500InternalServerError},
        },
        summary="Upload a JATS Document (ZIP-file) to the storage",
        description="This endpoint accepts a ZIP file containing a JATS document (XML file) and optional referenced files and uploads it to the storage backend.",
    )
    async def upload(zip_file: UploadFile = File(...)):
        return await jats_upload.upload(zip_file)

    # More endpoints can be added here. If we have to add more endpoints, we should use routers

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("applications.api.main:app", host=APIConfig.HOST, port=APIConfig.PORT, reload=APIConfig.RELOAD, factory=True, workers=APIConfig.WORKERS)
