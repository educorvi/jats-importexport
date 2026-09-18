import json
import logging

from fastapi import BackgroundTasks

from api.models import HtmlDocumentResponse
from api.services.export import html_export
from api.services.export_async.keyval_implementations import ASYNC_EXPORT_CACHE, ExportTypes, KeyValImplementation

logger = logging.getLogger(__name__)

async def _export_and_write_html(path: str):
    try:
        html: HtmlDocumentResponse = await html_export(path)
        data = {
            "front": html.front,
            "html": html.html,
        }
        ASYNC_EXPORT_CACHE.set(path, ExportTypes.HTML, json.dumps(data))
        logger.info(f"HTML exported and written to {path}")
    except Exception as e:
        logger.error(f"An error occurred while exporting HTML: {e}")
        return


def html_export_async(path: str, bt: BackgroundTasks) -> HtmlDocumentResponse | None:
    if ASYNC_EXPORT_CACHE.has(path, ExportTypes.HTML):
        string = ASYNC_EXPORT_CACHE.get(path, ExportTypes.HTML)
        data = json.loads(string)
        return HtmlDocumentResponse(**data)

    else:
        bt.add_task(_export_and_write_html, path)
        return None
