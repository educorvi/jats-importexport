from fastapi import APIRouter, File, UploadFile

from ..models import (
    HTTP400BadRequest,
    HTTP413PayloadTooLarge,
    HTTP415UnsupportedMediaType,
    HTTP500InternalServerError,
    UploadFileResponse,
)
from ..services.upload import upload_xml as upload_xml_service
from ..services.upload import upload_zip as upload_zip_service

router = APIRouter(prefix="/upload")


@router.post(
    "/zip",
    response_model=UploadFileResponse,
    responses={
        400: {"model": HTTP400BadRequest},
        413: {"model": HTTP413PayloadTooLarge},
        415: {"model": HTTP415UnsupportedMediaType},
        500: {"model": HTTP500InternalServerError},
    },
    summary="Upload a JATS Document (ZIP-file) to the storage",
    description=(
        "This endpoint accepts a ZIP file containing a JATS document (XML file)"
        " and optional referenced files and uploads it to the storage backend."
    ),
)
async def upload_zip(zip_file: UploadFile = File(...)):
    return await upload_zip_service(zip_file)


@router.post(
    "/xml",
    response_model=UploadFileResponse,
    responses={
        400: {"model": HTTP400BadRequest},
        415: {"model": HTTP415UnsupportedMediaType},
        500: {"model": HTTP500InternalServerError},
    },
    summary="Upload a JATS Document (XML) to the storage",
    description=(
        "This endpoint accepts a JATS document as an XML file upload and uploads it to the"
        " storage backend."
        " Note that this endpoint does not support uploading referenced files, so it should"
        " only be used for simple JATS documents without external file references."
    ),
)
async def upload_xml(xml_file: UploadFile = File(...)):
    return await upload_xml_service(xml_file)
