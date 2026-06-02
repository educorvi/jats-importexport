import asyncio
from enum import Enum

from fastapi import Request
from fastapi.responses import Response
from jats_exporters import HtmlExporter, JatsExporter

from api.models import HtmlDocumentResponse, JatsDocumentResponse
from api.services.common import get_adapter_instance

JATS_EXPORTER = JatsExporter()
HTML_EXPORTER = HtmlExporter()


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


async def jats_export(path: str, return_type: ReturnType):
    document = await asyncio.to_thread(get_adapter_instance().get_jats_document, path)
    jats = await asyncio.to_thread(JATS_EXPORTER.export, document)
    if return_type == ReturnType.XML:
        return Response(content=jats, media_type="application/xml")
    else:
        return JatsDocumentResponse(jats=jats)


async def html_export(path: str, return_type: ReturnType):
    document = await asyncio.to_thread(get_adapter_instance().get_jats_document, path)
    html = await asyncio.to_thread(HTML_EXPORTER.export, document)
    if return_type == ReturnType.HTML:
        return Response(content=html, media_type="text/html")
    else:
        return HtmlDocumentResponse(html=html)
