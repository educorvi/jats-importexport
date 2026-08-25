from jats_storage_adapters.errors import PathNotFoundExpection
import base64
import io
import zipfile

from jats_storage_adapters.interface import GetJATSDocumentOptions, SaveJATSDocumentOptions, StorageAdapter
import pytest
from api.config import APIConfig
from api.main import app
from fastapi.testclient import TestClient
from jats_classes import JATSDocument

client = TestClient(app)

# ----------------------------------------------------
# XML Snippets for testing
# ----------------------------------------------------

VALID_JATS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<article>
    <front>
        <journal-meta>
            <journal-id/>
            <issn/>
        </journal-meta>
        <article-meta>
            <title-group>
                <article-title>API Test Article</article-title>
            </title-group>
        </article-meta>
    </front>
    <body>
        <sec>
            <title>Section 1</title>
            <p>Content.</p>
        </sec>
    </body>
    <back></back>
</article>
"""

XML_WITH_IMAGE = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink">
    <front>
        <journal-meta>
            <journal-id/>
            <issn/>
        </journal-meta>
        <article-meta>
            <title-group>
                <article-title>Image Reference Article</article-title>
            </title-group>
        </article-meta>
    </front>
    <body>
        <sec>
            <title>Sec 1</title>
            <p>Look at <inline-graphic xlink:href="images/pic.png"/></p>
        </sec>
    </body>
    <back></back>
</article>
"""

# ----------------------------------------------------
# Helper to build in-memory ZIPs
# ----------------------------------------------------


def make_zip_bytes(files_dict: dict, add_symlink: bool = False, symlink_name: str = "link") -> bytes:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in files_dict.items():
            zip_file.writestr(filename, content)
        if add_symlink:
            # Create a symbolic link entry in the zip
            info = zipfile.ZipInfo(symlink_name)
            # Set symlink flag in external attributes (S_IFLNK = 0xA000)
            info.external_attr = 0xA0000000
            zip_file.writestr(info, "target_file.txt")
    return zip_buffer.getvalue()


# ----------------------------------------------------
# Mock Storage Adapter
# ----------------------------------------------------


class MockStorageAdapter(StorageAdapter):
    def list_articles(self, fachbereiche: list[str] | None = None, sachgebiete: list[str] | None = None,
                      organisationseinheiten: list[str] | None = None, rubriken: list[str] | None = None,
                      batch_start: int = 0, batch_size: int | None = None) -> tuple[list[str], int]:
        return [], 0

    def __init__(self):
        self.uploaded_files = []
        self.saved_docs = []

    def upload_file(self, file, container) -> str:
        import os

        name = os.path.basename(getattr(file, "name", "file") or "file")
        url = f"http://mockstore/assets/{name}"
        self.uploaded_files.append((name, container, url))
        return url

    def get_jats_document(self, path: str, options: GetJATSDocumentOptions | None = None) -> JATSDocument:
        if path == "nonexistent":
            raise PathNotFoundExpection(path)
        # Return a valid JATSDocument
        return JATSDocument.from_xml(VALID_JATS_XML, xsd_path=None)

    def save_jats_document(self, document: JATSDocument, container: str, options: SaveJATSDocumentOptions | None = None) -> str:
        self.saved_docs.append((document, container))
        title = document.article.front.title or "article"
        return f"http://mockstore/jats-file/{title.lower().replace(' ', '-')}"

    def link_related_articles(self) -> list[str]:
        raise NotImplementedError("link_related_articles is not implemented in MockStorageAdapter")

    def list_fachbereiche(self) -> list[str]:
        raise NotImplementedError("list_fachbereiche is not implemented in MockStorageAdapter")

    def list_sachgebiete(self) -> list[str]:
        raise NotImplementedError("list_sachgebiete is not implemented in MockStorageAdapter")


@pytest.fixture
def mock_adapter(mocker):
    adapter = MockStorageAdapter()
    mocker.patch("api.services.upload.get_adapter_instance", return_value=adapter)
    mocker.patch("api.services.export.get_adapter_instance", return_value=adapter)
    mocker.patch.object(APIConfig, "API_KEY", None)
    return adapter


# ----------------------------------------------------
# Tests for Status Endpoint
# ----------------------------------------------------


def test_status_endpoint():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ----------------------------------------------------
# Tests for Export Endpoints
# ----------------------------------------------------


def test_export_jats(mock_adapter):
    # Standard JSON accept
    response = client.get("/export/jats?path=doc1")
    assert response.status_code == 200
    assert "jats" in response.json()
    assert "API Test Article" in response.json()["jats"]


def test_export_html(mock_adapter):
    # Standard JSON accept
    response = client.get("/export/html?path=doc1")
    assert response.status_code == 200
    assert "html" in response.json()


def test_export_md(mock_adapter):
    response = client.get("/export/md?path=doc1")
    assert response.status_code == 200
    assert "md" in response.json()


def test_export_md_nonexistent_path(mock_adapter):
    response = client.get("/export/md?path=nonexistent")
    assert response.status_code == 404


def test_export_md_requires_auth(mocker, mock_adapter):
    mocker.patch.object(APIConfig, "API_KEY", "secret")
    response = client.get("/export/md?path=doc1")
    assert response.status_code == 401

    response = client.get("/export/md?path=doc1", headers={"X-API-Key": "secret"})
    assert response.status_code == 200


# ----------------------------------------------------
# Tests for XML Upload Endpoint
# ----------------------------------------------------


def test_upload_xml_multipart_success(mock_adapter):
    file_payload = {"xml_file": ("test.xml", VALID_JATS_XML, "application/xml")}
    response = client.post("/upload/xml", files=file_payload)
    assert response.status_code == 200
    response_urls = response.json()["urls"]
    assert len(response_urls) == 1
    assert response_urls[0] == "http://mockstore/jats-file/api-test-article"
    assert len(mock_adapter.saved_docs) == 1


def test_upload_xml_multipart_malformed(mock_adapter):
    malformed_xml = "<article><front>unclosed-tag</article>"
    file_payload = {"xml_file": ("test.xml", malformed_xml, "application/xml")}
    response = client.post("/upload/xml", files=file_payload)
    assert response.status_code == 400
    assert "malformed" in response.json()["detail"].lower()


def test_upload_xml_multipart_too_large(mock_adapter, mocker):
    mocker.patch("api.services.upload.MAX_ZIP_UNCOMPRESSED_SIZE", 10)  # limit to 10 bytes
    file_payload = {"xml_file": ("test.xml", VALID_JATS_XML, "application/xml")}
    response = client.post("/upload/xml", files=file_payload)
    assert response.status_code == 413
    assert "too large" in response.json()["detail"].lower()


def test_upload_xml_json_data_uri_success(mock_adapter):
    encoded = base64.b64encode(VALID_JATS_XML.encode("utf-8")).decode("ascii")
    data_uri = f"data:application/xml;base64,{encoded}"

    response = client.post("/upload/xml", json={"xml_file": data_uri})
    assert response.status_code == 200
    response_urls = response.json()["urls"]
    assert len(response_urls) == 1
    assert response_urls[0] == "http://mockstore/jats-file/api-test-article"


def test_upload_xml_json_data_uri_malformed_header(mock_adapter):
    response = client.post("/upload/xml", json={"xml_file": "not-a-data-uri"})
    assert response.status_code == 400
    assert "invalid data uri" in response.json()["detail"].lower()


def test_upload_xml_json_data_uri_malformed_base64(mock_adapter):
    response = client.post("/upload/xml", json={"xml_file": "data:application/xml;base64,invalid-base64!!!"})
    assert response.status_code == 400
    assert "failed to decode base64" in response.json()["detail"].lower()


# ----------------------------------------------------
# Tests for ZIP Upload Endpoint (Security & Validation)
# ----------------------------------------------------


def test_upload_zip_not_a_zip(mock_adapter):
    # Uploading raw non-zip bytes
    file_payload = {"zip_file": ("test.zip", b"not-a-zip-content", "application/zip")}
    response = client.post("/upload/zip", files=file_payload)
    assert response.status_code == 415
    assert "must be a zip archive" in response.json()["detail"].lower()


def test_upload_zip_empty_zip(mock_adapter):
    empty_zip = make_zip_bytes({})
    file_payload = {"zip_file": ("test.zip", empty_zip, "application/zip")}
    response = client.post("/upload/zip", files=file_payload)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_upload_zip_too_many_files(mock_adapter, mocker):
    mocker.patch("api.services.upload.MAX_ZIP_FILE_COUNT", 1)  # limit to 1 file
    zip_bytes = make_zip_bytes({"test1.xml": VALID_JATS_XML, "test2.xml": VALID_JATS_XML})
    file_payload = {"zip_file": ("test.zip", zip_bytes, "application/zip")}
    response = client.post("/upload/zip", files=file_payload)
    assert response.status_code == 413
    assert "contains too many files" in response.json()["detail"].lower()


def test_upload_zip_too_large(mock_adapter, mocker):
    mocker.patch("api.services.upload.MAX_ZIP_UNCOMPRESSED_SIZE", 5)  # limit to 5 bytes
    zip_bytes = make_zip_bytes({"test1.xml": VALID_JATS_XML})
    file_payload = {"zip_file": ("test.zip", zip_bytes, "application/zip")}
    response = client.post("/upload/zip", files=file_payload)
    assert response.status_code == 413
    assert "too large" in response.json()["detail"].lower()


def test_upload_zip_path_traversal_absolute(mock_adapter):
    # Member name with absolute path
    zip_bytes = make_zip_bytes({"/etc/passwd": "content"})
    file_payload = {"zip_file": ("test.zip", zip_bytes, "application/zip")}
    response = client.post("/upload/zip", files=file_payload)
    assert response.status_code == 400
    assert "invalid file paths" in response.json()["detail"].lower()


def test_upload_zip_path_traversal_relative(mock_adapter):
    # Member name containing relative traversal components
    zip_bytes = make_zip_bytes({"../../escaped.txt": "content"})
    file_payload = {"zip_file": ("test.zip", zip_bytes, "application/zip")}
    response = client.post("/upload/zip", files=file_payload)
    assert response.status_code == 400
    assert "invalid file paths" in response.json()["detail"].lower()


def test_upload_zip_symlink_rejection(mock_adapter):
    # ZIP containing symbolic link
    zip_bytes = make_zip_bytes({"test.xml": VALID_JATS_XML}, add_symlink=True)
    file_payload = {"zip_file": ("test.zip", zip_bytes, "application/zip")}
    response = client.post("/upload/zip", files=file_payload)
    assert response.status_code == 400
    assert "must not contain symbolic links" in response.json()["detail"].lower()


def test_upload_zip_no_xml_file(mock_adapter):
    # ZIP with no XML files
    zip_bytes = make_zip_bytes({"image.png": b"fake-png"})
    file_payload = {"zip_file": ("test.zip", zip_bytes, "application/zip")}
    response = client.post("/upload/zip", files=file_payload)
    assert response.status_code == 400
    assert "no xml file found" in response.json()["detail"].lower()


# ----------------------------------------------------
# Success ZIP Upload & Asset Processing Verification
# ----------------------------------------------------


def test_upload_zip_success(mock_adapter):
    # Create valid zip containing XML referencing an image file and the image file itself.
    files = {"article.xml": XML_WITH_IMAGE, "images/pic.png": b"fake-png-bytes"}
    zip_bytes = make_zip_bytes(files)
    file_payload = {"zip_file": ("test.zip", zip_bytes, "application/zip")}

    response = client.post("/upload/zip", files=file_payload)
    assert response.status_code == 200
    response_urls = response.json()["urls"]
    assert len(response_urls) == 1
    assert response_urls[0] == "http://mockstore/jats-file/image-reference-article"

    # Verify that the image file was successfully uploaded to assets container
    assert len(mock_adapter.uploaded_files) == 1
    uploaded_name, container, url = mock_adapter.uploaded_files[0]
    assert uploaded_name == "pic.png"
    assert container == "jats-assets"
    assert url == "http://mockstore/assets/pic.png"

    # Verify that the saved JATSDocument was updated to point to the uploaded image URL!
    saved_doc, container = mock_adapter.saved_docs[0]
    assert isinstance(saved_doc, JATSDocument)

    # Check content_raw of the section for updated xlink:href reference modification
    xml_str = saved_doc.article.body.sections[0].content_raw
    assert (
        'xlink:href="http://mockstore/assets/pic.png"' in xml_str or 'href="http://mockstore/assets/pic.png"' in xml_str
    )


# ----------------------------------------------------
# Tests for API Key Authentication
# ----------------------------------------------------


def test_auth_status_is_always_public(mocker):
    mocker.patch.object(APIConfig, "API_KEY", "secret")
    response = client.get("/status")
    assert response.status_code == 200


def test_auth_disabled_when_no_api_key_set(mocker, mock_adapter):
    mocker.patch.object(APIConfig, "API_KEY", None)
    response = client.get("/export/jats?path=doc1")
    assert response.status_code == 200


def test_auth_rejects_missing_key(mocker, mock_adapter):
    mocker.patch.object(APIConfig, "API_KEY", "secret")
    response = client.get("/export/jats?path=doc1")
    assert response.status_code == 401


def test_auth_rejects_wrong_key(mocker, mock_adapter):
    mocker.patch.object(APIConfig, "API_KEY", "secret")
    response = client.get("/export/jats?path=doc1", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


def test_auth_accepts_correct_key(mocker, mock_adapter):
    mocker.patch.object(APIConfig, "API_KEY", "secret")
    response = client.get("/export/jats?path=doc1", headers={"X-API-Key": "secret"})
    assert response.status_code == 200


def test_auth_upload_requires_key(mocker, mock_adapter):
    mocker.patch.object(APIConfig, "API_KEY", "secret")
    file_payload = {"xml_file": ("test.xml", VALID_JATS_XML, "application/xml")}
    response = client.post("/upload/xml", files=file_payload)
    assert response.status_code == 401

    response = client.post("/upload/xml", files=file_payload, headers={"X-API-Key": "secret"})
    assert response.status_code == 200
