"""Interface definitions for JATS document storage adapters.

Defines the abstract base StorageAdapter class used to fetch, upload,
and store JATS documents and arbitrary files in a repository backend.
"""

import abc
import enum
from datetime import datetime
from typing import TypedDict

from jats_classes import Front, JATSClassInterface, JATSDocument

EDIT_PI = "<?section-edit-link {url}?>"


class GetJATSDocumentOptions(TypedDict):
    """Options for retrieving a JATSDocument from a storage adapter."""

    include_edit_links: bool | None


class SaveJATSDocumentOptions(TypedDict):
    """Options for saving a JATSDocument to a storage adapter."""

    use_html_sections: bool | None


class StorageAdapter(metaclass=abc.ABCMeta):
    """Abstract base class for all storage adapter implementations.

    Provides a contract for file upload and JATSDocument retrieving/saving.
    """

    # General methods

    @abc.abstractmethod
    def get_url_from_path(self, path: str) -> str:
        """Retrieve the URL for a JatsDocument from the storage system.

        Args:
            path: The path to the file in the storage system.

        Returns:
            The URL for the file.
        """
        raise NotImplementedError

    def get_path_from_url(self, url: str) -> str:
        """Retrieve the storage path from an absolute storage URL."""
        raise NotImplementedError

    # Upload related methods

    @abc.abstractmethod
    def upload_file(self, file: bytes, filename: str, container: str, status: str | None = None) -> str:
        """Upload a binary file into a target container.

        Args:
            file: The binary file stream/object to upload.
            filename: The name of the file being uploaded.
            container: The path to the container in the storage system.
            status: Optional publication status of the article that the file
                belongs to. Storage backends that support per-object workflow status
                may use this status to set the initial state of the uploaded object.

        Returns:
            The path of the uploaded file, relative to the container, starting with "/".
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_empty_article(
        self, front: Front, container: str, create_media_container: bool = False
    ) -> tuple[str, str | None]:
        """Create an empty Article with metadata from the provided Front object in the specified container.

        Args:
            front: The Front object containing metadata for the article.
            container: The path to the container in the storage system.
            create_media_container: Whether to create a media container inside the article.

        Returns:
            A tuple containing the path of the created article and the path of the media container (if created).
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_article_content(
        self, document: JATSDocument, container: str, options: SaveJATSDocumentOptions | None = None
    ) -> str:
        """Create the content of an article in the specified container.

        Args:
            document: The JATSDocument containing the article content.
            container: The path to the container in the storage system.
            options: Additional options for saving the article content.

        Returns:
            The path of the article.
        """
        raise NotImplementedError

    # Download / export related methods

    @abc.abstractmethod
    def download_file(self, url: str) -> tuple[bytes, str]:
        """Download the binary content of a file referenced by a URL (e.g. an image).

        Implementations must reject URLs that do not point into the storage
        backend they manage, to avoid being used to fetch arbitrary external
        resources.

        Args:
            url: The absolute URL of the file, as found e.g. in JATS content.

        Returns:
            A tuple of (file content bytes, content-type string).
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_media(self, path: str, filename: str, signature: str) -> tuple[bytes, str]:
        """Retrieve the binary content of a media file from the storage system.

        Args:
            path: The path to the JATS document containing the media file in the storage system.
            filename: The name of the media file.
            signature: A signature for accessing the media file.

        Returns:
            A tuple of (file content bytes, content-type string).
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_jats_document(self, path: str, options: GetJATSDocumentOptions | None = None) -> JATSDocument:
        """Retrieve a JATSDocument from the storage system.

        Args:
            path: The path to the document in the storage system.
            options: Additional options for retrieving the JATSDocument.

        Returns:
            A JATSDocument instance.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_jats_document_part(
        self, path: str, sub_path: str, options: GetJATSDocumentOptions | None = None
    ) -> tuple[JATSClassInterface, Front]:
        """Retrieve a part of a JATSDocument from the storage system.

        Args:
            path: The path to the document in the storage system.
            sub_path: The sub-path within the JATS document.
            options: Additional options for retrieving the JATS document part.

        Returns:
            A tuple containing:
                - A JATSClassInterface instance representing the requested part of the document.
                - The Front of the article associated with the requested part of the document.
        """
        raise NotImplementedError

    def get_metadata(self, path: str) -> Front:
        """Retrieve metadata for a JatsDocument from the storage system.

        Args:
            path: The path to the file in the storage system.

        Returns:
            A Front instance containing metadata for the file.
        """
        return self.get_jats_document(path).article.front

    @abc.abstractmethod
    def get_structure_tree(self, path: str, max_level: int | None = None) -> list[dict]:
        """Retrieve the structure tree for a JatsDocument from the storage system.

        Args:
            path: The path to the file in the storage system.
            max_level: The maximum depth of the structure tree to retrieve.

        Returns:
            A list of dictionaries representing the structure tree entries.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_related_articles(self, path: str) -> tuple[list[str], list[str]]:
        """Retrieve a list of related articles and translated articles for a JatsDocument from the storage system.

        Args:
            path: The path to the file in the storage system.

        Returns:
            A tuple containing two lists: the first list contains paths to related articles,
            and the second list contains paths to translated articles.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_path_from_webcode(self, webcode: str) -> str:
        """Retrieve a path to an article by its webcode from the storage system.
        Args:
            webcode: The webcode of the article.

        Returns:
            The path to the article corresponding to the given webcode.
        """
        raise NotImplementedError

    # Modify / automation related methods

    @abc.abstractmethod
    def link_related_articles(self) -> list[str]:
        """Link related articles and return the list of updated article paths."""
        raise NotImplementedError

    @abc.abstractmethod
    def delete_article(self, path: str) -> list[str]:
        """Delete an article from the storage system and return a list of any errors encountered."""
        raise NotImplementedError

    # Listing / querying related methods

    @abc.abstractmethod
    def list_articles(
        self,
        fachbereiche: list[str] | None = None,
        sachgebiete: list[str] | None = None,
        organisationseinheiten: list[str] | None = None,
        rubriken: list[str] | None = None,
        modified_since: datetime | None = None,
        get_webcodes: bool = False,
        batch_start: int = 0,
        batch_size: int | None = None,
    ) -> tuple[list[str], int]:
        """List a range of articles and return it together with the total match count.

        ``modified_since`` limits results to articles modified after the given timestamp.
        ``get_webcodes`` determines whether to list the webcodes for the articles instead of their paths.
        ``batch_start`` is the zero-based index of the first article. A
        ``None`` ``batch_size`` requests all remaining articles.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list_fachbereiche(self) -> list[str]:
        """List all available Fachbereiche."""
        raise NotImplementedError

    @abc.abstractmethod
    def list_fachbereiche_tree(self) -> dict[str, list[str]]:
        """List all available Fachbereiche along with their associated Sachgebiete in a tree structure."""
        raise NotImplementedError

    @abc.abstractmethod
    def list_sachgebiete(self, fachbereich: str | None = None) -> list[str]:
        """List all available Sachgebiete, optionally filtered by Fachbereich."""
        raise NotImplementedError


class AvailableStorageAdapters(enum.StrEnum):
    """Enumeration of available storage adapter implementations."""

    PLONE = "plone"

    def create_instance(self) -> StorageAdapter:
        """Factory method to create an instance of the storage adapter."""
        match self:
            case AvailableStorageAdapters.PLONE:
                from . import PloneStorageAdapter

                return PloneStorageAdapter()
            case _:
                raise ValueError(f"Storage adapter '{self.value}' is not supported.")

    @classmethod
    def create_instance_by_name(cls, name: str) -> StorageAdapter:
        """Create a storage adapter instance based on the adapter name.
        Throws ValueError if the adapter name is not supported.
        """
        try:
            adapter_enum = cls(name)
        except ValueError:
            raise ValueError(f"Storage adapter '{name}' is not supported.")
        return adapter_enum.create_instance()
