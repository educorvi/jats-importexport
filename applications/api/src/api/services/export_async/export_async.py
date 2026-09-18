import logging

from fastapi import BackgroundTasks

from api.models import HtmlDocumentResponse
from api.services.export import html_export
from api.services.keyval_implementations import EXPORT_CACHE

logger = logging.getLogger(__name__)


async def _export_and_write_html(path: str):
    try:
        html: HtmlDocumentResponse = await html_export(path)
        await EXPORT_CACHE.set_html(path, False, html.html, html.front)
        logger.info(f"HTML exported and written to {path}")
    except Exception as e:
        logger.error(f"An error occurred while exporting HTML: {e}")
        return


async def html_export_async(path: str, bt: BackgroundTasks) -> HtmlDocumentResponse | None:
    cached_html = await EXPORT_CACHE.get_html(path, False)
    if cached_html:
        return HtmlDocumentResponse(**cached_html)
    else:
        bt.add_task(_export_and_write_html, path)
        return None
