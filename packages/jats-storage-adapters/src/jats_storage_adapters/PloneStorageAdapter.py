import base64
import mimetypes
import os
from typing import BinaryIO

import httpx
from jats_classes import (
    Appendix,
    Article,
    Body,
    Front,
    JATSDocument,
    Section, Back, AppendixGroup, GenericSection,
)

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
            raise ValueError(
                "PLONE_USERNAME and PLONE_PASSWORD environment variables must be set"
            )
        self.auth = (username, password)

        super()

    def upload_file(self, file: BinaryIO, container: str) -> str:
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
        pass

    def save_jats_document(self, document: JATSDocument, container: str) -> str:
        # get path without document name
        self.__create_container(container)
        result_url = self.__create_article(document.article, container)


        return result_url

    def __get_container_url(self, container: str) -> str:
        return f"{self.base_url}/{container.strip('/')}"

    def __create_front(self, front: Front, container_url: str) -> str:
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

    def __create_appendix_group(self, app_group: AppendixGroup, container_url: str):
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
        return "/".join(path.split("/")[:-1])

    def __create_container_for_file(self, path: str):
        self.__create_container(self.__get_container_path(path))

    def __create_container(self, container: str) -> None:
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
