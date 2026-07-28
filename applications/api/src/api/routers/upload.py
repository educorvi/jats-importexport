from io import BytesIO
from typing import Any, cast

from fastapi import APIRouter, HTTPException, Request, UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile

from ..models import (
    HTTP400BadRequest,
    HTTP413PayloadTooLarge,
    HTTP415UnsupportedMediaType,
    HTTP500InternalServerError,
    UploadFileResponse,
)
from ..services.upload import decode_data_uri
from ..services.upload import upload_docx as upload_docx_service
from ..services.upload import upload_xml as upload_xml_service
from ..services.upload import upload_zip as upload_zip_service

router = APIRouter(prefix="/upload", tags=["Upload"])


def _request_body_extra(field: str) -> dict[str, Any]:
    """Build the openapi_extra requestBody dict for a given field name."""
    return {
        "requestBody": {
            "required": True,
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {field: {"type": "string", "format": "binary"}},
                        "required": [field],
                    }
                },
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            field: {
                                "type": "string",
                                "description": "Base64-encoded data URI of the file (e.g. `data:<mime>;base64,<data>`)",
                            }
                        },
                        "required": [field],
                    }
                },
            },
        }
    }


def _upload_file_from_data_uri(data_uri: str, filename: str) -> UploadFile:
    file_bytes = decode_data_uri(data_uri)
    return UploadFile(filename=filename, file=BytesIO(file_bytes))


@router.post(
    "/zip",
    operation_id="upload_zip",
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
        " and optional referenced asset files and uploads it to the storage backend."
        " The file can be provided either as a multipart form upload (`zip_file` field)"
        " or as a JSON body with the `zip_file` field set to a base64-encoded data URI"
        " (e.g. `data:application/zip;base64,<data>`)."
        " The target containers for the uploaded files and assets can be specified using"
        " the `container` and `assets_container` query parameters."
        " If not specified, the default containers will be used."
    ),
    openapi_extra=_request_body_extra("zip_file"),
)
async def upload_zip(request: Request, container: str | None = None, assets_container: str | None = None):
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("multipart/"):
        form = await request.form()
        zip_file = form.get("zip_file")
        if zip_file is None:
            raise HTTPException(status_code=422, detail="Missing 'zip_file' form field.")
        if not isinstance(zip_file, StarletteUploadFile):
            raise HTTPException(status_code=422, detail="Invalid 'zip_file' form field.")
    else:
        body = await request.json()
        data_uri = body.get("zip_file")
        if not data_uri:
            raise HTTPException(status_code=422, detail="Missing 'zip_file' field in JSON body.")
        zip_file = _upload_file_from_data_uri(data_uri, "upload.zip")
    return await upload_zip_service(cast(UploadFile, zip_file), container, assets_container)


@router.post(
    "/xml",
    operation_id="upload_xml",
    response_model=UploadFileResponse,
    responses={
        400: {"model": HTTP400BadRequest},
        413: {"model": HTTP413PayloadTooLarge},
        415: {"model": HTTP415UnsupportedMediaType},
        500: {"model": HTTP500InternalServerError},
    },
    summary="Upload a JATS Document (XML) to the storage",
    description=(
        "This endpoint accepts a JATS document as an XML file upload and uploads it to the"
        " storage backend."
        " Note that this endpoint does not support uploading referenced files, so it should"
        " only be used for simple JATS documents without external file references."
        " The file can be provided either as a multipart form upload (`xml_file` field)"
        " or as a JSON body with the `xml_file` field set to a base64-encoded data URI"
        " (e.g. `data:application/xml;base64,<data>`)."
        " The target container for the uploaded file can be specified using the `container` query parameter."
        " If not specified, the default container will be used."
    ),
    openapi_extra=_request_body_extra("xml_file"),
)
async def upload_xml(request: Request, container: str | None = None):
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("multipart/"):
        form = await request.form()
        xml_file = form.get("xml_file")
        if xml_file is None:
            raise HTTPException(status_code=422, detail="Missing 'xml_file' form field.")
        if not isinstance(xml_file, StarletteUploadFile):
            raise HTTPException(status_code=422, detail="Invalid 'xml_file' form field.")
    else:
        body = await request.json()
        data_uri = body.get("xml_file")
        if not data_uri:
            raise HTTPException(status_code=422, detail="Missing 'xml_file' field in JSON body.")
        xml_file = _upload_file_from_data_uri(data_uri, "upload.xml")
    return await upload_xml_service(cast(UploadFile, xml_file), container)


@router.post(
    "/docx",
    operation_id="upload_docx",
    # response_model=DownloadFileResponse,
    responses={
        400: {"model": HTTP400BadRequest},
        413: {"model": HTTP413PayloadTooLarge},
        415: {"model": HTTP415UnsupportedMediaType},
        500: {"model": HTTP500InternalServerError},
    },
    summary="Convert a docx file to JATS XML and return the JATS XML file",
    description=(
        "This endpoint accepts a DOCX file upload, converts it to JATS XML, and uploads it to the storage backend."
        " The file can be provided either as a multipart form upload (`docx_file` field)"
        " or as a JSON body with the `docx_file` field set to a base64-encoded data URI"
        " (e.g. `data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,<data>`)."
        " The target containers for the uploaded files and assets can be specified using"
        " the `container` and `assets_container` query parameters."
        " If not specified, the default containers will be used."
    ),
    openapi_extra=_request_body_extra("docx_file"),
)
async def upload_docx(request: Request, container: str | None = None, assets_container: str | None = None):
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("multipart/"):
        form = await request.form()
        docx_file = form.get("docx_file")
        if docx_file is None:
            raise HTTPException(status_code=422, detail="Missing 'docx_file' form field.")
        if not isinstance(docx_file, StarletteUploadFile):
            raise HTTPException(status_code=422, detail="Invalid 'docx_file' form field.")
    else:
        body = await request.json()
        data_uri = body.get("docx_file")
        if not data_uri:
            raise HTTPException(status_code=422, detail="Missing 'docx_file' field in JSON body.")
        docx_file = _upload_file_from_data_uri(data_uri, "upload.docx")
    return await upload_docx_service(cast(UploadFile, docx_file), container, assets_container)
