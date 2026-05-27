import abc
from typing import BinaryIO

from jats_classes import JATSDocument


class StorageAdapter(metaclass=abc.ABCMeta):
    # Returns the URL of the uploaded file
    @abc.abstractmethod
    def upload_file(self, file: BinaryIO) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def get_jats_document(self, doi: str) -> JATSDocument:
        raise NotImplementedError

    #  Returns the URL of the saved file
    @abc.abstractmethod
    def save_jats_document(self, document: JATSDocument) -> str:
        raise NotImplementedError
