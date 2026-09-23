import logging

import prometheus_client
from fastapi import BackgroundTasks

from api.models import HtmlDocumentResponse
from api.services.export import html_export, pdf_export
from api.services.keyval_implementations import EXPORT_CACHE, EXPORT_STATE_CACHE, ExportState, ExportType

logger = logging.getLogger(__name__)

FAILED_ASYNC_EXPORTS = prometheus_client.Counter(
    "failed_async_exports", "Number of failed async exports", labelnames=["export_type"]
)


async def _export_and_write_html(path: str, include_edit_links: bool = False):
    export_type = ExportType.HTML_EDIT_LINKS if include_edit_links else ExportType.HTML
    try:
        html: HtmlDocumentResponse = await html_export(path, include_edit_links)
        await EXPORT_CACHE.set_html(path, include_edit_links, html.html, html.front)
        await EXPORT_STATE_CACHE.set(path, export_type, ExportState.COMPLETE.value)
        logger.info(f"HTML exported and written to {path}")
    except Exception as e:
        await EXPORT_STATE_CACHE.set(path, export_type, ExportState.FAILED.value)
        FAILED_ASYNC_EXPORTS.labels(export_type=export_type.value).inc()
        logger.error(f"An error occurred while exporting HTML: {e}")
        return


async def html_export_async(
    path: str, bt: BackgroundTasks, include_edit_links: bool = False
) -> HtmlDocumentResponse | None:
    export_type = ExportType.HTML_EDIT_LINKS if include_edit_links else ExportType.HTML
    cached_html = await EXPORT_CACHE.get_html(path, include_edit_links)
    if cached_html:
        return HtmlDocumentResponse(**cached_html)
    state = await EXPORT_STATE_CACHE.get(path, export_type)
    if state == ExportState.RUNNING.value:
        return None
    else:
        await EXPORT_STATE_CACHE.set(path, export_type, ExportState.RUNNING.value)
        bt.add_task(_export_and_write_html, path, include_edit_links)
        return None


async def _export_and_write_pdf(path: str):
    try:
        content, filename = await pdf_export(path)
        await EXPORT_CACHE.set_pdf(path, content, filename)
        await EXPORT_STATE_CACHE.set(path, ExportType.PDF, ExportState.COMPLETE.value)
        logger.info(f"PDF exported and written to {path}")
    except Exception as e:
        await EXPORT_STATE_CACHE.set(path, ExportType.PDF, ExportState.FAILED.value)
        FAILED_ASYNC_EXPORTS.labels(export_type=ExportType.PDF.value).inc()
        logger.error(f"An error occurred while exporting PDF: {e}")


async def pdf_export_async(path: str, bt: BackgroundTasks) -> tuple[bytes, str] | None:
    cached_pdf = await EXPORT_CACHE.get_pdf(path)
    if cached_pdf is not None:
        return cached_pdf
    state = await EXPORT_STATE_CACHE.get(path, ExportType.PDF)
    if state == ExportState.RUNNING.value:
        return None
    await EXPORT_STATE_CACHE.set(path, ExportType.PDF, ExportState.RUNNING.value)
    bt.add_task(_export_and_write_pdf, path)
    return None


async def async_export_status(path: str, export_type: ExportType) -> ExportState | None:
    state = await EXPORT_STATE_CACHE.get(path, export_type)
    if not state:
        return None
    estate = ExportState(state)
    return estate
