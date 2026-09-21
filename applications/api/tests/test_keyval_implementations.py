import pytest

from api.services.keyval_implementations import ExportTypes, InMemoryCache


@pytest.fixture
async def cache():
    cache = InMemoryCache(0, cache_name="TEST_CACHE")
    await cache.init()
    return cache


async def test_cache_normalizes_paths_and_separates_export_types(cache):
    await cache.set("/articles/one/", ExportTypes.MD, "markdown")
    await cache.set("articles/one", ExportTypes.JATS, "xml")
    await cache.set("articles/two", ExportTypes.MD, "other")

    assert await cache.get("articles/one", ExportTypes.MD) == "markdown"
    assert await cache.get("/articles/one/", ExportTypes.JATS) == "xml"
    await cache.set("articles/one", ExportTypes.MD, "updated")
    assert await cache.get("/articles/one", ExportTypes.MD) == "updated"
    assert (await cache.get_cache_status()).model_dump() == {
        "implementation": "InMemory", "items_in_cache": 3,
    }

    await cache.delete("/articles/one/", ExportTypes.MD)
    assert await cache.get("articles/one", ExportTypes.MD) is None
    assert await cache.get("articles/one", ExportTypes.JATS) == "xml"
    assert await cache.get("articles/two", ExportTypes.MD) == "other"


async def test_delete_path_removes_all_formats_but_preserves_other_paths(cache):
    for export_type in ExportTypes:
        await cache.set("articles/one", export_type, "one")
        await cache.set("articles/two", export_type, "two")

    await cache.delete("/articles/one/", None)
    for export_type in ExportTypes:
        assert await cache.get("articles/one", export_type) is None
        assert await cache.get("articles/two", export_type) == "two"

    await cache.delete("missing", None)
    await cache.delete("missing", ExportTypes.MD)
    assert (await cache.get_cache_status()).items_in_cache == len(ExportTypes)
    await cache.delete_all()
    assert (await cache.get_cache_status()).items_in_cache == 0
    for export_type in ExportTypes:
        assert await cache.get("articles/two", export_type) is None


async def test_html_variants_round_trip_independently(cache):
    assert await cache.get_html("article", False) is None
    assert await cache.get_html("article", True) is None
    await cache.set_html("/article/", False, "<p>Normal</p>", "<header>Title</header>")
    await cache.set_html("article", True, '<a href="/edit">Edit</a>', "")

    assert await cache.get_html("article", False) == {
        "html": "<p>Normal</p>", "front": "<header>Title</header>",
    }
    assert await cache.get_html("/article/", True) == {
        "html": '<a href="/edit">Edit</a>', "front": "",
    }
    await cache.delete("article", ExportTypes.HTML_EDIT_LINKS)
    assert await cache.get_html("article", True) is None
    assert await cache.get_html("article", False) is not None


async def test_pdf_binary_and_filename_round_trip(cache):
    assert await cache.get_pdf("article") is None
    content = b"%PDF-1.7\n\x00\xff\x80"
    await cache.set_pdf("/article/", content, "article.pdf")
    assert await cache.get_pdf("article") == (content, "article.pdf")
    await cache.delete("article", ExportTypes.PDF)
    assert await cache.get_pdf("article") is None
