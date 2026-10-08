"""Plone Download Service implementation.

Provides functionality to download files and articles from a Plone CMS instance.
"""

import logging
import os
import re
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
    GenericSection,
    SchemaValidator,
    Section,
)
from lxml import etree

from ..errors import DuplicateException, InternalError, PathNotFoundExpection
from ..interface import EDIT_PI
from ..interface import GetJATSDocumentOptions as BaseGetJATSDocumentOptions

logger = logging.getLogger(__name__)


class PloneGetJATSDocumentOptions(BaseGetJATSDocumentOptions):
    """Retrieval options understood specifically by the Plone adapter."""

    pre_requested_sections: NotRequired[dict[str, dict[str, Any]] | None]


# Path to the XSLT file used for transforming HTML to JATS (EasySections)
XSL_PATH = os.path.join(os.path.dirname(__file__), "xslt", "html_to_jats.xslt")

# Processing Instruction to append to Label / Title
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

_XLINK_NS = "http://www.w3.org/1999/xlink"
_XLINK_HREF = f"{{{_XLINK_NS}}}href"
_XLINK_TITLE = f"{{{_XLINK_NS}}}title"
_XLINK_SHOW = f"{{{_XLINK_NS}}}show"

# Regular expression patterns for identifying DGUV references in text
DASHES = "\u002d\u2013\u2014"
TITLE_PATTERN = rf"(?:DGUV[{DASHES}\s](?:Vorschrift|Regel|Information|Grundsatz))"
NUMBER_PATTERN = rf"\d+(?:[{DASHES}]\d+)?"
BOUNDARY_PATTERN = rf"(?![{DASHES}\d])"
REJECTED_PATTERN = r"(?!\s*[,/]\s*\d)(?!\s+(?:und|sowie|bzw\.|bzw|oder|and|or)\s+\d)"
LINK_PATTERN = re.compile(rf"{TITLE_PATTERN} {NUMBER_PATTERN}{BOUNDARY_PATTERN}{REJECTED_PATTERN}")


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
        article = Article(front=front, body=body, back=back)
        self.__find_and_replace_link_candidates(article)
        return article

    def __fetch_front(self, data: dict, resolve_related_items: bool = True) -> Front:
        """Convert Plone front node data into a Front domain model."""
        front = Front.from_dict(data)

        # rebuild related_articles from related_articles and relatedItems
        # rebuild related_articles_translations from related_articles_translations and related_items_translations
        related_articles = {ra: "" for ra in data.get("related_articles") or []}
        related_articles_translations = {rat: ("", "") for rat in data.get("related_articles_translations") or []}
        if resolve_related_items:
            related_items, related_items_translations = self.get_related_articles(
                self.__get_path_from_plone_object(data)
            )
            if related_items:
                for item in related_items:
                    item_url = f"{self.base_url}/{item.strip('/')}"
                    metadata = self.get_metadata(item_url, resolve_related_items=False)
                    if metadata.webcode:
                        related_articles[metadata.webcode] = metadata.title or ""
            if related_items_translations:
                for item in related_items_translations:
                    item_url = f"{self.base_url}/{item.strip('/')}"
                    metadata = self.get_metadata(item_url, resolve_related_items=False)
                    if metadata.webcode:
                        related_articles_translations[metadata.webcode] = (
                            metadata.title or "",
                            metadata.xml_lang or "",
                        )

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
                    items = data.get("items", [])
                    children = data.get("children", [])
                    data["items"] = children or items
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

    def __normalize_identifier(self, value: str) -> str:
        replaced_dashes = re.sub(r"[\u2013\u2014]", "-", value)
        return re.sub(r"DGUV[-\s]", "DGUV ", replaced_dashes)

    def __is_self_match(self, normalized_article_id: str | None, normalized_match: str) -> bool:
        if not normalized_article_id:
            return False
        return normalized_match == normalized_article_id

    def __find_and_replace_links_in_section(self, article_id: str | None, language: str, section: GenericSection):
        """Wrap mentions of other DGUV articles in the section content with <ext-link> tags.

        Matches are only replaced if:
            - The match does not reference the article itself.
            - The match is allowed as a direct child of the owning element per the JATS schema.
            - The match corresponds to an existing article in Plone.
        """
        for subsection in section.sections:
            self.__find_and_replace_links_in_section(article_id, language, subsection)

        if not section.content_raw:
            return

        try:
            parser = etree.XMLParser(recover=True, resolve_entities=False)
            root = etree.fromstring(f"<root>{section.content_raw}</root>", parser=parser)
        except etree.XMLSyntaxError as exc:
            logger.warning(f"Could not parse section content for link candidates: {exc}")
            return
        if root is None:
            return

        if article_id is not None:
            article_id = self.__normalize_identifier(article_id)

        # Collect the fixes first, applying them changes the tree.
        # Each fix: (owner element, child whose tail holds the text or None for element.text, list of (match, href)).
        replacements: list[tuple[etree._Element, etree._Element | None, list[tuple[re.Match[str], str]]]] = []
        for element in root.iter(tag=etree.Element):
            text_sources = [(None, element.text)] + [(child, child.tail) for child in element]
            for ref_child, text in text_sources:
                if not text:
                    continue
                matches = []
                for match in LINK_PATTERN.finditer(text):
                    normalized_match = self.__normalize_identifier(match.group(0))
                    if self.__is_self_match(article_id, normalized_match):
                        continue
                    href = self.__get_href_from_article_id(normalized_match, language)
                    if href is None:
                        continue
                    matches.append((match, href))
                if not matches:
                    continue
                tag = etree.QName(element).localname if isinstance(element.tag, str) else ""
                if not SchemaValidator.allows_direct_child(tag, "ext-link"):
                    continue
                replacements.append((element, ref_child, matches))

        if not replacements:
            return

        for element, ref_child, matches in replacements:
            # The matched text lives either in the element's own text or in the tail of ref_child.
            if ref_child is None:
                text = element.text or ""
                insert_index = 0
            else:
                text = ref_child.tail or ""
                insert_index = element.index(ref_child) + 1
            # Work in reverse so the offsets of the earlier matches stay valid after each cut.
            for match, href in reversed(matches):
                ext_link = etree.Element("ext-link", nsmap={"xlink": _XLINK_NS})
                ext_link.set(_XLINK_HREF, href)
                ext_link.set(_XLINK_TITLE, match.group(0))
                ext_link.set(_XLINK_SHOW, "new")
                ext_link.text = match.group(0)
                ext_link.tail = text[match.end() :]
                text = text[: match.start()]
                element.insert(insert_index, ext_link)
            if ref_child is None:
                element.text = text
            else:
                ref_child.tail = text

        rendered = etree.tostring(root, encoding="unicode")
        # Strip the wrapping <root ...> ... </root> that was only added for parsing.
        section.content_raw = re.sub(r"^<root\b[^>]*>|</root>$", "", rendered)

    def __find_and_replace_link_candidates(self, article: Article):
        article_id = article.front.article_id
        language = article.front.xml_lang
        for section in article.body.sections:
            self.__find_and_replace_links_in_section(article_id, language, section)
        if article.back is not None:
            for section in article.back.appendix_groups:
                self.__find_and_replace_links_in_section(article_id, language, section)

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

    def get_path_from_webcode(self, webcode: str) -> str:
        url = f"{self.base_url}/@querystring-search"
        query = [
            {"i": "portal_type", "o": "plone.app.querystring.operation.selection.any", "v": ["Article"]},
            {"i": "webcode", "o": "plone.app.querystring.operation.string.is", "v": webcode},
        ]
        search_response = self.httpx_client.post(url, json={"query": query})
        search_response.raise_for_status()
        search_results = search_response.json().get("items", [])
        if not search_results:
            raise PathNotFoundExpection(webcode)
        if len(search_results) > 1:
            raise DuplicateException(webcode)

        result = search_results[0]
        path = self.__get_path_from_plone_object(result)
        return path

    def __get_href_from_article_id(self, article_id: str, language: str) -> str | None:
        """Look up the URL of the article whose article_id matches, or None if not found."""
        url = f"{self.base_url}/@querystring-search"
        query = [
            {"i": "portal_type", "o": "plone.app.querystring.operation.selection.any", "v": ["Article"]},
            {"i": "article_id", "o": "plone.app.querystring.operation.string.is", "v": article_id},
        ]
        try:
            search_response = self.httpx_client.post(url, json={"query": query, "fullobjects": True})
            search_response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning(f"Could not look up article_id '{article_id}': {exc}")
            return None
        search_results = search_response.json().get("items", [])

        if not search_results:
            return None
        if len(search_results) == 1:
            return search_results[0].get("@id")

        matching_language = next((item.get("@id") for item in search_results if item.get("xml_lang") == language), None)
        if matching_language:
            return matching_language
        german_match = next((item.get("@id") for item in search_results if item.get("xml_lang") == "de"), None)
        if german_match:
            return german_match

        return search_results[0].get("@id")
