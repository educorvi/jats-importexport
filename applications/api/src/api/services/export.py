from enum import Enum

from fastapi.responses import Response
from jats_exporters import HtmlExporter, JatsExporter

from api.models import HtmlDocumentResponse, JatsDocumentResponse
from api.services.common import get_adapter_instance

JATS_EXPORTER = JatsExporter()


class ReturnType(Enum):
    XML = "application/xml"
    JSON = "application/json"
    HTML = "text/html"


def jats_export(path: str, return_type: ReturnType):
    document = get_adapter_instance().get_jats_document(path)
    jats = JATS_EXPORTER.export(document)
    if return_type == ReturnType.XML:
        return Response(content=jats, media_type="application/xml")
    else:
        return JatsDocumentResponse(jats=jats)


def html_export(path: str, return_type: ReturnType):
    document = get_adapter_instance().get_jats_document(path)
    html = HtmlExporter().export(document)
    if return_type == ReturnType.HTML:
        return Response(content=html, media_type="text/html")
    else:
        return HtmlDocumentResponse(html=html)
