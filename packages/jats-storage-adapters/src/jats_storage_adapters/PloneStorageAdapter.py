"""Plone Storage Adapter implementation.

Connects to a live Plone CMS REST API to manage JATS documents and files.
"""

import base64
import mimetypes
import os
from typing import BinaryIO

import httpx
from jats_classes import (
    Appendix,
    AppendixGroup,
    Article,
    Back,
    Body,
    Front,
    GenericSection,
    JATSDocument,
    Section,
)

from .interface import StorageAdapter


class PloneStorageAdapter(StorageAdapter):
    """Storage adapter interacting with a Plone instance over the REST API.

    Requires the following environment variables:
    - PLONE_BASE_URL: Root URL of Plone CMS (e.g. http://localhost:8080/Plone).
    - PLONE_USERNAME: Authenticated username for API operations.
    - PLONE_PASSWORD: Password corresponding to user credentials.
    """

    base_url: str
    auth: tuple[str, str]

    def __init__(self):
        """Initialize storage adapter loading credentials from environment."""
        base_url = os.environ.get("PLONE_BASE_URL")
        if base_url is None:
            raise ValueError("PLONE_BASE_URL environment variable is not set")
        self.base_url = base_url.rstrip("/")

        username = os.environ.get("PLONE_USERNAME")
        password = os.environ.get("PLONE_PASSWORD")
        if username is None or password is None:
            raise ValueError(
                "PLONE_USERNAME and PLONE_PASSWORD environment variables must be set"
            )
        self.auth = (username, password)

        super().__init__()

    def upload_file(self, file: BinaryIO, container: str) -> str:
        """Upload a binary file to Plone.

        Converts the stream content into base64 and posts a new 'File' content type.
        """
        filename = os.path.basename(getattr(file, "name", "") or "upload")

        content_type, _ = mimetypes.guess_type(filename)
        if content_type is None:
            content_type = "application/octet-stream"

        encoded = base64.b64encode(file.read()).decode("ascii")

        url = self.__get_container_url(container)

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
        """Retrieve and reconstruct a JATSDocument from Plone content nodes."""
        url = f"{self.base_url}/{path.strip('/')}"
        article = self.__fetch_article(url)
        return JATSDocument(article=article)

    def __get_json(self, url: str) -> dict:
        """Fetch JSON data from a Plone API endpoint."""
        response = httpx.get(
            url,
            params={"fullobjects": 1},
            auth=self.auth,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()

    def __fetch_front(self, data: dict) -> Front:
        """Convert Plone front node data into a Front domain model."""
        return Front(content_raw=data.get("content_raw"))

    def __fetch_section(self, url: str) -> Section:
        """Fetch and reconstruct a Section and subsections from Plone REST endpoints."""
        data = self.__get_json(url)
        sections = [
            self.__fetch_section(item["@id"])
            for item in data.get("items", [])
            if item.get("@type") == "Section"
        ]
        return Section(
            sec_type=data.get("sec_type"),
            label=data.get("label"),
            title=data.get("title"),
            label_title_raw=data.get("label_title_raw") or "",
            content_raw=data.get("content_raw"),
            sections=sections,
        )

    def __fetch_appendix(self, url: str) -> Appendix:
        """Fetch and reconstruct an Appendix and subsections from Plone."""
        data = self.__get_json(url)
        sections = [
            self.__fetch_section(item["@id"])
            for item in data.get("items", [])
            if item.get("@type") == "Section"
        ]
        return Appendix(
            sec_type=data.get("sec_type"),
            label=data.get("label"),
            title=data.get("title"),
            label_title_raw=data.get("label_title_raw") or "",
            content_raw=data.get("content_raw"),
            sections=sections,
        )

    def __fetch_appendix_group(self, url: str) -> AppendixGroup:
        """Fetch and reconstruct an AppendixGroup from Plone REST endpoints."""
        data = self.__get_json(url)
        appendixes = [
            self.__fetch_appendix(item["@id"])
            for item in data.get("items", [])
            if item.get("@type") == "Appendix"
        ]
        return AppendixGroup(
            sec_type=data.get("sec_type"),
            label=data.get("label"),
            title=data.get("title"),
            label_title_raw=data.get("label_title_raw") or "",
            content_raw=data.get("content_raw"),
            appendixes=appendixes,
        )

    def __fetch_body(self, url: str) -> Body:
        """Fetch and reconstruct the Body node and its sections from Plone."""
        data = self.__get_json(url)
        sections = [
            self.__fetch_section(item["@id"])
            for item in data.get("items", [])
            if item.get("@type") == "Section"
        ]
        return Body(sections=sections)

    def __fetch_back(self, url: str) -> Back:
        """Fetch and reconstruct the Back node and its appendix groups from Plone."""
        data = self.__get_json(url)
        appendix_groups = [
            self.__fetch_appendix_group(item["@id"])
            for item in data.get("items", [])
            if item.get("@type") == "AppendixGroup"
        ]
        return Back(appendix_groups=appendix_groups)

    def __fetch_article(self, url: str) -> Article:
        """Fetch and build an Article node with Front, Body, and Back from Plone."""
        data = self.__get_json(url)
        front = body = back = None
        for item in data.get("items", []):
            pt = item.get("@type")
            item_url = item.get("@id")
            if pt == "Front":
                front = self.__fetch_front(item)
            elif pt == "Body":
                body = self.__fetch_body(item_url)
            elif pt == "Back":
                back = self.__fetch_back(item_url)
        if not all([front, body, back]):
            raise ValueError("Article must contain Front, Body, and Back")
        assert front is not None and body is not None and back is not None
        return Article(front=front, body=body, back=back)

    def save_jats_document(self, document: JATSDocument, container: str) -> str:
        """Serialize and upload a JATSDocument object graph to Plone."""
        self.__create_container(container)
        result_url = self.__create_article(document.article, container)
        return result_url

    def __get_container_url(self, container: str) -> str:
        """Build the complete Plone API URL for a container folder."""
        return f"{self.base_url}/{container.strip('/')}"

    def __create_front(self, front: Front, container_url: str) -> str:
        """Create a Front object inside a Plone Article container."""
        response = httpx.post(
            container_url,
            json={
                "@type": "Front",
                "title": "Front",
                "content_raw": front.content_raw,
            },
            auth=self.auth,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json().get("@id")

    def __create_section(self, section: GenericSection, container_url: str) -> str:
        """Recursively create a Section/Appendix node structure in a Plone container."""
        portal_type: str
        if isinstance(section, Section):
            portal_type = "Section"
        else:
            portal_type = "Appendix"
        response = httpx.post(
            container_url,
            json={
                "@type": portal_type,
                "title": section.title or portal_type,
                "sec_type": section.sec_type,
                "label": section.label,
                "label_title_raw": section.label_title_raw,
                "content_raw": section.content_raw,
            },
            auth=self.auth,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        response_url: str = response.json().get("@id")
        for sub_section in section.sections:
            self.__create_section(sub_section, response_url)
        return response_url

    def __create_body(self, body: Body, container_url: str) -> str:
        """Create a Body node inside a Plone Article and upload its sections."""
        response = httpx.post(
            container_url,
            json={
                "@type": "Body",
                "title": "Body",
            },
            auth=self.auth,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        response_url: str = response.json().get("@id")
        for section in body.sections:
            self.__create_section(section, response_url)
        return response_url

    def __create_appendix_group(
        self, app_group: AppendixGroup, container_url: str
    ) -> str:
        """Create an AppendixGroup node inside Plone Back and upload sections."""
        response = httpx.post(
            container_url,
            json={
                "@type": "AppendixGroup",
                "title": app_group.title or "AppendixGroup",
                "label": app_group.label,
                "label_title_raw": app_group.label_title_raw,
                "content_raw": app_group.content_raw,
            },
            auth=self.auth,
        )
        response.raise_for_status()
        response_url: str = response.json().get("@id")
        for app in app_group.appendixes:
            self.__create_section(app, response_url)
        return response_url

    def __create_back(self, back: Back, container_url: str) -> str:
        """Create a Back node inside a Plone Article and upload its appendix groups."""
        response = httpx.post(
            container_url,
            json={
                "@type": "Back",
                "title": "Back",
            },
            auth=self.auth,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        response_url: str = response.json().get("@id")
        for app in back.appendix_groups:
            self.__create_appendix_group(app, response_url)
        return response_url

    def __create_article(self, article: Article, container: str) -> str:
        """Create an Article root node and Front, Body, Back children in Plone."""
        url = f"{self.base_url}/{container.strip('/')}"
        response = httpx.post(
            url,
            json={
                "@type": "Article",
                "title": "Placeholder",
            },
            auth=self.auth,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        result_url: str = response.json().get("@id")
        self.__create_front(article.front, result_url)
        self.__create_body(article.body, result_url)
        self.__create_back(article.back, result_url)
        return result_url

    def __get_container_path(self, path: str) -> str:
        """Split a URL path to obtain the parent container's path."""
        return "/".join(path.split("/")[:-1])

    def __create_container_for_file(self, path: str) -> None:
        """Ensure parent folders exist for a given file path in Plone."""
        self.__create_container(self.__get_container_path(path))

    def __create_container(self, container: str) -> None:
        """Recursively create folder structures ('Folder' type) in Plone if missing."""
        print(f"Creating container: {container}")
        parts = [p for p in container.strip("/").split("/") if p]
        current_path = ""

        for part in parts:
            current_path = f"{current_path}/{part}" if current_path else part
            url = f"{self.base_url}/{current_path}"

            response = httpx.get(
                url, auth=self.auth, headers={"Accept": "application/json"}
            )
            if response.status_code == 200:
                continue

            parent_url = (
                f"{self.base_url}/{current_path.rsplit('/', 1)[0]}"
                if "/" in current_path
                else self.base_url
            )
            response = httpx.post(
                parent_url,
                json={"@type": "Folder", "title": part, "id": part},
                auth=self.auth,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
