import io
import os

import httpx
import pytest
from jats_classes import (
    Article,
    Back,
    Body,
    Front,
    JATSDocument,
    Section,
)
from jats_storage_adapters.interface import AvailableStorageAdapters
from jats_storage_adapters.PloneStorageAdapter import PloneStorageAdapter

# ----------------------------------------------------
# Setup / Teardown env variables for storage adapters
# ----------------------------------------------------


@pytest.fixture
def clean_env():
    old_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(old_env)


# Helper to create mock httpx.Response with associated request to satisfy raise_for_status
def make_response(status_code=200, json=None, method="GET", url="http://localhost"):
    req = httpx.Request(method, url)
    return httpx.Response(status_code=status_code, json=json, request=req)


# ----------------------------------------------------
# Tests for PloneStorageAdapter Initialization & Factory
# ----------------------------------------------------


def test_plone_storage_adapter_init_missing_env(clean_env):
    os.environ.clear()
    with pytest.raises(ValueError, match="PLONE_BASE_URL environment variable is not set"):
        PloneStorageAdapter()

    os.environ["PLONE_BASE_URL"] = "http://localhost:8080/Plone"
    with pytest.raises(ValueError, match="PLONE_USERNAME and PLONE_PASSWORD environment variables must be set"):
        PloneStorageAdapter()


def test_plone_storage_adapter_init_success(clean_env):
    os.environ["PLONE_BASE_URL"] = "http://localhost:8080/Plone/"
    os.environ["PLONE_USERNAME"] = "admin"
    os.environ["PLONE_PASSWORD"] = "secret"

    adapter = PloneStorageAdapter()
    assert adapter.base_url == "http://localhost:8080/Plone"
    assert adapter.auth == ("admin", "secret")


def test_available_storage_adapters_factory(clean_env):
    os.environ["PLONE_BASE_URL"] = "http://localhost:8080/Plone"
    os.environ["PLONE_USERNAME"] = "admin"
    os.environ["PLONE_PASSWORD"] = "secret"

    # Supported creation
    adapter = AvailableStorageAdapters.create_instance_by_name("plone")
    assert isinstance(adapter, PloneStorageAdapter)

    # Unsupported creation
    with pytest.raises(ValueError, match="Storage adapter 'unsupported' is not supported"):
        AvailableStorageAdapters.create_instance_by_name("unsupported")


# ----------------------------------------------------
# Tests for PloneStorageAdapter list_articles
# ----------------------------------------------------


def test_plone_storage_adapter_lists_only_requested_range(clean_env, mocker):
    os.environ["PLONE_BASE_URL"] = "http://localhost:8080/Plone"
    os.environ["PLONE_USERNAME"] = "admin"
    os.environ["PLONE_PASSWORD"] = "secret"
    adapter = PloneStorageAdapter()
    mock_post = mocker.patch.object(
        adapter.httpx_client,
        "post",
        return_value=make_response(
            json={
                "items": [
                    {"@id": "http://localhost:8080/Plone/articles/two"},
                    {"@id": "http://localhost:8080/Plone/articles/three"},
                ],
                "items_total": 12,
                "batching": {"next": "http://localhost:8080/Plone/@querystring-search?b_start=4"},
            },
            method="POST",
            url="http://localhost:8080/Plone/@querystring-search",
        ),
    )

    paths, total = adapter.list_articles(fachbereiche=["law"], batch_start=2, batch_size=2)

    assert paths == ["/articles/two", "/articles/three"]
    assert total == 12
    mock_post.assert_called_once()
    assert mock_post.call_args.kwargs["json"]["b_start"] == 2
    assert mock_post.call_args.kwargs["json"]["b_size"] == 2


# ----------------------------------------------------
# Tests for PloneStorageAdapter Upload File
# ----------------------------------------------------


def test_plone_storage_adapter_upload_file(clean_env, mocker):
    os.environ["PLONE_BASE_URL"] = "http://localhost:8080/Plone"
    os.environ["PLONE_USERNAME"] = "admin"
    os.environ["PLONE_PASSWORD"] = "secret"

    adapter = PloneStorageAdapter()

    # Mock response from Plone API
    mock_response = make_response(
        status_code=201,
        json={"@id": "http://localhost:8080/Plone/jats-assets/image.png"},
        method="POST",
        url="http://localhost:8080/Plone/jats-assets",
    )
    mock_post = mocker.patch.object(adapter.httpx_client, "post", return_value=mock_response)
    # Container already exists — __create_container skips folder creation
    mocker.patch.object(
        adapter.httpx_client,
        "get",
        return_value=make_response(status_code=200, json={}, method="GET"),
    )

    # Perform file upload
    file_content = b"fake-png-binary-data"
    file_stream = io.BytesIO(file_content)
    file_stream.name = "image.png"

    url = adapter.upload_file(file_stream, "jats-assets")

    # Assert returned path is extracted from Plone URL @id
    assert url == "http://localhost:8080/Plone/jats-assets/image.png"

    # Verify httpx payload. Authentication and default headers are configured
    # on adapter.httpx_client rather than passed to every request.
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "http://localhost:8080/Plone/jats-assets"
    assert kwargs["json"]["@type"] == "Image"
    assert kwargs["json"]["title"] == "image.png"
    assert kwargs["json"]["image"]["filename"] == "image.png"
    assert kwargs["json"]["image"]["content-type"] == "image/png"  # guessed png


def test_plone_storage_adapter_upload_file_default_mimetype(clean_env, mocker):
    os.environ["PLONE_BASE_URL"] = "http://localhost:8080/Plone"
    os.environ["PLONE_USERNAME"] = "admin"
    os.environ["PLONE_PASSWORD"] = "secret"
    adapter = PloneStorageAdapter()

    mock_response = make_response(status_code=201, json={"@id": "http://localhost/path"}, method="POST")
    mock_post = mocker.patch.object(adapter.httpx_client, "post", return_value=mock_response)
    mocker.patch.object(
        adapter.httpx_client,
        "get",
        return_value=make_response(status_code=200, json={}, method="GET"),
    )

    # Upload file with no extension/unknown mimetype
    file_stream = io.BytesIO(b"data")
    file_stream.name = "unknown_file_type"

    adapter.upload_file(file_stream, "jats-assets")
    _, kwargs = mock_post.call_args
    assert kwargs["json"]["file"]["content-type"] == "application/octet-stream"


# ----------------------------------------------------
# Tests for PloneStorageAdapter download_file
# ----------------------------------------------------


def test_plone_storage_adapter_download_file_success(clean_env, mocker):
    os.environ["PLONE_BASE_URL"] = "http://localhost:8080/Plone"
    os.environ["PLONE_USERNAME"] = "admin"
    os.environ["PLONE_PASSWORD"] = "secret"
    adapter = PloneStorageAdapter()

    object_url = "http://localhost:8080/Plone/jats-assets/image.png"
    download_url = "http://localhost:8080/Plone/jats-assets/image.png/@@images/image"

    def mock_get_side_effect(url, *args, **kwargs):
        if url == object_url:
            return make_response(
                status_code=200,
                json={"@id": object_url, "image": {"download": download_url, "content-type": "image/png"}},
                url=url,
            )
        elif url == download_url:
            response = make_response(status_code=200, url=url)
            return httpx.Response(200, content=b"binary-image-data", request=response.request)
        raise AssertionError(f"Unexpected URL requested: {url}")

    mocker.patch.object(adapter.httpx_client, "get", side_effect=mock_get_side_effect)

    content, content_type = adapter.download_file(object_url)

    assert content == b"binary-image-data"
    assert content_type == "image/png"


def test_plone_storage_adapter_download_file_rejects_external_urls(clean_env):
    os.environ["PLONE_BASE_URL"] = "http://localhost:8080/Plone"
    os.environ["PLONE_USERNAME"] = "admin"
    os.environ["PLONE_PASSWORD"] = "secret"
    adapter = PloneStorageAdapter()

    with pytest.raises(ValueError, match="Refusing to download file"):
        adapter.download_file("http://evil.example.com/image.png")


# ----------------------------------------------------
# Tests for PloneStorageAdapter get_jats_document (Retrieve)
# ----------------------------------------------------


def test_plone_storage_adapter_get_jats_document_success(clean_env, mocker):
    os.environ["PLONE_BASE_URL"] = "http://localhost:8080/Plone"
    os.environ["PLONE_USERNAME"] = "admin"
    os.environ["PLONE_PASSWORD"] = "secret"
    adapter = PloneStorageAdapter()

    # We mock various Plone content nodes responses.
    def mock_get_side_effect(url, *args, **kwargs):
        if url == "http://localhost:8080/Plone/my-doc":
            # Article
            return make_response(
                status_code=200,
                json={
                    "@id": url,
                    "@type": "Article",
                    "items": [
                        {"@type": "Body", "@id": "http://localhost:8080/Plone/my-doc/body"},
                        {"@type": "Back", "@id": "http://localhost:8080/Plone/my-doc/back"},
                    ],
                    "title": "Hello",
                },
                url=url,
            )
        elif url == "http://localhost:8080/Plone/my-doc/body":
            # Body
            return make_response(
                status_code=200,
                json={
                    "@id": url,
                    "@type": "Body",
                    "items": [{"@type": "Section", "@id": "http://localhost:8080/Plone/my-doc/body/sec1"}],
                },
                url=url,
            )
        elif url == "http://localhost:8080/Plone/my-doc/body/sec1":
            # Section 1
            return make_response(
                status_code=200,
                json={
                    "@id": url,
                    "@type": "Section",
                    "sec_type": "intro",
                    "label": "1.",
                    "title": "Intro Title",
                    "label_title_raw": "<label>1.</label><title>Intro Title</title>",
                    "content_raw": "<p>Content</p>",
                    "items": [{"@type": "Section", "@id": "http://localhost:8080/Plone/my-doc/body/sec1/sub1"}],
                },
                url=url,
            )
        elif url == "http://localhost:8080/Plone/my-doc/body/sec1/sub1":
            # Subsection
            return make_response(
                status_code=200,
                json={
                    "@id": url,
                    "@type": "Section",
                    "sec_type": "subsection",
                    "label": "1.1",
                    "title": "Sub Title",
                    "content_raw": "Sub Content",
                    "items": [],
                },
                url=url,
            )
        elif url == "http://localhost:8080/Plone/my-doc/back":
            # Back
            return make_response(
                status_code=200,
                json={
                    "@id": url,
                    "@type": "Back",
                    "items": [{"@type": "AppendixGroup", "@id": "http://localhost:8080/Plone/my-doc/back/appg1"}],
                },
                url=url,
            )
        elif url == "http://localhost:8080/Plone/my-doc/back/appg1":
            # Appendix Group
            return make_response(
                status_code=200,
                json={
                    "@id": url,
                    "@type": "AppendixGroup",
                    "title": "App Group",
                    "label": "G1",
                    "content_raw": "Group Content",
                    "items": [{"@type": "Appendix", "@id": "http://localhost:8080/Plone/my-doc/back/appg1/app1"}],
                },
                url=url,
            )
        elif url == "http://localhost:8080/Plone/my-doc/back/appg1/app1":
            # Appendix
            return make_response(
                status_code=200,
                json={
                    "@id": url,
                    "@type": "Appendix",
                    "sec_type": "appendix",
                    "label": "A1",
                    "title": "Appendix 1",
                    "content_raw": "Appendix Content",
                    "items": [
                        {"@type": "Section", "@id": "http://localhost:8080/Plone/my-doc/back/appg1/app1/appsec1"}
                    ],
                },
                url=url,
            )
        elif url == "http://localhost:8080/Plone/my-doc/back/appg1/app1/appsec1":
            # Section inside Appendix
            return make_response(
                status_code=200, json={"@id": url, "@type": "Section", "title": "App Sec Title", "items": []}, url=url
            )
        else:
            return make_response(status_code=404, url=url)

    mocker.patch.object(adapter.httpx_client, "get", side_effect=mock_get_side_effect)

    # Perform document retrieval
    doc = adapter.get_jats_document("/my-doc")

    # Assert correct domain models structure reconstruction
    assert isinstance(doc, JATSDocument)
    assert doc.article.front.title == "Hello"
    assert len(doc.article.body.sections) == 1

    sec = doc.article.body.sections[0]
    assert sec.title == "Intro Title"
    assert sec.sec_type == "intro"
    assert len(sec.sections) == 1

    sub = sec.sections[0]
    assert sub.title == "Sub Title"

    assert len(doc.article.back.appendix_groups) == 1
    app_group = doc.article.back.appendix_groups[0]
    assert app_group.label == "G1"
    assert len(app_group.appendixes) == 1

    app = app_group.appendixes[0]
    assert app.title == "Appendix 1"
    assert len(app.sections) == 1
    assert app.sections[0].title == "App Sec Title"


def test_plone_storage_adapter_get_jats_document_missing_parts(clean_env, mocker):
    os.environ["PLONE_BASE_URL"] = "http://localhost:8080/Plone"
    os.environ["PLONE_USERNAME"] = "admin"
    os.environ["PLONE_PASSWORD"] = "secret"
    adapter = PloneStorageAdapter()

    # Return incomplete article structure (missing Front/Body/Back)
    mock_response = make_response(
        status_code=200,
        json={
            "@id": "http://localhost:8080/Plone/my-doc",
            "@type": "Article",
            "items": [],
        },
        url="http://localhost:8080/Plone/my-doc",
    )
    mocker.patch.object(adapter.httpx_client, "get", return_value=mock_response)

    with pytest.raises(ValueError, match="Article must contain Front and Body"):
        adapter.get_jats_document("/my-doc")


# ----------------------------------------------------
# Tests for PloneStorageAdapter save_jats_document (Save)
# ----------------------------------------------------


def test_plone_storage_adapter_save_jats_document_success(clean_env, mocker):
    os.environ["PLONE_BASE_URL"] = "http://localhost:8080/Plone"
    os.environ["PLONE_USERNAME"] = "admin"
    os.environ["PLONE_PASSWORD"] = "secret"
    adapter = PloneStorageAdapter()

    # Reusable responses
    res_200 = lambda url: make_response(status_code=200, json={}, url=url)
    res_404 = lambda url: make_response(status_code=404, json={}, url=url)

    # Dict to keep track of created objects in Plone
    created_posts = []

    def mock_post_side_effect(url, *args, **kwargs):
        json_body = kwargs.get("json", {})
        item_id = json_body.get("id") or json_body.get("title") or "item"
        new_url = f"{url}/{item_id}".lower()
        created_posts.append((url, json_body))
        return make_response(status_code=201, json={"@id": new_url}, method="POST", url=url)

    def mock_get_side_effect(url, *args, **kwargs):
        # We need to simulate folder existence check.
        if url == "http://localhost:8080/Plone/jats-file":
            return res_404(url)  # doesn't exist, will be created
        return res_200(url)

    mocker.patch.object(adapter.httpx_client, "get", side_effect=mock_get_side_effect)
    mocker.patch.object(adapter.httpx_client, "post", side_effect=mock_post_side_effect)

    # Let's create a minimal JATSDocument to save
    front = Front.empty()
    front.title = "Save Test"
    sub_sec = Section(
        sec_type="sub", label=None, title="Sub", label_title_raw="", content_raw="Subcontent", sections=[]
    )
    body_sec = Section(
        sec_type="main", label=None, title="Main", label_title_raw="", content_raw="Maincontent", sections=[sub_sec]
    )
    body = Body(sections=[body_sec])
    back = Back(appendix_groups=[])
    article = Article(front=front, body=body, back=back)
    document = JATSDocument(article=article)

    # Save document to Plone
    path = adapter.save_jats_document(document, "jats-file")

    # Verify return value is path of created article
    assert path == "/jats-file/save test".lower()

    # Check that Folders, Article, Front, Body, Sections were recursively posted
    post_types = [p[1]["@type"] for p in created_posts]
    assert "Folder" in post_types
    assert "Article" in post_types
    assert "Body" in post_types
    assert "Section" in post_types

    # Verify section nesting posting URL
    sec_posts = [p for p in created_posts if p[1]["@type"] == "Section"]
    assert len(sec_posts) == 2

    sub_sec_url = sec_posts[1][0]
    # Subsection is posted *inside* parent section URL
    assert "main" in sub_sec_url
