import abc
import logging
from collections.abc import Callable
from typing import cast, override

from lxml import etree

from jats_classes.common import clean_string, clean_string_and_repair, try_repair_mojibake, try_repair_mojibake_element
from jats_classes.JATSClassInterface import JATSClassInterface

logger = logging.getLogger(__name__)

XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"
XLINK_HREF_ATTRIBUTE = f"{{{XLINK_NAMESPACE}}}href"
XLINK_HREF_LITERAL = "xlink:href"
ASSET_ELEMENT_TAGS = frozenset({"graphic", "inline-graphic", "media"})


class BaseSection(JATSClassInterface, metaclass=abc.ABCMeta):
    label_title_raw: str
    content_raw: str | None

    @property
    def title(self) -> str | None:
        """Recursively resolve textual title content from the raw label+title XML.

        Iterates through <named-content> and <styled-content> tags and ignores all other tags.
        """
        try:
            element = etree.fromstring(f"<root>{self.label_title_raw}</root>")
            title = element.find("title")
            if title is None:
                return None
        except etree.XMLSyntaxError:
            return None

        def collect_text(element: etree._Element) -> str:
            parts = []
            if element.text:
                parts.append(element.text)
            for child in element:
                if child.tag in ["named-content", "styled-content"]:
                    parts.append(collect_text(child))
                if child.tail:
                    parts.append(child.tail)
            return "".join(parts)

        return clean_string(collect_text(title)) or None

    @property
    def label(self) -> str | None:
        """Get the textual label content from the raw label+title XML."""
        try:
            element = etree.fromstring(f"<root>{self.label_title_raw}</root>")
            label = element.find("label")
            if label is None:
                return None
        except etree.XMLSyntaxError:
            return None

        return clean_string(label.text) if label.text else None

    def __init__(self, label_title_raw: str, content_raw: str | None):
        self.label_title_raw = label_title_raw
        self.content_raw = content_raw

    @classmethod
    def _get_raw_label_title(cls, section: etree._Element) -> str:
        """Extract raw label and title xml."""
        label_element = try_repair_mojibake_element(section.find("label"))
        label_string = etree.tostring(label_element, encoding="unicode") if label_element is not None else ""
        title_element = try_repair_mojibake_element(section.find("title"))
        title_string = etree.tostring(title_element, encoding="unicode") if title_element is not None else ""
        return label_string + title_string

    @classmethod
    def _get_raw_content(cls, section: etree._Element) -> str | None:
        """Extract inner raw XML content, ignoring label, title, and nested sections."""
        result = ""
        nodes = section.xpath("./node()")
        if not isinstance(nodes, list):
            return None

        for node in nodes:
            if isinstance(node, str):
                result += try_repair_mojibake(node)
                continue

            if not isinstance(node, etree._Element):
                continue

            if node.tag in ["label", "title"]:
                if node.tail:
                    result += try_repair_mojibake(node.tail)
                continue
            if node.tag in ["sec", "app", "glossary", "ref-list"]:
                break

            repaired = try_repair_mojibake_element(node)
            if repaired is None:
                continue
            result += etree.tostring(repaired, encoding="unicode")

        if result.strip() == "":
            return None
        return result

    @classmethod
    def get_raw_content(cls, element: etree._Element) -> str | None:
        """Public method to get the raw content of a section like element."""
        return cls._get_raw_content(element)

    def extract_keywords(self) -> list[str]:
        keywords: list[str] = []
        try:
            root = etree.fromstring(f"<root>{self.label_title_raw}{self.content_raw or ''}</root>")
            for element in cast(list[etree._Element], root.xpath('.//named-content[@specific-use="keyword"]')):
                keyword = clean_string_and_repair(element.text)
                if keyword and keyword != "" and keyword not in keywords:
                    keywords.append(keyword)
        except etree.XMLSyntaxError:
            pass

        return keywords

    @override
    def replace_media_links(
        self,
        media_link_conversion: Callable[[str, tuple[bytes, str] | None], str],
        media_downloader: Callable[[str], tuple[bytes, str]] | None = None,
    ) -> dict[str, tuple[str, tuple[bytes, str] | None]]:
        replaced_links = {}
        self._replace_media_links(replaced_links, media_link_conversion, media_downloader)
        return replaced_links

    def _replace_media_links(
            self,
            replaced_links: dict[str, tuple[str, tuple[bytes, str] | None]],
            media_link_conversion: Callable[[str, tuple[bytes, str] | None], str],
            media_downloader: Callable[[str], tuple[bytes, str]] | None = None,
        ) -> None:
            self._replace_media_links_in_content(replaced_links, media_link_conversion, media_downloader)

    def _replace_media_links_in_content(
        self,
        replaced_links: dict[str, tuple[str, tuple[bytes, str] | None]],
        media_link_conversion: Callable[[str, tuple[bytes, str] | None], str],
        media_downloader: Callable[[str], tuple[bytes, str]] | None = None,
    ) -> None:
        """Replace the media links in the section's content using the provided conversion function.
        If a media_downloader is provided, it will be used to download the media content for the given links.

        The content is parsed as XML and only the elements of ``ASSET_ELEMENT_TAGS`` are taken into
        account, so hrefs of link elements (``ext-link``, ``uri``, ``related-article``, ...) — which
        may reference other articles of the same Plone site — are not mistaken for assets.
        """
        if not self.content_raw:
            return

        try:
            root = etree.fromstring(
                f"<root>{self.content_raw}</root>",
                parser=etree.XMLParser(recover=True, resolve_entities=False),
            )
        except etree.XMLSyntaxError as e:
            logger.warning(f"Could not parse content to replace media links: {e}")
            return
        if root is None:
            return

        for element in root.iter(tag=etree.Element):
            tag = etree.QName(element).localname.lower() if isinstance(element.tag, str) else ""
            if tag not in ASSET_ELEMENT_TAGS:
                continue
            for attr in [XLINK_HREF_ATTRIBUTE, XLINK_HREF_LITERAL]:
                href_value = element.get(attr)
                if not href_value or not isinstance(href_value, str) or href_value.startswith("#"):
                    continue

                if href_value in replaced_links:
                    new_href, _ = replaced_links[href_value]
                else:
                    if media_downloader:
                        try:
                            media_content = media_downloader(href_value)
                        except Exception as e:
                            logger.warning(f"Failed to download media from {href_value}: {e}")
                            media_content = None
                    else:
                        media_content = None
                    new_href = media_link_conversion(href_value, media_content)
                    replaced_links[href_value] = (new_href, media_content)

                element.set(attr, new_href)

        new_content = (root.text or "") + "".join(
            [etree.tostring(child, encoding="unicode", with_tail=True, pretty_print=True) for child in root]
        )
        self.content_raw = new_content