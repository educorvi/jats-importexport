import abc
import base64
import json
import logging
from enum import Enum
from typing import TypedDict

from jats_classes import Front
from prometheus_client import Counter
from pydantic import BaseModel, TypeAdapter
from valkey.asyncio import Valkey

from api.config import StorageConfig

EXPORT_CACHE_REQUESTS = Counter(
    "vur_hub_export_cache_requests_total",
    "Completed export cache requests by endpoint and cache result.",
    ["type", "result", "cache_id"],
)


_FRONT_ADAPTER = TypeAdapter(Front)


class ExportState(Enum):
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class ExportTypes(Enum):
    HTML = "html"
    HTML_EDIT_LINKS = "html_edit_links"
    MD = "md"
    MD_EDIT_LINKS = "md_edit_links"
    JATS = "jats"
    PDF = "pdf"
    METADATA = "metadata"


class HtmlData(TypedDict):
    html: str
    front: str


class CacheStatus(BaseModel):
    implementation: str
    items_in_cache: int


class CacheImplementation(abc.ABC):
    cache_id: int
    cache_name: str

    @property
    @abc.abstractmethod
    def implementation_name(self) -> str:
        raise NotImplementedError

    def __init__(self, cache_id: int, cache_name: str):
        self.cache_id = cache_id
        self.cache_name = cache_name

    @staticmethod
    def __clean_path(path: str):
        return path.strip("/")

    async def get(self, path: str, export_type: ExportTypes) -> str | None:
        data = await self._get(self.__clean_path(path), export_type)
        result = "hit" if data is not None else "miss"
        EXPORT_CACHE_REQUESTS.labels(type=export_type.value, result=result, cache_id=self.cache_id).inc()
        return data

    @abc.abstractmethod
    async def _get(self, path: str, export_type: ExportTypes) -> str | None:
        raise NotImplementedError

    async def set(self, path: str, export_type: ExportTypes, value: str) -> None:
        await self._set(self.__clean_path(path), export_type, value)

    @abc.abstractmethod
    async def _set(self, path: str, export_type: ExportTypes, value: str) -> None:
        raise NotImplementedError

    async def delete(self, path: str, export_type: ExportTypes | None) -> None:
        await self._delete(self.__clean_path(path), export_type)

    @abc.abstractmethod
    async def _delete(self, path: str, export_type: ExportTypes | None) -> None:
        raise NotImplementedError

    async def delete_all(self) -> None:
        await self._delete_all()

    @abc.abstractmethod
    async def _delete_all(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_cache_status(self) -> CacheStatus:
        raise NotImplementedError

    async def init(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def get_html(self, path: str, edit_links: bool) -> HtmlData | None:
        export_type = ExportTypes.HTML_EDIT_LINKS if edit_links else ExportTypes.HTML
        cache_string = await self._get(self.__clean_path(path), export_type)
        if cache_string:
            return json.loads(cache_string)
        return None

    async def set_html(self, path: str, edit_links: bool, html: str, front: str) -> None:
        export_type = ExportTypes.HTML_EDIT_LINKS if edit_links else ExportTypes.HTML
        await self._set(self.__clean_path(path), export_type, json.dumps({"html": html, "front": front}))

    async def set_metadata(self, path: str, metadata: Front) -> None:
        value = _FRONT_ADAPTER.dump_json(metadata).decode("utf-8")
        await self.set(path, ExportTypes.METADATA, value)

    async def set_pdf(self, path: str, content: bytes, filename: str) -> None:
        value = json.dumps({"content": base64.b64encode(content).decode("ascii"), "filename": filename})
        await self.set(path, ExportTypes.PDF, value)

    async def get_pdf(self, path: str) -> tuple[bytes, str] | None:
        value = await self.get(path, ExportTypes.PDF)
        if value is None:
            return None
        data = json.loads(value)
        return base64.b64decode(data["content"]), data["filename"]

    async def get_metadata(self, path: str) -> Front | None:
        value = await self.get(path, ExportTypes.METADATA)
        if value is None:
            return None
        return _FRONT_ADAPTER.validate_json(value)


logger = logging.getLogger(__name__)


class InMemoryCache(CacheImplementation):
    @property
    def implementation_name(self) -> str:
        return "InMemory"

    _data: dict[tuple[str, ExportTypes], str]

    async def init(self) -> None:
        self._data = {}

    async def _get(self, path: str, export_type: ExportTypes) -> str | None:
        return self._data.get((path, export_type))

    async def _set(self, path: str, export_type: ExportTypes, value: str):
        self._data[(path, export_type)] = value

    async def _delete(self, path: str, export_type: ExportTypes | None):
        if export_type is None:
            keys_to_delete = [key for key in self._data if key[0] == path]
            for key in keys_to_delete:
                del self._data[key]
        else:
            if (path, export_type) in self._data:
                del self._data[(path, export_type)]

    async def _delete_all(self) -> None:
        self._data.clear()

    async def get_cache_status(self) -> CacheStatus:
        return CacheStatus(implementation=self.implementation_name, items_in_cache=len(self._data))


class ValKeyCache(CacheImplementation):
    client: Valkey

    async def init(self) -> None:
        self.client = Valkey(host=StorageConfig.VALKEY_HOST, db=self.cache_id, decode_responses=True)
        await self.client.ping()

    async def close(self) -> None:
        await self.client.close()

    @staticmethod
    def __build_key(path: str, export_type: ExportTypes) -> str:
        return f"{path}:{export_type}"

    def __check_client(self):
        if not self.client:
            raise SystemError("Valkey client is not initialized")

    async def _get(self, path: str, export_type: ExportTypes) -> str | None:
        self.__check_client()
        key = self.__build_key(path, export_type)
        return await self.client.get(key)

    async def _set(self, path: str, export_type: ExportTypes, value: str) -> None:
        self.__check_client()
        key = self.__build_key(path, export_type)
        await self.client.set(key, value)

    async def _delete(self, path: str, export_type: ExportTypes | None) -> None:
        self.__check_client()
        if export_type is None:
            for export_type in ExportTypes:
                await self.client.delete(self.__build_key(path, export_type))
        else:
            key = self.__build_key(path, export_type)
            await self.client.delete(key)

    async def _delete_all(self) -> None:
        self.__check_client()
        await self.client.flushdb(True)

    async def get_cache_status(self) -> CacheStatus:
        self.__check_client()
        return CacheStatus(
            implementation=self.implementation_name,
            items_in_cache=await self.client.dbsize(),
        )

    @property
    def implementation_name(self) -> str:
        return "ValKey"


def __create_cache(cache_id: int, cache_name: str) -> CacheImplementation:
    match StorageConfig.CACHE_IMPLEMENTATION:
        case "valkey":
            logger.info(f"Using ValKey cache implementation for cache {cache_id}")
            return ValKeyCache(cache_id, cache_name)
        case "inmemory":
            logger.info(f"Using InMemory cache implementation for cache {cache_id}")
            return InMemoryCache(cache_id, cache_name)
        case _:
            raise ValueError("Invalid cache implementation. Supported options: inmemory, valkey")


async def init_caches():
    for cache in ALL_CACHES:
        try:
            await cache.init()
        except Exception as e:  # noqa: E722
            logger.fatal("Cache client init failed:")
            logger.exception(e)
            exit(1)


async def close_caches():
    for cache in ALL_CACHES:
        try:
            await cache.close()
        except Exception as e:  # noqa: E722
            logger.warning("Cache client close failed:")
            logger.exception(e)


EXPORT_CACHE = __create_cache(StorageConfig.VALKEY_DB_EXPORT, "EXPORT_CACHE")
EXPORT_STATE_CACHE = __create_cache(StorageConfig.VALKEY_DB_EXPORT_STATE, "EXPORT_STATE_CACHE")
ALL_CACHES = [EXPORT_CACHE, EXPORT_STATE_CACHE]
