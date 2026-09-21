from fastapi import BackgroundTasks
import pytest

from api.services.export_async.export_async import pdf_export_async
from api.services.keyval_implementations import EXPORT_CACHE, EXPORT_STATE_CACHE, ExportState, ExportTypes


async def test_pdf_running_does_not_queue_another_export():
    await EXPORT_STATE_CACHE.set("article", ExportTypes.PDF, ExportState.RUNNING.value)
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
    assert await EXPORT_STATE_CACHE.get("article", ExportTypes.PDF) == ExportState.RUNNING.value
    await tasks()
    assert await EXPORT_STATE_CACHE.get("article", ExportTypes.PDF) == ExportState.FAILED.value
    assert await EXPORT_CACHE.get_pdf("article") is None

    retry = BackgroundTasks()
    assert await pdf_export_async("article", retry) is None
    await retry()
    assert await EXPORT_STATE_CACHE.get("article", ExportTypes.PDF) == ExportState.COMPLETE.value
    assert await pdf_export_async("article", BackgroundTasks()) == (b"%PDF-1.7", "article.pdf")
    assert exporter.await_count == 2


@pytest.mark.parametrize("state", [None, ExportState.COMPLETE.value])
async def test_pdf_cache_miss_queues_generation(mocker, state):
    if state is not None:
        await EXPORT_STATE_CACHE.set("article", ExportTypes.PDF, state)
    exporter = mocker.patch(
        "api.services.export_async.export_async.pdf_export", return_value=(b"pdf", "article.pdf")
    )
    tasks = BackgroundTasks()
    assert await pdf_export_async("article", tasks) is None
    exporter.assert_not_awaited()
    assert len(tasks.tasks) == 1
    await tasks()
    assert await EXPORT_CACHE.get_pdf("article") == (b"pdf", "article.pdf")
