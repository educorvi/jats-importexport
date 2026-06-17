import asyncio
import logging
from enum import Enum

from fastapi import Request
from jats_exporters import HtmlExporter, JatsExporter
from jats_exporters.markdown import MarkdownExporter

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


async def jats_export(path: str):
    document = await asyncio.to_thread(get_adapter_instance().get_jats_document, path)
    jats = await asyncio.to_thread(JATS_EXPORTER.export, document)
    return JatsDocumentResponse(jats=jats)


async def html_export(path: str):
    document = await asyncio.to_thread(get_adapter_instance().get_jats_document, path)
    html_content = await asyncio.to_thread(HTML_EXPORTER.export, document)
    return HtmlDocumentResponse(html=html_content)

async def md_export(path: str):
    document = await asyncio.to_thread(get_adapter_instance().get_jats_document, path)
    md_content = await asyncio.to_thread(MARKDOWN_EXPORTER.export, document)
    return MarkdownDocumentResponse(md=md_content)