import asyncio
import logging
from enum import Enum

from fastapi import HTTPException, Request
from jats_exporters import HtmlExporter, JatsExporter
from jats_exporters.markdown import MarkdownExporter
from jats_storage_adapters.errors import PathNotFoundExpection

from api.models import HtmlDocumentResponse, JatsDocumentResponse, MarkdownDocumentResponse
from api.services.common import get_adapter_instance

JATS_EXPORTER = JatsExporter()
HTML_EXPORTER = HtmlExporter()
MARKDOWN_EXPORTER = MarkdownExporter()

logger = logging.getLogger(__name__)


class ReturnType(Enum):
    XML = "application/xml"
    JSON = "application/json"
    HTML = "text/html"


def get_return_type(request: Request) -> ReturnType:
    match request.headers.get("Accept"):
        case "application/xml":
            return ReturnType.XML
        case "application/json":
            return ReturnType.JSON
        case "text/html":
            return ReturnType.HTML
        case _:
            return ReturnType.JSON


async def __load_document(path: str):
    try:
        return await asyncio.to_thread(get_adapter_instance().get_jats_document, path)
    except PathNotFoundExpection as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {e}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading document: {e}") from e


async def jats_export(path: str):
    document = await __load_document(path)
    jats = await asyncio.to_thread(JATS_EXPORTER.export, document)
    return JatsDocumentResponse(jats=jats)


async def html_export(path: str):
    document = await __load_document(path)
    html_content = await asyncio.to_thread(HTML_EXPORTER.export, document)
    return HtmlDocumentResponse(html=html_content)


async def md_export(path: str):
    document = await __load_document(path)
    md_content = await asyncio.to_thread(MARKDOWN_EXPORTER.export, document)
    return MarkdownDocumentResponse(md=md_content)
