"""Interface definitions for JATS document storage adapters.

Defines the abstract base StorageAdapter class used to fetch, upload,
and store JATS documents and arbitrary files in a repository backend.
"""

import abc
from typing import BinaryIO

from jats_classes import JATSDocument


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
    def get_jats_document(self, path: str) -> JATSDocument:
        """Retrieve a JATSDocument from the storage system.

        Args:
            path: The path to the document in the storage system.

        Returns:
            A JATSDocument instance.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def save_jats_document(self, document: JATSDocument, container: str) -> str:
        """Save a JATSDocument structure into a target container.

        Args:
            document: The JATSDocument to save.
            container: The path to the target container in the storage system.

        Returns:
            The URL of the saved file or main container object.
        """
        raise NotImplementedError

