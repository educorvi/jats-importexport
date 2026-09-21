import logging

from fastapi import BackgroundTasks

from api.models import HtmlDocumentResponse
from api.services.export import html_export, pdf_export
from api.services.keyval_implementations import EXPORT_CACHE, EXPORT_STATE_CACHE, ExportState, ExportTypes

logger = logging.getLogger(__name__)


async def _export_and_write_html(path: str):
    try:
        html: HtmlDocumentResponse = await html_export(path)
        await EXPORT_CACHE.set_html(path, False, html.html, html.front)
        await EXPORT_STATE_CACHE.set(path, ExportTypes.HTML, ExportState.COMPLETE.value)
        logger.info(f"HTML exported and written to {path}")
    except Exception as e:
        await EXPORT_STATE_CACHE.set(path, ExportTypes.HTML, ExportState.FAILED.value)
        logger.error(f"An error occurred while exporting HTML: {e}")
        return


async def html_export_async(path: str, bt: BackgroundTasks) -> HtmlDocumentResponse | None:
    cached_html = await EXPORT_CACHE.get_html(path, False)
    if cached_html:
        return HtmlDocumentResponse(**cached_html)
    state = await EXPORT_STATE_CACHE.get(path, ExportTypes.HTML)
    if state == ExportState.RUNNING.value:
        return None
    else:
        await EXPORT_STATE_CACHE.set(path, ExportTypes.HTML, ExportState.RUNNING.value)
        bt.add_task(_export_and_write_html, path)
        return None


async def _export_and_write_pdf(path: str):
    try:
        content, filename = await pdf_export(path)
        await EXPORT_CACHE.set_pdf(path, content, filename)
        await EXPORT_STATE_CACHE.set(path, ExportTypes.PDF, ExportState.COMPLETE.value)
        logger.info(f"PDF exported and written to {path}")
    except Exception as e:
        await EXPORT_STATE_CACHE.set(path, ExportTypes.PDF, ExportState.FAILED.value)
        logger.error(f"An error occurred while exporting PDF: {e}")


async def pdf_export_async(path: str, bt: BackgroundTasks) -> tuple[bytes, str] | None:
    cached_pdf = await EXPORT_CACHE.get_pdf(path)
    if cached_pdf is not None:
        return cached_pdf
    state = await EXPORT_STATE_CACHE.get(path, ExportTypes.PDF)
    if state == ExportState.RUNNING.value:
        return None
    await EXPORT_STATE_CACHE.set(path, ExportTypes.PDF, ExportState.RUNNING.value)
    bt.add_task(_export_and_write_pdf, path)
    return None
