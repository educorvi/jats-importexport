from fastapi import HTTPException
from jats_storage_adapters.interface import StorageAdapter, AvailableStorageAdapters

from api.config import StorageConfig

STORAGE_ADAPTER = StorageConfig.STORAGE_ADAPTER


def get_adapter_instance() -> StorageAdapter:
    try:
        return AvailableStorageAdapters.create_instance_by_name(STORAGE_ADAPTER)
    except ValueError:
        raise HTTPException(status_code=500, detail="Could not connect to the storage adapter.")
