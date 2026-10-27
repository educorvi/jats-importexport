import asyncio
import copy
import logging
import pathlib
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup
from fastapi import HTTPException
from jats_classes import Front, JATSDocument
from jats_exporters import HtmlExporter, JatsExporter, MarkdownExporter, PdfExporter, ZipExporter
from jats_storage_adapters.errors import (
    DuplicateException,
    PathNotFoundExpection,
)
from jats_storage_adapters.interface import GetJATSDocumentOptions, StorageAdapter
from prometheus_client import Histogram, Summary

from api.models import HtmlDocumentResponse, JatsDocumentResponse, MarkdownDocumentResponse, MetadataResponse
from api.services.common import get_adapter_instance, get_media_downloader, pdf_replace_media_links_callback
from api.services.keyval_implementations import EXPORT_CACHE, ExportType

JATS_EXPORTER = JatsExporter()
HTML_EXPORTER = HtmlExporter()
MARKDOWN_EXPORTER = MarkdownExporter()
PDF_EXPORTER = PdfExporter()
ZIP_EXPORTER = ZipExporter()

logger = logging.getLogger(__name__)


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


async def __load_structure_tree(
    path: str, adapter: StorageAdapter | None = None
) -> list[dict]:
    try:
        adapter = adapter or get_adapter_instance()
        return await asyncio.to_thread(adapter.get_structure_tree, path)
    except PathNotFoundExpection as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {e}")
    except DuplicateException as e:
        raise HTTPException(status_code=409, detail=f"More than one document found for {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading document: {e}")


def _crop_structure_tree(tree_entries: list[dict], max_level: int | None, current_level: int = 1) -> list[dict]:
    if max_level is None:
        return tree_entries
    if current_level > max_level:
        return []
    return [
        {
            **entry,
            "children": _crop_structure_tree(entry.get("children", []), max_level, current_level + 1),
        }
        for entry in tree_entries
    ]


async def _replace_related_articles_webcode_with_url(doc: JATSDocument, adapter: StorageAdapter) -> None:
    related_articles_webcode = doc.article.front.related_articles_map
    if related_articles_webcode:
        related_articles_url = {}
        for webcode, title in related_articles_webcode.items():
            try:
                url = adapter.get_url_from_path(await asyncio.to_thread(adapter.get_path_from_webcode, webcode))
                related_articles_url[url] = title
            except Exception:
                continue
        doc.article.front.related_articles_map = related_articles_url

    related_articles_translations_webcode = doc.article.front.related_articles_translations_map
    if related_articles_translations_webcode:
        related_articles_translations_url = {}
        for webcode, title_lang in related_articles_translations_webcode.items():
            try:
                url = adapter.get_url_from_path(await asyncio.to_thread(adapter.get_path_from_webcode, webcode))
                related_articles_translations_url[url] = title_lang
            except Exception:
                continue
        doc.article.front.related_articles_translations_map = related_articles_translations_url


def _jats_replace_media_links_callback(url: str, media: tuple[bytes, str] | None = None) -> str:
    if media is None:
        logger.warning(f"No media content available for URL: {url}")
        return url
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    query_filename = query.get("filename", [None])[0]
    if query_filename is not None:
        filename = pathlib.PurePosixPath(query_filename)
    else:
        filename = (pathlib.PurePosixPath(urlparse(url).path).name).replace("\\", "/")
    return f"media/{filename}"


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
        await _replace_related_articles_webcode_with_url(document, get_adapter_instance())
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
        await _replace_related_articles_webcode_with_url(document, get_adapter_instance())
        md_content = await asyncio.to_thread(MARKDOWN_EXPORTER.export, document)
        if include_edit_links:
            await EXPORT_CACHE.set(path, ExportType.MD_EDIT_LINKS, md_content)
        else:
            await EXPORT_CACHE.set(path, ExportType.MD, md_content)
        return MarkdownDocumentResponse(md=md_content)


async def pdf_export(path: str):
    cached = await EXPORT_CACHE.get_pdf(path)
    if cached is not None:
        return cached
    with exp_metric.labels("pdf").time(), exp_document_metric.labels("pdf", path).time():
        adapter = get_adapter_instance()
        document = await __load_document(path, adapter=adapter)
        media_downloader = get_media_downloader(adapter)
        await asyncio.to_thread(document.replace_media_links, pdf_replace_media_links_callback, media_downloader)
        pdf_content, filename = await asyncio.to_thread(PDF_EXPORTER.export, document)
        await EXPORT_CACHE.set_pdf(path, pdf_content, filename)
        return pdf_content, filename


async def zip_export(path: str):
    cached = await EXPORT_CACHE.get_zip(path)
    if cached is not None:
        return cached
    with exp_metric.labels("zip").time(), exp_document_metric.labels("zip", path).time():
        adapter = get_adapter_instance()
        document_for_jats = await __load_document(path, adapter=adapter)
        document_for_pdf = copy.deepcopy(document_for_jats)
        media_downloader = get_media_downloader(adapter)

        media = await asyncio.to_thread(
            document_for_jats.replace_media_links, _jats_replace_media_links_callback, media_downloader
        )

        document_for_html = copy.deepcopy(document_for_jats)
        await _replace_related_articles_webcode_with_url(document_for_html, adapter)

        await asyncio.to_thread(
            document_for_pdf.replace_media_links, pdf_replace_media_links_callback, media_downloader
        )

        metadata = MetadataResponse(metadata=document_for_jats.article.front).model_dump(mode="json")
        zip_content, filename = await asyncio.to_thread(
            ZIP_EXPORTER.export, document_for_jats, document_for_html, document_for_pdf, media, metadata
        )
        await EXPORT_CACHE.set_zip(path, zip_content, filename)
        return zip_content, filename


async def metadata_export(path: str):
    cached = await EXPORT_CACHE.get_metadata(path)
    if cached is not None:
        return cached
    with exp_metric.labels("metadata").time(), exp_document_metric.labels("metadata", path).time():
        adapter = get_adapter_instance()
        front = await __load_metadata(path, adapter=adapter)
        await EXPORT_CACHE.set_metadata(path, front)
        return front


async def structure_tree_export(path: str, max_level: int | None = None):
    cached = await EXPORT_CACHE.get_structure_tree(path)
    if cached is not None:
        return _crop_structure_tree(cached, max_level)
    with exp_metric.labels("structure_tree").time(), exp_document_metric.labels("structure_tree", path).time():
        tree_entries = await __load_structure_tree(path)
        await EXPORT_CACHE.set_structure_tree(path, tree_entries)
        return _crop_structure_tree(tree_entries, max_level)
