"""Generic JATS section base class.

Defines properties and helper methods for extraction and representation shared by
Section and Appendix nodes.
"""

from __future__ import annotations

import abc
import logging
from collections.abc import Callable
from typing import cast

from lxml import etree

from jats_classes.common import clean_string, clean_string_and_repair, try_repair_mojibake, try_repair_mojibake_element

logger = logging.getLogger(__name__)

XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"
XLINK_HREF_ATTRIBUTE = f"{{{XLINK_NAMESPACE}}}href"
XLINK_HREF_LITERAL = "xlink:href"
ASSET_ELEMENT_TAGS = frozenset({"graphic", "inline-graphic", "media"})


class GenericSection(metaclass=abc.ABCMeta):
    """Base class for JATS Section, Appendix and AppendixGroup components.

    Holds common fields such as label, title, section type, and raw markup content,
    and provides utility methods to extract these elements from raw XML elements.
    """

    sec_type: str | None
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

    def __init__(
        self,
        sec_type: str | None,
        label_title_raw: str,
        content_raw: str | None,
        media_link_conversion: Callable[[str], str] | None = None,
    ):
        """Initialize the GenericSection base properties."""
        self.sec_type = sec_type
        self.label_title_raw = label_title_raw
        if content_raw and media_link_conversion:
            self.content_raw = self._replace_media_links_in_content(content_raw, media_link_conversion)
        else:
            self.content_raw = content_raw

    @property
    @abc.abstractmethod
    def sections(self) -> list[GenericSection]:
        """Return the list of nested sections."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def _tag_name(self) -> str:
        """Return the XML tag name for this section type."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def _sec_type_attr_name(self) -> str:
        """Return the name of the XML attribute that specifies the section type."""
        raise NotImplementedError

    def to_xml(self) -> str:
        """Serialize the GenericSection back to XML."""
        sec_type = f' {self._sec_type_attr_name}="{self.sec_type}"' if self.sec_type else ""
        sub_content = "\n".join(section.to_xml() for section in self.sections)
        if sub_content:
            sub_content = f"{sub_content}\n"
        content = self.content_raw or ""
        if content:
            content = f"{content}\n"
        return f"<{self._tag_name}{sec_type}>\n{self.label_title_raw}\n{content}{sub_content}</{self._tag_name}>"

    def _replace_media_links_in_content(self, content: str, media_link_conversion: Callable[[str], str]) -> str:
        """Replace the media links in the section's content using the provided conversion function.

        The content is parsed as XML and only the elements of ``ASSET_ELEMENT_TAGS`` are taken into
        account, so hrefs of link elements (``ext-link``, ``uri``, ``related-article``, ...) — which
        may reference other articles of the same Plone site — are not mistaken for assets.

        Args:
            media_link_conversion: A callable that takes a media link and returns the converted link.

        Returns:
            str: The content with media links replaced.
        """
        if not content:
            return ""

        try:
            root = etree.fromstring(
                f"<root>{content}</root>",
                parser=etree.XMLParser(recover=True, resolve_entities=False),
            )
        except etree.XMLSyntaxError as e:
            logger.warning(f"Could not parse content to replace media links: {e}")
            return content
        if root is None:
            return content

        for element in root.iter(tag=etree.Element):
            tag = etree.QName(element).localname.lower() if isinstance(element.tag, str) else ""
            if tag not in ASSET_ELEMENT_TAGS:
                continue
            for attr in [XLINK_HREF_ATTRIBUTE, XLINK_HREF_LITERAL]:
                href_value = element.get(attr)
                if not href_value or not isinstance(href_value, str) or href_value.startswith("#"):
                    continue
                element.set(attr, media_link_conversion(href_value))

        return (root.text or "") + "".join(
            [etree.tostring(child, encoding="unicode", with_tail=True, pretty_print=True) for child in root]
        )

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
            if not isinstance(node, etree._Element) and not isinstance(node, str):
                result += etree.tostring(node, encoding="unicode")
                continue

            if isinstance(node, str):
                result += try_repair_mojibake(node)
                continue

            if node.tag in ["label", "title"]:
                if node.tail:
                    result += try_repair_mojibake(node.tail)
                continue
            if node.tag in ["sec", "app"]:
                break

            result += etree.tostring(try_repair_mojibake_element(node), encoding="unicode")

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
