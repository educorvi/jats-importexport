import asyncio
import logging
from enum import Enum

from bs4 import BeautifulSoup
from fastapi import HTTPException, Request
from jats_classes import Front, JATSDocument
from jats_exporters import HtmlExporter, JatsExporter, MarkdownExporter, PdfExporter
from jats_storage_adapters.errors import PathNotFoundExpection
from jats_storage_adapters.interface import GetJATSDocumentOptions, StorageAdapter
from prometheus_client import Histogram, Summary

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


async def __load_document(
    path: str, options: GetJATSDocumentOptions | None = None, adapter: StorageAdapter | None = None
) -> JATSDocument:
    try:
        adapter = adapter or get_adapter_instance()
        return await asyncio.to_thread(adapter.get_jats_document, path, options)
    except PathNotFoundExpection as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading document: {e}")


async def __load_metadata(path: str, adapter: StorageAdapter | None = None) -> Front:
    try:
        adapter = adapter or get_adapter_instance()
        return await asyncio.to_thread(adapter.get_metadata, path)
    except PathNotFoundExpection as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading document: {e}")


exp_metric = Histogram(
    "jats_export_duration_seconds",
    "Time spent exporting JATS documents",
    labelnames=["export_type"],
    buckets=[0.1, 0.25, 0.5, 1, 2.5, 5, 10, 20, 30, 60],
)

exp_document_metric = Summary(
    "jats_export_document_duration_seconds",
    "Time spent exporting JATS documents per document",
    labelnames=["export_type", "path"],
)


async def jats_export(path: str):
    with exp_metric.labels("jats").time(), exp_document_metric.labels("jats", path).time():
        document = await __load_document(path)
        jats = await asyncio.to_thread(JATS_EXPORTER.export, document)
        return JatsDocumentResponse(jats=jats)


async def html_export(path: str, include_edit_links: bool = False):
    with exp_metric.labels("html").time(), exp_document_metric.labels("html", path).time():
        document = await __load_document(path, {"include_edit_links": include_edit_links})
        html_content = await asyncio.to_thread(HTML_EXPORTER.export, document)

        soup = BeautifulSoup(html_content, "html.parser")
        content = soup.find(id="article-content")
        if content is None:
            raise HTTPException(
                status_code=500, detail="HTML export failed: 'article-content' not found in the output."
            )
        content.attrs["class"] = "content"
        front = soup.find(id="article-front")
        if front is None:
            raise HTTPException(status_code=500, detail="HTML export failed: 'article-front' not found in the output.")
        front.attrs["class"] = "front"

        return HtmlDocumentResponse(html=str(content), front=str(front))


async def md_export(path: str, include_edit_links: bool = False):
    with exp_metric.labels("md").time(), exp_document_metric.labels("md", path).time():
        document = await __load_document(path, {"include_edit_links": include_edit_links})
        md_content = await asyncio.to_thread(MARKDOWN_EXPORTER.export, document)
        return MarkdownDocumentResponse(md=md_content)


async def pdf_export(path: str):
    with exp_metric.labels("pdf").time(), exp_document_metric.labels("pdf", path).time():
        adapter = get_adapter_instance()
        document = await __load_document(path, adapter=adapter)
        pdf_content, filename = await asyncio.to_thread(
            PdfExporter(image_downloader=adapter.download_file).export, document
        )
        return pdf_content, filename


async def metadata_export(path: str):
    with exp_metric.labels("metadata").time(), exp_document_metric.labels("metadata", path).time():
        adapter = get_adapter_instance()
        front = await __load_metadata(path, adapter=adapter)
        return front
