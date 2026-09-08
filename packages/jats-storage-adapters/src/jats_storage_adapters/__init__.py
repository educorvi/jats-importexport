"""Storage Adapters package for interacting with document repositories.

Exposes storage adapters such as PloneStorageAdapter for uploading files
and loading/saving JATS documents from a storage backend.
"""

from .plone_storage_adapter import PloneStorageAdapter

__all__ = ["PloneStorageAdapter"]
