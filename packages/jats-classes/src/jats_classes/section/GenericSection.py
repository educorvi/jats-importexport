"""Generic JATS section base class.

Defines properties and helper methods for extraction and representation shared by
Section and Appendix nodes.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import cast

from lxml import etree


def clean_string(string: str | None) -> str:
    """Remove leading and trailing whitespace and newlines from a string."""
    return string.strip().replace("\n", " ").replace("\t", " ").replace("\r", " ").strip() if string else ""


class GenericSection:
    """Base class for JATS Section and Appendix components.

    Holds common fields such as label, title, section type, and raw markup content,
    and provides utility methods to extract these elements from raw XML elements.
    """

    sections: Sequence[GenericSection]
    sec_type: str | None
    label_title_raw: str
    content_raw: str | None

    @property
    def title(self) -> str | None:
        return self.get_title()

    @property
    def label(self) -> str | None:
        return self.get_label()

    def __init__(
        self,
        sec_type: str | None,
        label_title_raw: str,
        content_raw: str | None,
    ):
        """Initialize the GenericSection base properties."""
        self.sec_type = sec_type
        self.label_title_raw = label_title_raw
        self.content_raw = content_raw

    @classmethod
    def _get_raw_label_title(cls, section: etree._Element) -> str:
        """Extract raw label and title xml."""
        label_element = section.find("label")
        label_string = etree.tostring(label_element, encoding="unicode") if label_element is not None else ""
        title_element = section.find("title")
        title_string = etree.tostring(title_element, encoding="unicode") if title_element is not None else ""
        return label_string + title_string

    def get_title(self) -> str | None:
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

    def get_label(self) -> str | None:
        """Get the textual label content from the raw label+title XML."""
        try:
            element = etree.fromstring(f"<root>{self.label_title_raw}</root>")
            label = element.find("label")
            if label is None:
                return None
        except etree.XMLSyntaxError:
            return None

        return clean_string(label.text) if label.text else None

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
