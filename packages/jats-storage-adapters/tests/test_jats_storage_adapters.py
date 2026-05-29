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
    mock_post = mocker.patch("httpx.post", return_value=mock_response)

    # Perform file upload
    file_content = b"fake-png-binary-data"
    file_stream = io.BytesIO(file_content)
    file_stream.name = "image.png"

    url = adapter.upload_file(file_stream, "jats-assets")

    # Assert returned path is extracted from Plone URL @id
    assert url == "http://localhost:8080/Plone/jats-assets/image.png"

    # Verify httpx payload and headers
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "http://localhost:8080/Plone/jats-assets"
    assert kwargs["auth"] == ("admin", "secret")
    assert kwargs["json"]["@type"] == "File"
    assert kwargs["json"]["title"] == "image.png"
    assert kwargs["json"]["file"]["filename"] == "image.png"
    assert kwargs["json"]["file"]["content-type"] == "image/png"  # guessed png


def test_plone_storage_adapter_upload_file_default_mimetype(clean_env, mocker):
    os.environ["PLONE_BASE_URL"] = "http://localhost:8080/Plone"
    os.environ["PLONE_USERNAME"] = "admin"
    os.environ["PLONE_PASSWORD"] = "secret"
    adapter = PloneStorageAdapter()

    mock_response = make_response(status_code=201, json={"@id": "http://localhost/path"}, method="POST")
    mocker.patch("httpx.post", return_value=mock_response)

    # Upload file with no extension/unknown mimetype
    file_stream = io.BytesIO(b"data")
    file_stream.name = "unknown_file_type"

    adapter.upload_file(file_stream, "jats-assets")
    _, kwargs = httpx.post.call_args
    assert kwargs["json"]["file"]["content-type"] == "application/octet-stream"


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
                        {
                            "@type": "Front",
                            "@id": "http://localhost:8080/Plone/my-doc/front",
                            "content_raw": "<article-title>Hello</article-title>",
                        },
                        {"@type": "Body", "@id": "http://localhost:8080/Plone/my-doc/body"},
                        {"@type": "Back", "@id": "http://localhost:8080/Plone/my-doc/back"},
                    ],
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

    mocker.patch("httpx.get", side_effect=mock_get_side_effect)

    # Perform document retrieval
    doc = adapter.get_jats_document("/my-doc")

    # Assert correct domain models structure reconstruction
    assert isinstance(doc, JATSDocument)
    assert doc.article.front.content_raw == "<article-title>Hello</article-title>"
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
            "items": [{"@type": "Front", "@id": "http://localhost/front", "content_raw": "..."}],
        },
        url="http://localhost:8080/Plone/my-doc",
    )
    mocker.patch("httpx.get", return_value=mock_response)

    with pytest.raises(ValueError, match="Article must contain Front, Body, and Back"):
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

    mocker.patch("httpx.get", side_effect=mock_get_side_effect)
    mocker.patch("httpx.post", side_effect=mock_post_side_effect)

    # Let's create a minimal JATSDocument to save
    front = Front(
        content_raw="<article-meta><title-group><article-title>Save Test</article-title></title-group></article-meta>"
    )
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
    assert "Front" in post_types
    assert "Body" in post_types
    assert "Section" in post_types

    # Verify section nesting posting URL
    sec_posts = [p for p in created_posts if p[1]["@type"] == "Section"]
    assert len(sec_posts) == 2

    sub_sec_url = sec_posts[1][0]
    # Subsection is posted *inside* parent section URL
    assert "main" in sub_sec_url
