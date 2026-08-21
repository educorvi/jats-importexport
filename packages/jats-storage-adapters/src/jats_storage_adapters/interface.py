"""Interface definitions for JATS document storage adapters.

Defines the abstract base StorageAdapter class used to fetch, upload,
and store JATS documents and arbitrary files in a repository backend.
"""

import abc
import enum
from typing import BinaryIO, TypedDict

from jats_classes import JATSDocument

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

    @abc.abstractmethod
    def upload_file(self, file: BinaryIO, container: str) -> str:
        """Upload a binary file into a target container.

        Args:
            file: The binary file stream/object to upload.
            container: The path to the container in the storage system.

        Returns:
            The URL of the uploaded file.
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
    def save_jats_document(
        self, document: JATSDocument, container: str, options: SaveJATSDocumentOptions | None = None
    ) -> str:
        """Save a JATSDocument structure into a target container.

        Args:
            document: The JATSDocument to save.
            container: The path to the target container in the storage system.
            options: Additional options for saving the JATSDocument.

        Returns:
            The path of the saved file or main container object.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list_articles(
        self,
        fachbereiche: list[str] | None = None,
        sachgebiete: list[str] | None = None,
        organisationseinheiten: list[str] | None = None,
        rubriken: list[str] | None = None,
    ) -> list[str]:
        """List all articles in the storage system."""
        raise NotImplementedError


class AvailableStorageAdapters(enum.StrEnum):
    """Enumeration of available storage adapter implementations."""

    PLONE = "plone"

    def create_instance(self) -> StorageAdapter:
        """Factory method to create an instance of the storage adapter."""
        match self:
            case AvailableStorageAdapters.PLONE:
                from .PloneStorageAdapter import PloneStorageAdapter

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
