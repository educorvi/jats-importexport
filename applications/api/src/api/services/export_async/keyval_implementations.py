import abc
import logging
from enum import Enum

from api.config import StorageConfig


class ExportTypes(Enum):
    HTML = "html"
    MD = "md"
    JATS = "jats"
    PDF = "pdf"


class KeyValImplementation(abc.ABC):
    db_id: str

    @property
    @abc.abstractmethod
    def implementation_name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def __init__(self, db_id: str):
        self.db_id = db_id

    def __clean_path(self, path: str):
        return path.strip("/")

    def has(self, path: str, export_type: ExportTypes) -> bool:
        return self._has(self.__clean_path(path), export_type)

    @abc.abstractmethod
    def _has(self, path: str, export_type: ExportTypes) -> bool:
        raise NotImplementedError

    def get(self, path: str, export_type: ExportTypes) -> str:
        return self._get(self.__clean_path(path), export_type)

    @abc.abstractmethod
    def _get(self, path: str, export_type: ExportTypes) -> str:
        raise NotImplementedError

    def set(self, path: str, export_type: ExportTypes, value: str) -> None:
        self._set(self.__clean_path(path), export_type, value)

    @abc.abstractmethod
    def _set(self, path: str, export_type: ExportTypes, value: str) -> None:
        raise NotImplementedError

    def delete(self, path: str, export_type: ExportTypes | None) -> None:
        self._delete(self.__clean_path(path), export_type)

    @abc.abstractmethod
    def _delete(self, path: str, export_type: ExportTypes | None) -> None:
        raise NotImplementedError


logger = logging.getLogger(__name__)


class InMemoryKeyValImplementation(KeyValImplementation):
    @property
    def implementation_name(self) -> str:
        return "InMemory"

    _data: dict[tuple[str, ExportTypes], str]

    def __init__(self, db_id: str):
        super().__init__(db_id)
        self._data = {}

    def _has(self, path: str, export_type: ExportTypes) -> bool:
        return (path, export_type) in self._data

    def _get(self, path: str, export_type: ExportTypes):
        return self._data.get((path, export_type))

    def _set(self, path: str, export_type: ExportTypes, value: str):
        self._data[(path, export_type)] = value

    def _delete(self, path: str, export_type: ExportTypes | None):
        if export_type is None:
            keys_to_delete = [key for key in self._data if key[0] == path]
            for key in keys_to_delete:
                del self._data[key]
        else:
            if (path, export_type) in self._data:
                del self._data[(path, export_type)]
        logger.info(f"Deleted key-value pair for path: {path}, export type: {export_type}")
        print(self._data)


def __create_cache(db_id: str) -> KeyValImplementation:
    return InMemoryKeyValImplementation(db_id)


ASYNC_EXPORT_CACHE = __create_cache(StorageConfig.VALKEY_DB_ASYNC_EXPORT)
