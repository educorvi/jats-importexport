import base64
import mimetypes
import os
from typing import BinaryIO

import httpx
from jats_classes import JATSDocument

from .interface import StorageAdapter


class PloneStorageAdapter(StorageAdapter):
    base_url: str
    auth: tuple[str, str]

    def __init__(self):
        base_url = os.environ.get("PLONE_BASE_URL")
        if base_url is None:
            raise ValueError("PLONE_BASE_URL environment variable is not set")
        self.base_url = base_url.rstrip("/")

        username = os.environ.get("PLONE_USERNAME")
        password = os.environ.get("PLONE_PASSWORD")
        if username is None or password is None:
            raise ValueError("PLONE_USERNAME and PLONE_PASSWORD environment variables must be set")
        self.auth = (username, password)

        super()

    def upload_file(self, file: BinaryIO, container: str | None) -> str:
        filename = os.path.basename(getattr(file, "name", "") or "upload")

        content_type, _ = mimetypes.guess_type(filename)
        if content_type is None:
            content_type = "application/octet-stream"

        encoded = base64.b64encode(file.read()).decode("ascii")

        url = f"{self.base_url}/{container.strip('/')}" if container else self.base_url

        response = httpx.post(
            url,
            json={
                "@type": "File",
                "title": filename,
                "file": {
                    "data": encoded,
                    "encoding": "base64",
                    "filename": filename,
                    "content-type": content_type,
                },
            },
            auth=self.auth,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()

        return response.json().get("@id", url)

    def get_jats_document(self, path: str) -> JATSDocument:
        pass

    def save_jats_document(self, document: JATSDocument, container: str | None) -> str:
        pass