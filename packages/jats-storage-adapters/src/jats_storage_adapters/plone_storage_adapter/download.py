"""Plone Download Service implementation.

Provides functionality to download files and articles from a Plone CMS instance.
"""

import logging
import os
from typing import Any, NotRequired
from urllib.parse import urlparse

import httpx
from jats_classes import (
    Appendix,
    AppendixGroup,
    Article,
    Back,
    Body,
    Front,
    Section,
)
from lxml import etree

from ..errors import InternalError
from ..interface import EDIT_PI
from ..interface import GetJATSDocumentOptions as BaseGetJATSDocumentOptions

logger = logging.getLogger(__name__)


class PloneGetJATSDocumentOptions(BaseGetJATSDocumentOptions):
    """Retrieval options understood specifically by the Plone adapter."""

    pre_requested_sections: NotRequired[dict[str, dict[str, Any]] | None]


XSL_PATH = os.path.join(os.path.dirname(__file__), "xslt", "html_to_jats.xslt")

EDIT_PI_PLONE = EDIT_PI.format(url="{url}/edit")

# review state mapping from vur workflow
# status in plone with vur workflow -> status in jats
REVIEW_STATE_MAPPING: dict[str, str] = {
    "internally_published": "veröffentlicht",  # yes, also published
    "published": "veröffentlicht",
    "private": "privat",
    "draft": "Entwurf",
}
DEFAULT_REVIEW_STATE: str = "draft"


class PloneDownloadService:
    """Service class for handling Plone file downloads and article retrieval."""

    base_url: str
    httpx_client: httpx.Client
    transform: etree.XSLT

    def __init__(self, base_url: str, httpx_client: httpx.Client):
        self.base_url = base_url
        self.httpx_client = httpx_client
        xsl_path = os.path.abspath(XSL_PATH)
        self.transform = etree.XSLT(etree.parse(xsl_path))

    # Private helper methods

    def __get_path_from_url(self, url: str) -> str:
        base_path = urlparse(self.base_url).path.rstrip("/")
        result_path = urlparse(url).path
        if result_path.lower().startswith(base_path.lower()):
            return result_path[len(base_path) :]
        return result_path

    def __get_path_from_plone_object(self, obj: dict) -> str:
        obj_id = obj.get("@id", "")
        return self.__get_path_from_url(obj_id)

    @staticmethod
    def __plone_status_to_jats_status(plone_status: str | None) -> str:
        if plone_status is None or plone_status not in REVIEW_STATE_MAPPING:
            plone_status = DEFAULT_REVIEW_STATE
        return REVIEW_STATE_MAPPING.get(plone_status, "")

    def download_file(self, url: str) -> tuple[bytes, str]:
        """Download a file from the given URL."""
        if not self.__is_url_within_base(url):
            raise ValueError(f"Refusing to download file from outside the configured Plone instance: {url}")
        response1 = self.httpx_client.get(url)
        response1.raise_for_status()
        content_type = response1.headers.get("content-type")
        if not content_type or not isinstance(content_type, str):
            raise InternalError(f"Could not determine content-type for {url}")
        if content_type.startswith("image/"):
            return response1.content, content_type
        elif content_type == "application/json":
            data = response1.json()
            field = data.get("image") or data.get("file")
            download_url = field.get("download") if field else None
            if not download_url:
                raise InternalError(f"No downloadable file found for {url}")
            response = self.httpx_client.get(download_url, headers={"Accept": "*/*"})
            response.raise_for_status()
            content_type = field.get("content-type") or response.headers.get("content-type", "application/octet-stream")
            return response.content, content_type
        else:
            raise InternalError(f"Unsupported content-type for {url}: {content_type}")

    def __is_url_within_base(self, url: str) -> bool:
        """Check whether a URL points into this adapter's configured Plone instance."""
        base = urlparse(self.base_url)
        target = urlparse(url)
        return (
            target.scheme in ("http", "https")
            and target.netloc.lower() == base.netloc.lower()
            and target.path.lower().startswith(base.path.lower())
        )

    def fetch_article(self, url: str, options: PloneGetJATSDocumentOptions | None = None) -> Article:
        """Fetch and build an Article node with Front, Body, and Back from Plone."""
        data = self.__get_json(url, options)
        pre_request = self.httpx_client.get(url + "/@all_descendents")
        if pre_request.status_code == 200:
            if options is None:
                options = PloneGetJATSDocumentOptions(include_edit_links=False, pre_requested_sections=None)
            pre_request_res = pre_request.json()
            pre_request_data = {}
            for item in pre_request_res.get("items", []):
                pre_request_data[item["@id"]] = item
                options["pre_requested_sections"] = pre_request_data
        front = body = back = None
        for item in data.get("items", []):
            pt = item.get("@type")
            item_url = item.get("@id")
            if pt == "Body":
                body = self.__fetch_body(item_url, options)
            elif pt == "Back":
                back = self.__fetch_back(item_url, options)
        front = self.__fetch_front(data)
        if not all([front, body]):
            raise ValueError("Article must contain Front and Body")
        assert front is not None and body is not None
        return Article(front=front, body=body, back=back)

    def __fetch_front(self, data: dict, resolve_related_items: bool = True) -> Front:
        """Convert Plone front node data into a Front domain model."""
        front = Front.from_dict(data)

        # rebuild related_articles from related_articles and relatedItems
        # rebuild related_articles_translations from related_articles_translations and related_items_translations
        related_articles = {ra: "" for ra in data.get("related_articles") or []}
        related_articles_translations = {rat: "" for rat in data.get("related_articles_translations") or []}
        if resolve_related_items:
            related_items, related_items_translations = self.get_related_articles(
                self.__get_path_from_plone_object(data)
            )
            if related_items:
                for item in related_items:
                    metadata = self.get_metadata(item, resolve_related_items=False)
                    if metadata.article_id:
                        related_articles[metadata.article_id] = metadata.title or ""
            if related_items_translations:
                for item in related_items_translations:
                    metadata = self.get_metadata(item, resolve_related_items=False)
                    if metadata.article_id:
                        related_articles_translations[metadata.article_id] = metadata.title or ""

        front.related_articles_map = related_articles
        front.related_articles_translations_map = related_articles_translations

        # rebuild veroeffentlichungsstatus from plone workflow state
        review_state = data.get("review_state")
        front.veroeffentlichungsstatus = self.__plone_status_to_jats_status(review_state)

        return front

    def __fetch_body(self, url: str, options: PloneGetJATSDocumentOptions | None = None) -> Body:
        """Fetch and reconstruct the Body node and its sections from Plone."""
        data = self.__get_json(url, options)
        sections = [
            self.__fetch_section(item["@id"], options)
            for item in data.get("items", [])
            if item.get("@type") == "Section" or item.get("@type") == "EasySection"
        ]
        return Body(sections=sections)

    def __fetch_back(self, url: str, options: PloneGetJATSDocumentOptions | None = None) -> Back:
        """Fetch and reconstruct the Back node and its appendix groups from Plone."""
        data = self.__get_json(url, options)
        appendix_groups = [
            self.__fetch_appendix_group(item["@id"], options)
            for item in data.get("items", [])
            if item.get("@type") == "AppendixGroup"
        ]
        return Back(appendix_groups=appendix_groups)

    def __fetch_appendix_group(self, url: str, options: PloneGetJATSDocumentOptions | None = None) -> AppendixGroup:
        """Fetch and reconstruct an AppendixGroup from Plone REST endpoints."""
        data = self.__get_json(url, options)
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

    def __fetch_appendix(self, url: str, options: PloneGetJATSDocumentOptions | None = None) -> Appendix:
        """Fetch and reconstruct an Appendix and subsections from Plone."""
        data = self.__get_json(url, options)
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

    def __fetch_section(self, url: str, options: PloneGetJATSDocumentOptions | None = None) -> Section:
        """Fetch and reconstruct a Section and subsections from Plone REST endpoints."""
        data = self.__get_json(url, options)
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

    def __get_json(self, url: str, options: PloneGetJATSDocumentOptions | None) -> dict:
        """Fetch JSON data from a Plone API endpoint."""
        if options and options.get("pre_requested_sections"):
            pre_requested_sections = options.get("pre_requested_sections")
            if pre_requested_sections:
                data = pre_requested_sections.get(url)
                if data:
                    return data
        response = self.httpx_client.get(url)
        response.raise_for_status()
        return response.json()

    def __get_label_title_raw(self, data: dict, url: str, options: PloneGetJATSDocumentOptions | None = None) -> str:
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

    def get_metadata(self, url: str, resolve_related_items: bool = True) -> Front:
        article = self.__get_json(url, None)
        front = self.__fetch_front(article, resolve_related_items=resolve_related_items)
        return front

    def get_related_articles(self, path: str) -> tuple[list[str], list[str]]:
        path_set_related: set[str] = set()
        path_set_translations: set[str] = set()

        url = self.base_url + "/@relations?source=/" + path.lstrip("/")
        response = self.httpx_client.get(url)
        response.raise_for_status()
        data = response.json()
        for item in data.get("relations", {}).get("relatedItems", {}).get("items", []):
            path_set_related.add(self.__get_path_from_plone_object(item["target"]))
        for item in data.get("relations", {}).get("related_items_translations", {}).get("items", []):
            path_set_translations.add(self.__get_path_from_plone_object(item["target"]))

        url = self.base_url + "/@relations?target=/" + path.lstrip("/")
        response = self.httpx_client.get(url)
        response.raise_for_status()
        data = response.json()
        for item in data.get("relations", {}).get("relatedItems", {}).get("items", []):
            path_set_related.add(self.__get_path_from_plone_object(item["source"]))
        for item in data.get("relations", {}).get("related_items_translations", {}).get("items", []):
            path_set_translations.add(self.__get_path_from_plone_object(item["source"]))

        return list(path_set_related), list(path_set_translations)
