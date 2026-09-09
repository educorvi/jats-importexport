"""Plone Storage Adapter implementation.

Connects to a live Plone CMS REST API to manage JATS documents and files.
"""

import logging
import os
from typing import BinaryIO, cast, overload
from urllib.parse import urlparse

import httpx
from httpx import HTTPStatusError
from jats_classes import (
    Front,
    JATSDocument,
)

from ..errors import InternalError, PathNotFoundExpection
from ..interface import GetJATSDocumentOptions as BaseGetJATSDocumentOptions
from ..interface import SaveJATSDocumentOptions, StorageAdapter
from .download import PloneDownloadService, PloneGetJATSDocumentOptions
from .listing import PloneListingService
from .modify import PloneModifyService
from .upload import PloneUploadService

logger = logging.getLogger(__name__)


class PloneStorageAdapter(StorageAdapter):
    """Storage adapter interacting with a Plone instance over the REST API.

    Requires the following environment variables:
    - PLONE_BASE_URL: Root URL of Plone CMS (e.g. http://localhost:8080/Plone).
    - PLONE_USERNAME: Authenticated username for API operations.
    - PLONE_PASSWORD: Password corresponding to user credentials.
    """

    base_url: str
    auth: tuple[str, str]
    httpx_client: httpx.Client

    def __init__(self):
        """Initialize storage adapter loading credentials from environment."""
        base_url = os.environ.get("PLONE_BASE_URL")
        if base_url is None:
            raise ValueError("PLONE_BASE_URL environment variable is not set")
        self.base_url = base_url.rstrip("/")

        username = os.environ.get("PLONE_USERNAME")
        password = os.environ.get("PLONE_PASSWORD")
        if username is None or password is None:
            raise ValueError("PLONE_USERNAME and PLONE_PASSWORD environment variables must be set")
        self.auth = (username, password)

        self.httpx_client = httpx.Client(
            timeout=15,
            auth=self.auth,
            headers={"Accept": "application/json", "X-UVNXS-Suppress-Cache-Invalidation": "1"},
            base_url=self.base_url,
        )

        super().__init__()

    def __del__(self) -> None:
        try:
            self.httpx_client.close()
        except Exception:
            pass

    # Private helper methods

    def __get_path_from_url(self, url: str) -> str:
        base_path = urlparse(self.base_url).path.rstrip("/")
        result_path = urlparse(url).path
        if result_path.lower().startswith(base_path.lower()):
            return result_path[len(base_path) :]
        return result_path

    def __get_path_from_plone_object(self, obj: dict) -> str:
        obj_id = obj.get("@id", "")
        return self.__get_path_from_url(obj_id)

    # General methods

    def get_url_from_path(self, path: str) -> str:
        return f"{self.base_url}/{path.strip('/')}"

    # Upload related methods

    def upload_file(self, file: BinaryIO, container: str, status: str | None = None) -> str:
        """Upload a binary file to Plone.

        Converts the stream content into base64 and posts a new 'File' content type.
        If ``status`` is provided, the uploaded object is given the same initial
        workflow status derived from the article's publication status.
        """
        try:
            return PloneUploadService(self.base_url, self.httpx_client).upload_file(file, container, status)
        except Exception:
            raise InternalError(f"Error uploading file to {container}")

    def save_jats_document(
        self, document: JATSDocument, container: str, options: SaveJATSDocumentOptions | None = None
    ) -> str:
        """Serialize and upload a JATSDocument object graph to Plone."""
        try:
            upload_service = PloneUploadService(self.base_url, self.httpx_client)
            result_url = upload_service.create_article(document.article, container, options)
            return self.__get_path_from_url(result_url)
        except Exception as e:
            logger.error(f"Error saving JATS document: {e}")
            raise

    # Download / export related methods

    def download_file(self, url: str) -> tuple[bytes, str]:
        """Download the binary content of a file/image object hosted in Plone.

        Refuses to download from URLs outside of the configured PLONE_BASE_URL,
        to avoid this adapter being used to fetch arbitrary external resources.
        """
        try:
            download_service = PloneDownloadService(self.base_url, self.httpx_client)
            return download_service.download_file(url)
        except InternalError:
            raise
        except ValueError:
            raise
        except Exception as e:
            raise InternalError(f"Error downloading file from {url}") from e

    @overload
    def get_jats_document(self, path: str, options: PloneGetJATSDocumentOptions) -> JATSDocument: ...

    @overload
    def get_jats_document(self, path: str, options: BaseGetJATSDocumentOptions | None = None) -> JATSDocument: ...

    def get_jats_document(self, path: str, options: BaseGetJATSDocumentOptions | None = None) -> JATSDocument:
        """Retrieve and reconstruct a JATSDocument from Plone content nodes."""
        url = self.get_url_from_path(path)
        plone_options = cast(PloneGetJATSDocumentOptions | None, options)
        download_service = PloneDownloadService(self.base_url, self.httpx_client)
        try:
            article = download_service.fetch_article(url, plone_options)
        except HTTPStatusError as e:
            if e.response.status_code == 404 and str(e.request.url) == url:
                raise PathNotFoundExpection(path) from e
            raise InternalError(f"Error fetching article at {url}") from e
        except ValueError:
            raise
        except Exception as e:
            raise InternalError(f"Error fetching article at {url}") from e

        try:
            relations, related_articles_translations = self.get_related_articles_with_metadata(path)
        except Exception as e:
            raise InternalError(f"Error fetching related articles for {path}") from e

        return JATSDocument(
            article=article, related_articles=relations, related_articles_translations=related_articles_translations
        )

    def get_metadata(self, path: str) -> Front:
        """Fetch the metadata of a JATS document from Plone."""
        url = self.get_url_from_path(path)
        return PloneDownloadService(self.base_url, self.httpx_client).get_metadata(url)

    def get_related_articles(self, path: str) -> tuple[list[str], list[str]]:
        return PloneDownloadService(self.base_url, self.httpx_client).get_related_articles(path)

    # Modify / automation related methods

    def link_related_articles(self) -> list[str]:
        """Link related articles in Plone (by using plone.relatedItems) based on metadata field 'related_articles'.

        This method links the listed articles from 'related_articles' (listed with the article-id) to the actual
        articles in Plone (using the @id = url) and saves them into relatedItems (attribute obtained from the
        plone.relateditems behavior). This is done for every article in the plone instance. All related articles that
        are found and linked will be deleted from the related_articles field afterwards. The method returns a list of
        all articles that have been updated.
        """
        articles = self.list_articles()[0]
        modify_service = PloneModifyService(self.base_url, self.httpx_client)
        updated_articles = []
        for article in articles:
            url = self.get_url_from_path(article)
            if modify_service.link_related_articles(url):
                updated_articles.append(article)
        return updated_articles

    # Listing / querying related methods

    def list_articles(
        self,
        fachbereiche: list[str] | None = None,
        sachgebiete: list[str] | None = None,
        organisationseinheiten: list[str] | None = None,
        rubriken: list[str] | None = None,
        batch_start: int = 0,
        batch_size: int | None = None,
    ) -> tuple[list[str], int]:
        items = PloneListingService(self.base_url, self.httpx_client).list_article_items(
            fachbereiche=fachbereiche,
            sachgebiete=sachgebiete,
            organisationseinheiten=organisationseinheiten,
            rubriken=rubriken,
            batch_start=batch_start,
            batch_size=batch_size,
        )
        paths = list(map(self.__get_path_from_plone_object, items[0]))
        return paths, items[1]

    def list_fachbereiche(self) -> list[str]:
        return PloneListingService(self.base_url, self.httpx_client).list_metadata_contents("fachbereich")

    def list_sachgebiete(self) -> list[str]:
        return PloneListingService(self.base_url, self.httpx_client).list_metadata_contents("sachgebiet")
