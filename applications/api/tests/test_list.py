from api.config import APIConfig
from api.main import app
from api.routers.list import list_articles
from starlette.requests import Request


async def test_list_articles_returns_requested_batch(mocker):
    list_articles_mock = mocker.patch(
        "api.services.list.list_articles",
        return_value=(["/articles/2", "/articles/3", "/articles/4"], 7),
    )

    request = Request(
        {
            "type": "http",
            "scheme": "https",
            "server": ("example.test", 443),
            "path": "/list/",
            "query_string": b"fachbereiche=law&fachbereiche=tax&batch_start=2&batch_size=3",
            "headers": [],
        }
    )
    response = await list_articles(request, ["law", "tax"], None, None, None, batch_start=2, batch_size=3)

    list_articles_mock.assert_awaited_once_with(["law", "tax"], None, None, None, 2, 3)
    assert response.articles == ["/articles/2", "/articles/3", "/articles/4"]
    assert response.count == 7
    assert response.batching.model_dump() == {
        "current": "https://example.test/list/?fachbereiche=law&fachbereiche=tax&batch_start=2&batch_size=3",
        "next": "https://example.test/list/?fachbereiche=law&fachbereiche=tax&batch_start=5&batch_size=3",
        "previous": "https://example.test/list/?fachbereiche=law&fachbereiche=tax&batch_start=0&batch_size=3",
        "first": "https://example.test/list/?fachbereiche=law&fachbereiche=tax&batch_start=0&batch_size=3",
        "last": "https://example.test/list/?fachbereiche=law&fachbereiche=tax&batch_start=6&batch_size=3",
    }


def test_list_articles_documents_batch_parameter_constraints():
    parameters = {
        parameter["name"]: parameter for parameter in app.openapi()["paths"]["/list/"]["get"]["parameters"]
    }

    assert parameters["batch_start"]["schema"]["minimum"] == 0
    assert parameters["batch_size"]["schema"]["minimum"] == 1
    assert parameters["batch_size"]["schema"]["maximum"] == APIConfig.LIST_BATCH_SIZE
    assert parameters["batch_size"]["schema"]["default"] == APIConfig.LIST_BATCH_SIZE
