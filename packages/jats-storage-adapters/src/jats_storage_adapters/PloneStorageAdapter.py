"""Plone Storage Adapter implementation.

Connects to a live Plone CMS REST API to manage JATS documents and files.
"""

import base64
import json
import logging
import mimetypes
import os
from logging import debug
from typing import BinaryIO, cast
from urllib.parse import urlparse

import httpx
from httpx import HTTPStatusError
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
from jats_exporters import HtmlExporter
from lxml import etree, html
from lxml.html import HtmlElement

from .errors import InternalError, PathNotFoundExpection
from .interface import EDIT_PI, GetJATSDocumentOptions, SaveJATSDocumentOptions, StorageAdapter

logger = logging.getLogger(__name__)


XSL_PATH = os.path.join(os.path.dirname(__file__), "xslt", "html_to_jats.xslt")

EDIT_PI_PLONE = EDIT_PI.format(url="{url}/edit")


class PloneStorageAdapter(StorageAdapter):
    """Storage adapter interacting with a Plone instance over the REST API.

    Requires the following environment variables:
    - PLONE_BASE_URL: Root URL of Plone CMS (e.g. http://localhost:8080/Plone).
    - PLONE_USERNAME: Authenticated username for API operations.
    - PLONE_PASSWORD: Password corresponding to user credentials.
    """

    base_url: str
    auth: tuple[str, str]
    httpx_client: httpx.Client

    def __init__(self):
        """Initialize storage adapter loading credentials from environment."""
        base_url = os.environ.get("PLONE_BASE_URL")
        if base_url is None:
            raise ValueError("PLONE_BASE_URL environment variable is not set")
        self.base_url = base_url.rstrip("/")

        username = os.environ.get("PLONE_USERNAME")
        password = os.environ.get("PLONE_PASSWORD")
        if username is None or password is None:
            raise ValueError("PLONE_USERNAME and PLONE_PASSWORD environment variables must be set")
        self.auth = (username, password)

        self.httpx_client = httpx.Client(timeout=15, auth=self.auth, headers={"Accept": "application/json"})

        xsl_path = os.path.abspath(XSL_PATH)
        self.xsl_doc = etree.parse(xsl_path)
        self.transform = etree.XSLT(self.xsl_doc)

        super().__init__()

    def __del__(self) -> None:
        try:
            self.httpx_client.close()
        except Exception:
            pass

    def __get_path_from_url(self, url: str) -> str:
        base_path = urlparse(self.base_url).path.rstrip("/")
        result_path = urlparse(url).path
        if result_path.lower().startswith(base_path.lower()):
            return result_path[len(base_path) :]
        return result_path

    def __plone_object_to_path(self, obj: dict) -> str:
        obj_id = obj.get("@id", "")
        return self.__get_path_from_url(obj_id)

    def list_articles(
        self,
        fachbereiche: list[str] | None = None,
        sachgebiete: list[str] | None = None,
        organisationseinheiten: list[str] | None = None,
        rubriken: list[str] | None = None,
        batch_start: int = 0,
        batch_size: int | None = None,
    ) -> tuple[list[str], int]:
        url = f"{self.base_url}/@querystring-search"
        query = [{"i": "portal_type", "o": "plone.app.querystring.operation.selection.any", "v": ["Article"]}]
        if fachbereiche:
            query.append({"i": "fachbereich", "o": "plone.app.querystring.operation.selection.any", "v": fachbereiche})
        if sachgebiete:
            query.append({"i": "sachgebiet", "o": "plone.app.querystring.operation.selection.any", "v": sachgebiete})
        if organisationseinheiten:
            query.append(
                {
                    "i": "organisationseinheit",
                    "o": "plone.app.querystring.operation.selection.any",
                    "v": organisationseinheiten,
                }
            )
        if rubriken:
            query.append({"i": "journal_title", "o": "plone.app.querystring.operation.selection.any", "v": rubriken})
        search: dict = {"query": query, "b_start": batch_start}
        if batch_size is not None:
            search["b_size"] = batch_size
        response = self.httpx_client.post(url, json=search)
        response.raise_for_status()
        json_res = response.json()
        paths = list(map(self.__plone_object_to_path, json_res.get("items", [])))
        while batch_size is None and json_res.get("batching", {}).get("next"):
            next_url = json_res["batching"]["next"]
            response = self.httpx_client.post(next_url, json=search)
            response.raise_for_status()
            json_res = response.json()
            paths.extend(map(self.__plone_object_to_path, json_res.get("items", [])))
        return paths, json_res.get("items_total", len(paths))

    def __upload_file(self, file: BinaryIO, container: str) -> str:
        self.__create_container(container)

        filename = os.path.basename(getattr(file, "name", "") or "upload")

        content_type, _ = mimetypes.guess_type(filename)
        if content_type is None:
            content_type = "application/octet-stream"

        encoded = base64.b64encode(file.read()).decode("ascii")

        url = self.__get_container_url(container)

        is_image = content_type.startswith("image/")
        portal_type = "Image" if is_image else "File"
        field_name = "image" if is_image else "file"

        response = self.httpx_client.post(
            url,
            json={
                "@type": portal_type,
                "title": filename,
                field_name: {
                    "data": encoded,
                    "encoding": "base64",
                    "filename": filename,
                    "content-type": content_type,
                },
            },
        )
        response.raise_for_status()

        return response.json().get("@id", url)

    def upload_file(self, file: BinaryIO, container: str) -> str:
        """Upload a binary file to Plone.

        Converts the stream content into base64 and posts a new 'File' content type.
        """
        try:
            return self.__upload_file(file, container)
        except Exception as e:
            raise InternalError(f"Error uploading file to {container}") from e

    def get_jats_document(self, path: str, options: GetJATSDocumentOptions | None = None) -> JATSDocument:
        """Retrieve and reconstruct a JATSDocument from Plone content nodes."""
        url = f"{self.base_url}/{path.strip('/')}"
        try:
            article = self.__fetch_article(url, options)
        except HTTPStatusError as e:
            raise PathNotFoundExpection(path) from e
        except ValueError:
            raise
        except Exception as e:
            raise InternalError(f"Error fetching article at {url}") from e
        return JATSDocument(article=article)

    def __get_json(self, url: str) -> dict:
        """Fetch JSON data from a Plone API endpoint."""
        response = self.httpx_client.get(url, params={"fullobjects": 1})
        response.raise_for_status()
        return response.json()

    def __get_label_title_raw(self, data: dict, url: str, options: GetJATSDocumentOptions | None = None) -> str:
        """Construct the label_title_raw string for a section, including edit link if requested."""
        section_type = data.get("@type")
        if section_type in ["Section", "AppendixGroup", "Appendix"]:
            label_title_raw = data.get("label_title_raw") or ""
        elif section_type == "EasySection":
            label = data.get("label") or ""
            title = data.get("title") or ""
            label_raw = f"<label>{label}</label>" if label else ""
            title_raw = (
                f'<title><named-content content-type="span" specific-use="keyword">{title}</named-content></title>'
                if title
                else ""
            )
            label_title_raw = label_raw + title_raw
        else:
            raise ValueError(f"Unsupported section type: {section_type}")

        if options and options.get("include_edit_links"):
            edit_pi = EDIT_PI_PLONE.format(url=url)
            label_title_raw += edit_pi

        return label_title_raw

    def __fetch_front(self, data: dict) -> Front:
        """Convert Plone front node data into a Front domain model."""
        return Front(content_raw=data.get("content_raw"))

    def __fetch_section(self, url: str, options: GetJATSDocumentOptions | None = None) -> Section:
        """Fetch and reconstruct a Section and subsections from Plone REST endpoints."""
        data = self.__get_json(url)
        sections = [
            self.__fetch_section(item["@id"], options)
            for item in data.get("items", [])
            if item.get("@type") == "Section" or item.get("@type") == "EasySection"
        ]
        label_title_raw = self.__get_label_title_raw(data, url, options)
        if data.get("@type") == "Section":
            return Section(
                sec_type=data.get("sec_type"),
                label=data.get("label"),
                title=data.get("title"),
                label_title_raw=label_title_raw,
                content_raw=data.get("content_raw"),
                sections=sections,
            )
        elif data.get("@type") == "EasySection":
            content = data.get("content", {}).get("data", "")
            content = f"<main>{content}</main>"
            try:
                # Use HTML parser to recover from malformed HTML
                # (e.g. unclosed <col> and <img> tags from plone richtext editor)
                html_tree = etree.fromstring(content, parser=etree.HTMLParser(recover=True))
                # HTMLParser wraps in <html><body> — extract the <main>
                main_elem = html_tree.find(".//main")
                xml_content = main_elem if main_elem is not None else html_tree
            except Exception:
                raise InternalError(f"Error parsing HTML content for EasySection at {url}")
            jats_content = str(self.transform(xml_content))
            return Section(
                sec_type="",
                label=data.get("label"),
                title=data.get("title"),
                label_title_raw=label_title_raw,
                content_raw=jats_content,
                sections=sections,
            )
        else:
            raise ValueError(f"Unsupported section type: {data.get('@type')}")

    def __fetch_appendix(self, url: str, options: GetJATSDocumentOptions | None = None) -> Appendix:
        """Fetch and reconstruct an Appendix and subsections from Plone."""
        data = self.__get_json(url)
        sections = [
            self.__fetch_section(item["@id"], options)
            for item in data.get("items", [])
            if item.get("@type") == "Section"
        ]
        return Appendix(
            sec_type=data.get("sec_type"),
            label=data.get("label"),
            title=data.get("title"),
            label_title_raw=self.__get_label_title_raw(data, url, options),
            content_raw=data.get("content_raw"),
            sections=sections,
        )

    def __fetch_appendix_group(self, url: str, options: GetJATSDocumentOptions | None = None) -> AppendixGroup:
        """Fetch and reconstruct an AppendixGroup from Plone REST endpoints."""
        data = self.__get_json(url)
        appendixes = [
            self.__fetch_appendix(item["@id"], options)
            for item in data.get("items", [])
            if item.get("@type") == "Appendix"
        ]
        return AppendixGroup(
            sec_type=data.get("sec_type"),
            label=data.get("label"),
            title=data.get("title"),
            label_title_raw=self.__get_label_title_raw(data, url, options),
            content_raw=data.get("content_raw"),
            appendixes=appendixes,
        )

    def __fetch_body(self, url: str, options: GetJATSDocumentOptions | None = None) -> Body:
        """Fetch and reconstruct the Body node and its sections from Plone."""
        data = self.__get_json(url)
        sections = [
            self.__fetch_section(item["@id"], options)
            for item in data.get("items", [])
            if item.get("@type") == "Section" or item.get("@type") == "EasySection"
        ]
        return Body(sections=sections)

    def __fetch_back(self, url: str, options: GetJATSDocumentOptions | None = None) -> Back:
        """Fetch and reconstruct the Back node and its appendix groups from Plone."""
        data = self.__get_json(url)
        appendix_groups = [
            self.__fetch_appendix_group(item["@id"], options)
            for item in data.get("items", [])
            if item.get("@type") == "AppendixGroup"
        ]
        return Back(appendix_groups=appendix_groups)

    def __fetch_article(self, url: str, options: GetJATSDocumentOptions | None = None) -> Article:
        """Fetch and build an Article node with Front, Body, and Back from Plone."""
        data = self.__get_json(url)
        front = body = back = None
        for item in data.get("items", []):
            pt = item.get("@type")
            item_url = item.get("@id")
            if pt == "Front":
                front = self.__fetch_front(item)
            elif pt == "Body":
                body = self.__fetch_body(item_url, options)
            elif pt == "Back":
                back = self.__fetch_back(item_url, options)
        if not all([front, body]):
            raise ValueError("Article must contain Front and Body")
        assert front is not None and body is not None
        return Article(front=front, body=body, back=back)

    def save_jats_document(
        self, document: JATSDocument, container: str, options: SaveJATSDocumentOptions | None = None
    ) -> str:
        """Serialize and upload a JATSDocument object graph to Plone."""
        try:
            self.__create_container(container)
            result_url = self.__create_article(document.article, container, options)
            return self.__get_path_from_url(result_url)
        except Exception as e:
            logger.error(f"Error saving JATS document: {e}")
            raise

    def __get_container_url(self, container: str) -> str:
        """Build the complete Plone API URL for a container folder."""
        return f"{self.base_url}/{container.strip('/')}"

    def __create_front(self, front: Front, container_url: str) -> str:
        """Create a Front object inside a Plone Article container."""
        logger.debug(f"Creating front node for article: {container_url}")
        response = self.httpx_client.post(
            container_url,
            json={
                "@type": "Front",
                "title": "Metadaten",
                "content_raw": front.content_raw,
            },
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

        title = section.title or "JATS-Abschnitt"

        logger.debug(f"Creating section node for article: {container_url}")
        logger.debug(f"Section title: {json.dumps(title)}")
        response = self.httpx_client.post(
            container_url,
            json={
                "@type": portal_type,
                "title": title,
                "sec_type": section.sec_type,
                "label": section.label,
                "label_title_raw": section.label_title_raw,
                "content_raw": section.content_raw,
            },
        )
        response.raise_for_status()
        response_url: str = response.json().get("@id")
        for sub_section in section.sections:
            self.__create_section(sub_section, response_url)
        return response_url

    def __create_easy_section(self, section: GenericSection, container_url: str) -> str:
        """Create an EasySection node in Plone with HTML content.
        Uses the HTML exporter to convert JATS content to HTML for storage in Plone.
        """
        html_exporter = HtmlExporter()
        label, title, html_content = self.__transform_section_to_easy_section(section, html_exporter)
        if title is None:
            title = "HTML-Abschnitt"

        logger.debug(f"Creating easy section node for article: {container_url}")
        logger.debug(f"EasySection title: {json.dumps(title)}")

        json_data = {
            "@type": "EasySection",
            "title": title,
            "label": label,
            "content": html_content,
        }

        response = self.httpx_client.post(container_url, json=json_data)
        response.raise_for_status()
        response_url: str = response.json().get("@id")
        return response_url

    def __transform_section_to_easy_section(
        self, section: GenericSection, html_exporter: HtmlExporter, level: int = 3
    ) -> tuple[str | None, str | None, str]:
        """Recursively transform a Section instance to an EasySection representation."""
        label = section.label
        title = section.title
        xml_content = section.content_raw
        html_content = html_exporter.transform_xml(xml_content) if xml_content else ""
        if html_content:
            html_content = self.__sanitize_html_for_richtext(html_content)

        for child in section.sections:
            child_label, child_title, child_content = self.__transform_section_to_easy_section(
                child, html_exporter, level + 1
            )
            heading_tag = f"h{min(level, 6)}"
            if child_title:
                if child_label:
                    heading = f"{child_label} {child_title}"
                else:
                    heading = child_title
                html_content += f"<{heading_tag}>{heading}</{heading_tag}>"
            html_content += child_content

        return label, title, html_content

    def __create_body(self, body: Body, container_url: str, options: SaveJATSDocumentOptions | None = None) -> str:
        """Create a Body node inside a Plone Article and upload its sections."""
        logger.debug(f"Creating body node for article: {container_url}")
        response = self.httpx_client.post(
            container_url,
            json={
                "@type": "Body",
                "title": "Textkörper",
            },
        )
        response.raise_for_status()
        response_url: str = response.json().get("@id")

        if options and options.get("use_html_sections"):
            # check if the first section is the table of contents (always create as normal section)
            # TODO: This is a temporary workaround. Ideally, the TOC should be handled in a more robust way.
            sections_start_index = 0
            if len(body.sections) > 0:
                first_section = body.sections[0]
                if first_section.title and first_section.title.lower() == "inhaltsverzeichnis":
                    self.__create_section(first_section, response_url)
                    sections_start_index = 1
            for section in body.sections[sections_start_index:]:
                self.__create_easy_section(section, response_url)
        else:
            for section in body.sections:
                self.__create_section(section, response_url)
        return response_url

    def __create_appendix_group(self, app_group: AppendixGroup, container_url: str) -> str:
        """Create an AppendixGroup node inside Plone Back and upload sections."""
        logger.debug(f"Creating appendix group node for article: {container_url}")
        response = self.httpx_client.post(
            container_url,
            json={
                "@type": "AppendixGroup",
                "title": app_group.title or "Anhanggruppe",
                "label": app_group.label,
                "label_title_raw": app_group.label_title_raw,
                "content_raw": app_group.content_raw,
            },
        )
        response.raise_for_status()
        response_url: str = response.json().get("@id")
        for app in app_group.appendixes:
            self.__create_section(app, response_url)
        return response_url

    def __create_back(self, back: Back | None, container_url: str) -> str | None:
        """Create a Back node inside a Plone Article and upload its appendix groups."""
        if back is None:
            return None
        logger.debug(f"Creating back node for article: {container_url}")
        response = self.httpx_client.post(
            container_url,
            json={
                "@type": "Back",
                "title": "Anhang",
            },
        )
        response.raise_for_status()
        response_url: str = response.json().get("@id")
        for app in back.appendix_groups:
            self.__create_appendix_group(app, response_url)
        return response_url

    def __create_article(self, article: Article, container: str, options: SaveJATSDocumentOptions | None = None) -> str:
        """Create an Article root node and Front, Body, Back children in Plone."""
        url = f"{self.base_url}/{container.strip('/')}"
        debug(f"Creating article node in container: {url}")
        response = self.httpx_client.post(
            url,
            json={
                "@type": "Article",
                "title": article.front.get_title() or "Artikel",
            },
        )
        response.raise_for_status()
        result_url: str = response.json().get("@id")
        self.__create_front(article.front, result_url)
        self.__create_body(article.body, result_url, options)
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
        debug(f"Creating container: {container}")
        parts = [p for p in container.strip("/").split("/") if p]
        current_path = ""

        for part in parts:
            current_path = f"{current_path}/{part}" if current_path else part
            url = f"{self.base_url}/{current_path}"

            response = self.httpx_client.get(url)
            if response.status_code == 200:
                continue
            if response.status_code != 404:
                response.raise_for_status()

            parent_url = f"{self.base_url}/{current_path.rsplit('/', 1)[0]}" if "/" in current_path else self.base_url
            response = self.httpx_client.post(parent_url, json={"@type": "Folder", "title": part, "id": part})
            response.raise_for_status()

    def __sanitize_html_for_richtext(self, html_content: str) -> str:
        """Sanitize HTML content of an easy section for Plone richtext fields."""
        tree = html.fromstring(html_content, parser=html.HTMLParser(recover=True, remove_comments=True))
        tree = cast(HtmlElement, tree)

        # remove <a> tags that have no content and only an id attribute
        empty_a_tags = tree.xpath("//a[not(*) and normalize-space(.) = '' and @id and count(@*) = 1]")
        if isinstance(empty_a_tags, list):
            for a in empty_a_tags:
                a.drop_tag()

        # remove <div> tags but keep their content
        etree.strip_tags(tree, "div")

        # wrap <img> in <picture> tags
        imgs = tree.xpath("//img")
        if isinstance(imgs, list):
            for img in imgs:
                parent = img.getparent()
                label = None
                label_element = None
                title = None
                title_element = None

                # Look at preceding siblings for optional caption elements
                prev = img.getprevious()
                if prev is not None and prev.tag == "h3" and "title" in prev.get("class", "").split():
                    title = prev.text_content().strip()
                    title_element = prev
                    prev = prev.getprevious()
                if prev is not None and prev.tag == "h5" and "label" in prev.get("class", "").split():
                    label = prev.text_content().strip()
                    label_element = prev

                # Create new structure
                p = etree.Element("p")

                if label or title:
                    figure = etree.SubElement(
                        p, "figure", attrib={"class": "image-richtext picture-variant-medium captioned"}
                    )

                    picture = etree.SubElement(figure, "picture", attrib={"class": "captioned"})

                    _ = etree.SubElement(picture, "img", attrib={"alt": img.get("alt", ""), "src": img.get("src", "")})

                    caption = etree.SubElement(figure, "figcaption", attrib={"class": "image-caption"})
                    caption.text = f"{label or ''} {title or ''}".strip()

                else:
                    picture = etree.SubElement(p, "picture")

                    _ = etree.SubElement(
                        picture,
                        "img",
                        attrib={
                            "alt": img.get("alt", ""),
                            "class": "image-richtext picture-variant-medium",
                            "src": img.get("src", ""),
                        },
                    )

                # Replace img with new structure
                parent.replace(img, p)

                # Remove consumed caption elements
                if label_element is not None:
                    label_element.drop_tree()

                if title_element is not None:
                    title_element.drop_tree()

        return etree.tostring(tree, encoding="unicode", method="html", pretty_print=True)
