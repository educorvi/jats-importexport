import asyncio
import logging

from fastapi import HTTPException
from jats_classes import Front, JATSClassInterface
from jats_exporters import HtmlExporter, JatsExporter, MarkdownExporter, PdfExporter
from jats_storage_adapters.errors import (
    DuplicateException,
    PathNotFoundExpection,
)
from jats_storage_adapters.interface import GetJATSDocumentOptions, StorageAdapter

from api.models import HtmlDocumentPartialResponse, JatsDocumentResponse, MarkdownDocumentResponse
from api.services.common import get_adapter_instance, get_media_downloader, pdf_replace_media_links_callback
from api.services.keyval_implementations import PARTIAL_EXPORT_CACHE, ExportType

JATS_EXPORTER = JatsExporter()
HTML_EXPORTER = HtmlExporter()
MARKDOWN_EXPORTER = MarkdownExporter()
PDF_EXPORTER = PdfExporter()

logger = logging.getLogger(__name__)


async def __load_document_part(
    path: str, sub_path: str, options: GetJATSDocumentOptions | None = None, adapter: StorageAdapter | None = None
) -> tuple[JATSClassInterface, Front]:
    try:
        adapter = adapter or get_adapter_instance()
        return await asyncio.to_thread(adapter.get_jats_document_part, path, sub_path, options)
    except PathNotFoundExpection as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {e}")
    except DuplicateException as e:
        raise HTTPException(status_code=409, detail=f"More than one document found for {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading document: {e}")


async def jats_export(path: str, sub_path: str):
    cached = await PARTIAL_EXPORT_CACHE.get(path, ExportType.JATS, sub_path)
    if cached is not None:
        return JatsDocumentResponse(jats=cached)
    document_part, _ = await __load_document_part(path, sub_path)
    jats = await asyncio.to_thread(JATS_EXPORTER.export_partial, document_part)
    await PARTIAL_EXPORT_CACHE.set(path, ExportType.JATS, jats, sub_path)
    return JatsDocumentResponse(jats=jats)


async def html_export(path: str, sub_path: str, include_edit_links: bool = False):
    cached = await PARTIAL_EXPORT_CACHE.get_html(path, include_edit_links, sub_path)
    if cached is not None:
        return HtmlDocumentPartialResponse(html=cached["html"])
    document_part, _ = await __load_document_part(path, sub_path, {"include_edit_links": include_edit_links})
    html_content = await asyncio.to_thread(HTML_EXPORTER.export_partial, document_part)
    await PARTIAL_EXPORT_CACHE.set_html(path, include_edit_links, html_content, "", sub_path)
    return HtmlDocumentPartialResponse(html=html_content)


async def md_export(path: str, sub_path: str, include_edit_links: bool = False):
    cached = await PARTIAL_EXPORT_CACHE.get_md(path, include_edit_links, sub_path)
    if cached is not None:
        return MarkdownDocumentResponse(md=cached)
    document_part, _ = await __load_document_part(path, sub_path, {"include_edit_links": include_edit_links})
    md_content = await asyncio.to_thread(MARKDOWN_EXPORTER.export_partial, document_part)
    await PARTIAL_EXPORT_CACHE.set_md(path, include_edit_links, md_content, sub_path)
    return MarkdownDocumentResponse(md=md_content)


async def pdf_export(path: str, sub_path: str):
    cached = await PARTIAL_EXPORT_CACHE.get_pdf(path, sub_path)
    if cached is not None:
        return cached
    adapter = get_adapter_instance()
    document_part, front = await __load_document_part(path, sub_path, adapter=adapter)
    media_downloader = get_media_downloader(adapter)
    await asyncio.to_thread(document_part.replace_media_links, pdf_replace_media_links_callback, media_downloader)
    pdf_content, filename = await asyncio.to_thread(PDF_EXPORTER.export_partial, document_part, front)
    await PARTIAL_EXPORT_CACHE.set_pdf(path, pdf_content, filename, sub_path)
    return pdf_content, filename
