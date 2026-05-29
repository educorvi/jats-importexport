"""Generic JATS section base class.

Defines properties and helper methods for extraction and representation shared by
Section and Appendix nodes.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import cast

from lxml import etree


class GenericSection:
    """Base class for JATS Section and Appendix components.

    Holds common fields such as label, title, section type, and raw markup content,
    and provides utility methods to extract these elements from raw XML elements.
    """

    sections: Sequence[GenericSection]
    sec_type: str | None
    label: str | None
    title: str | None
    label_title_raw: str
    content_raw: str | None

    def __init__(
        self,
        sec_type: str | None,
        label: str | None,
        title: str | None,
        label_title_raw: str,
        content_raw: str | None,
    ):
        """Initialize the GenericSection base properties."""
        self.sec_type = sec_type
        self.label = label
        self.title = title
        self.label_title_raw = label_title_raw
        self.content_raw = content_raw

    @classmethod
    def _get_label_and_title(cls, section: etree._Element) -> tuple[str | None, str | None, str]:
        """Extract label, title, and raw combined label+title XML string."""
        label_element = section.find("label")
        label_string = etree.tostring(label_element, encoding="unicode") if label_element is not None else ""
        title_element = section.find("title")
        title_string = etree.tostring(title_element, encoding="unicode") if title_element is not None else ""
        label_title_raw = label_string + title_string
        label = label_element.text if label_element is not None else None
        title = cls._get_title(title_element)
        return label, title, label_title_raw

    @classmethod
    def _get_title(cls, title_or_named_content: etree._Element | None) -> str | None:
        """Recursively resolve textual title content, bypassing <named-content> tags."""
        if title_or_named_content is None:
            return None
        named_content = title_or_named_content.find("named-content")
        if named_content is not None:
            return cls._get_title(named_content)
        else:
            return title_or_named_content.text

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
