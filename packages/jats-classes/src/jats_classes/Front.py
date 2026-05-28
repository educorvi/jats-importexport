"""JATS Front model.

Represents article front-matter metadata, publisher, author, and journal info.
"""

from __future__ import annotations

from typing import Any

from lxml import etree


class Front:
    """Represents a JATS <front> element containing article metadata."""

    content_raw: str | None

    def __init__(self, content_raw: str | None):
        """Initialize the Front model with raw XML content."""
        self.content_raw = content_raw

    @classmethod
    def from_xml_element(cls, element: etree._Element) -> Front:
        """Construct a Front instance from an lxml element representing a JATS <front>.

        Args:
            element: lxml _Element node representing the <front> tag.

        Returns:
            A Front instance.
        """
        content_raw = cls._get_raw_content(element)
        return cls(content_raw=content_raw)

    @classmethod
    def _get_raw_content(cls, front: etree._Element) -> str | None:
        """Extract internal XML markup string from the JATS <front> node."""
        result = ""
        for elem in front:
            result += etree.tostring(elem, encoding="unicode")
        if result == "":
            return None
        return result
