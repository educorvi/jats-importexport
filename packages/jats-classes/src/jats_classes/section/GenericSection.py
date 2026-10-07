"""Generic JATS section base class.

Defines properties and helper methods for extraction and representation shared by
Section and Appendix nodes.
"""

from __future__ import annotations

import abc
import re
from typing import cast

from lxml import etree


def clean_string(string: str) -> str:
    """Remove leading and trailing whitespace and newlines from a string."""
    return re.sub(r"[\s]+", " ", string).strip()


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

    def __init__(self, sec_type: str | None, label_title_raw: str, content_raw: str | None):
        """Initialize the GenericSection base properties."""
        self.sec_type = sec_type
        self.label_title_raw = label_title_raw
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

    @classmethod
    def _get_raw_label_title(cls, section: etree._Element) -> str:
        """Extract raw label and title xml."""
        label_element = section.find("label")
        label_string = etree.tostring(label_element, encoding="unicode") if label_element is not None else ""
        title_element = section.find("title")
        title_string = etree.tostring(title_element, encoding="unicode") if title_element is not None else ""
        return label_string + title_string

    @classmethod
    def _get_raw_content(cls, section: etree._Element) -> str | None:
        """Extract inner raw XML content, ignoring label, title, and nested sections."""
        result = ""
        nodes = cast(list[etree._Element | str], section.xpath("./node()"))
        for node in nodes:
            if isinstance(node, str):
                result += node
                continue

            if not isinstance(node, etree._Element):
                result += etree.tostring(node, encoding="unicode")
                continue

            if not isinstance(node.tag, str):
                result += etree.tostring(node, encoding="unicode")
                continue

            if node.tag in ["label", "title"]:
                if node.tail:
                    result += node.tail
                continue
            if node.tag in ["sec", "app"]:
                break

            result += etree.tostring(node, encoding="unicode")

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
                if element.text:
                    if (k := clean_string(element.text)) not in keywords and k != "":
                        keywords.append(k)
        except etree.XMLSyntaxError:
            pass

        return keywords
