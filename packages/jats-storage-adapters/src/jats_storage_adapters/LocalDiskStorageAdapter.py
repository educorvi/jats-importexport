import hashlib
import os
from pathlib import Path
from typing import BinaryIO

from jats_classes import JATSDocument
from jats_exporters.jats import JatsExporter

from .interface import StorageAdapter


class LocalDiskStorageAdapter(StorageAdapter):
    """Storage adapter interacting with local disk.

    Requires the following environment variables:
    - LOCAL_STORAGE_DIR: Root folder for storing files (default: ./.data).
    """

    def __init__(self):
        """Initialize storage adapter."""
        base_dir = os.environ.get("LOCAL_STORAGE_DIR", "./.data")
        self.base_dir = Path(base_dir).resolve()
        super().__init__()

    def upload_file(self, file: BinaryIO, container: str) -> str:
        """Upload a binary file to local disk, with deduplication by hash."""
        container_path = self.base_dir / container.strip("/")
        container_path.mkdir(parents=True, exist_ok=True)

        content = file.read()
        file_hash = hashlib.sha256(content).hexdigest()

        original_name = getattr(file, "name", "")
        if original_name:
            ext = "".join(Path(original_name).suffixes)
        else:
            ext = ""
            
        filename = f"{file_hash}{ext}"
        file_path = container_path / filename

        if not file_path.exists():
            with open(file_path, "wb") as f:
                f.write(content)

        return f"{container.strip('/')}/{filename}"

    def get_jats_document(self, path: str) -> JATSDocument:
        """Retrieve a JATSDocument from local disk."""
        file_path = self.base_dir / path.strip("/")
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        return JATSDocument.from_xml(content, xsd_path=None)

    def save_jats_document(self, document: JATSDocument, container: str) -> str:
        """Serialize and upload a JATSDocument to local disk."""
        container_path = self.base_dir / container.strip("/")
        container_path.mkdir(parents=True, exist_ok=True)
        
        xml_content = JatsExporter().export(document)
        content_bytes = xml_content.encode("utf-8")
        file_hash = hashlib.sha256(content_bytes).hexdigest()
        filename = f"{file_hash}.xml"
        file_path = container_path / filename

        if not file_path.exists():
            with open(file_path, "wb") as f:
                f.write(content_bytes)

        return f"{container.strip('/')}/{filename}"
