import asyncio
import base64
import logging
import os
from collections.abc import Callable
from enum import Enum
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup
from fastapi import HTTPException, Request
from jats_classes import Front, JATSDocument
from jats_exporters import HtmlExporter, JatsExporter, MarkdownExporter, PdfExporter
from jats_storage_adapters.errors import (
    DuplicateException,
    PathNotFoundExpection,
)
from jats_storage_adapters.interface import GetJATSDocumentOptions, StorageAdapter
from prometheus_client import Histogram, Summary

from api.models import HtmlDocumentResponse, JatsDocumentResponse, MarkdownDocumentResponse
from api.services.common import get_adapter_instance
from api.services.keyval_implementations import EXPORT_CACHE, ExportType

JATS_EXPORTER = JatsExporter()
HTML_EXPORTER = HtmlExporter()
MARKDOWN_EXPORTER = MarkdownExporter()
PDF_EXPORTER = PdfExporter()

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
    except DuplicateException as e:
        raise HTTPException(status_code=409, detail=f"More than one document found for {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading document: {e}")


async def __load_metadata(path: str, adapter: StorageAdapter | None = None) -> Front:
    try:
        adapter = adapter or get_adapter_instance()
        return await asyncio.to_thread(adapter.get_metadata, path)
    except PathNotFoundExpection as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {e}")
    except DuplicateException as e:
        raise HTTPException(status_code=409, detail=f"More than one document found for {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading document: {e}")


def _get_media_downloader(storage_adapter: StorageAdapter) -> Callable[[str], tuple[bytes, str]]:
    """Returns a callable that downloads media from the signed API URL or a StorageAdapter URL."""
    IEH_BASE_URL = os.environ.get("IEH_BASE_URL")
    if IEH_BASE_URL is None:
        raise OSError("IEH_BASE_URL environment variable is not set.")
    parsed_base_url = urlparse(IEH_BASE_URL)

    def downloader(url: str) -> tuple[bytes, str]:
        parsed_url = urlparse(url)
        if (parsed_url.scheme == parsed_base_url.scheme
            and parsed_url.netloc == parsed_base_url.netloc
            and parsed_url.path.startswith(parsed_base_url.path)
        ):
            query = parse_qs(parsed_url.query)
            required = ("path", "filename", "signature")
            values = {key: query.get(key, []) for key in required}
            if any(len(value) != 1 or not value[0] for value in values.values()):
                raise ValueError(f"Media URL is missing required signed parameters: {url}")
            return storage_adapter.get_media(
                values["path"][0],
                values["filename"][0],
                values["signature"][0],
            )
        else:
            return storage_adapter.download_file(url)

    return downloader

def _pdf_replace_media_links_callback(url: str, media: tuple[bytes, str] | None = None) -> str:
    if media is None:
        return url
    content, content_type = media
    encoded = base64.b64encode(content).decode("utf-8")
    return f"data:{content_type};base64,{encoded}"


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
    cached = await EXPORT_CACHE.get(path, ExportType.JATS)
    if cached:
        return JatsDocumentResponse(jats=cached)
    with exp_metric.labels("jats").time(), exp_document_metric.labels("jats", path).time():
        document = await __load_document(path)
        jats = await asyncio.to_thread(JATS_EXPORTER.export, document)
        await EXPORT_CACHE.set(path, ExportType.JATS, jats)
        return JatsDocumentResponse(jats=jats)


async def html_export(path: str, include_edit_links: bool = False):
    cached = await EXPORT_CACHE.get_html(path, include_edit_links)
    if cached:
        return HtmlDocumentResponse(**cached)
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
        await EXPORT_CACHE.set_html(path, include_edit_links, str(content), str(front))
        return HtmlDocumentResponse(html=str(content), front=str(front))


async def md_export(path: str, include_edit_links: bool = False):
    if include_edit_links:
        cached = await EXPORT_CACHE.get(path, ExportType.MD_EDIT_LINKS)
    else:
        cached = await EXPORT_CACHE.get(path, ExportType.MD)
    if cached:
        return MarkdownDocumentResponse(md=cached)
    with exp_metric.labels("md").time(), exp_document_metric.labels("md", path).time():
        document = await __load_document(path, {"include_edit_links": include_edit_links})
        md_content = await asyncio.to_thread(MARKDOWN_EXPORTER.export, document)
        if include_edit_links:
            await EXPORT_CACHE.set(path, ExportType.MD_EDIT_LINKS, md_content)
        else:
            await EXPORT_CACHE.set(path, ExportType.MD, md_content)
        return MarkdownDocumentResponse(md=md_content)


async def pdf_export(path: str):
    with exp_metric.labels("pdf").time(), exp_document_metric.labels("pdf", path).time():
        adapter = get_adapter_instance()
        document = await __load_document(path, adapter=adapter)
        media_downloader = _get_media_downloader(adapter)
        document.replace_media_links(_pdf_replace_media_links_callback, media_downloader)
        pdf_content, filename = await asyncio.to_thread(PDF_EXPORTER.export, document)
        return pdf_content, filename


async def metadata_export(path: str):
    with exp_metric.labels("metadata").time(), exp_document_metric.labels("metadata", path).time():
        adapter = get_adapter_instance()
        front = await __load_metadata(path, adapter=adapter)
        return front
