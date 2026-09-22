from fastapi import BackgroundTasks, FastAPI
from httpx import ASGITransport, AsyncClient
import pytest

from api.models import HtmlDocumentResponse
from api.routers.export_async import router
from api.services.export_async.export_async import async_export_status, html_export_async, pdf_export_async
from api.services.keyval_implementations import EXPORT_CACHE, EXPORT_STATE_CACHE, ExportState, ExportType


@pytest.mark.parametrize("include_edit_links", [False, True])
async def test_html_variants_have_independent_tasks_and_caches(mocker, include_edit_links):
    export_type = ExportType.HTML_EDIT_LINKS if include_edit_links else ExportType.HTML
    other_type = ExportType.HTML if include_edit_links else ExportType.HTML_EDIT_LINKS
    await EXPORT_STATE_CACHE.set("article", other_type, ExportState.RUNNING.value)
    await EXPORT_CACHE.set_html("article", not include_edit_links, "other html", "other front")
    document = HtmlDocumentResponse(html="requested html", front="requested front")
    exporter = mocker.patch("api.services.export_async.export_async.html_export", return_value=document)
    tasks = BackgroundTasks()

    assert await html_export_async("article", tasks, include_edit_links) is None
    assert await async_export_status("article", export_type) == ExportState.RUNNING
    duplicate = BackgroundTasks()
    assert await html_export_async("article", duplicate, include_edit_links) is None
    assert duplicate.tasks == []
    await tasks()

    exporter.assert_awaited_once_with("article", include_edit_links)
    assert await async_export_status("article", export_type) == ExportState.COMPLETE
    assert await async_export_status("article", other_type) == ExportState.RUNNING
    cached_tasks = BackgroundTasks()
    assert await html_export_async("article", cached_tasks, include_edit_links) == document
    assert cached_tasks.tasks == []
    assert await EXPORT_CACHE.get_html("article", not include_edit_links) == {
        "html": "other html", "front": "other front"
    }


async def test_html_edit_link_failure_can_be_retried(mocker):
    document = HtmlDocumentResponse(html="html", front="front")
    mocker.patch(
        "api.services.export_async.export_async.html_export",
        side_effect=[RuntimeError("render failed"), document],
    )
    tasks = BackgroundTasks()
    assert await html_export_async("article", tasks, True) is None
    await tasks()
    assert await async_export_status("article", ExportType.HTML_EDIT_LINKS) == ExportState.FAILED
    assert await async_export_status("article", ExportType.HTML) is None
    assert await EXPORT_CACHE.get_html("article", True) is None

    retry = BackgroundTasks()
    assert await html_export_async("article", retry, True) is None
    await retry()
    assert await async_export_status("article", ExportType.HTML_EDIT_LINKS) == ExportState.COMPLETE
    assert await html_export_async("article", BackgroundTasks(), True) == document


@pytest.mark.parametrize("params, include_edit_links", [({}, False), ({"include_edit_links": "true"}, True)])
async def test_html_async_endpoint_edit_links(mocker, params, include_edit_links):
    document = HtmlDocumentResponse(html="html", front="front")
    exporter = mocker.patch("api.services.export_async.export_async.html_export", return_value=document)
    app = FastAPI()
    app.include_router(router)
    query = {"path": "article", **params}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        assert (await client.get("/export/async/html", params=query)).status_code == 202
        response = await client.get("/export/async/html", params=query)
        assert response.status_code == 200
        assert response.json() == document.model_dump()
        exporter.assert_awaited_once_with("article", include_edit_links)
        export_type = "html_edit_links" if include_edit_links else "html"
        status = await client.get("/export/async/status", params={"path": "article", "export_type": export_type})
        assert status.status_code == 200
        assert status.json() == {"status": "Completed"}


async def test_pdf_running_does_not_queue_another_export():
    await EXPORT_STATE_CACHE.set("article", ExportType.PDF, ExportState.RUNNING.value)
    tasks = BackgroundTasks()

    assert await pdf_export_async("article", tasks) is None
    assert tasks.tasks == []


async def test_pdf_failure_can_be_retried(mocker):
    exporter = mocker.patch(
        "api.services.export_async.export_async.pdf_export",
        side_effect=[RuntimeError("render failed"), (b"%PDF-1.7", "article.pdf")],
    )
    tasks = BackgroundTasks()
    assert await pdf_export_async("article", tasks) is None
    assert await EXPORT_STATE_CACHE.get("article", ExportType.PDF) == ExportState.RUNNING.value
    await tasks()
    assert await EXPORT_STATE_CACHE.get("article", ExportType.PDF) == ExportState.FAILED.value
    assert await EXPORT_CACHE.get_pdf("article") is None

    retry = BackgroundTasks()
    assert await pdf_export_async("article", retry) is None
    await retry()
    assert await EXPORT_STATE_CACHE.get("article", ExportType.PDF) == ExportState.COMPLETE.value
    assert await pdf_export_async("article", BackgroundTasks()) == (b"%PDF-1.7", "article.pdf")
    assert exporter.await_count == 2


@pytest.mark.parametrize("state", [None, ExportState.COMPLETE.value])
async def test_pdf_cache_miss_queues_generation(mocker, state):
    if state is not None:
        await EXPORT_STATE_CACHE.set("article", ExportType.PDF, state)
    exporter = mocker.patch(
        "api.services.export_async.export_async.pdf_export", return_value=(b"pdf", "article.pdf")
    )
    tasks = BackgroundTasks()
    assert await pdf_export_async("article", tasks) is None
    exporter.assert_not_awaited()
    assert len(tasks.tasks) == 1
    await tasks()
    assert await EXPORT_CACHE.get_pdf("article") == (b"pdf", "article.pdf")
