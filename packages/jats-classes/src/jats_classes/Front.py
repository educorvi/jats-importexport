"""JATS Front model.

Represents article front-matter metadata, publisher, author, and journal info.
"""

from __future__ import annotations

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

    def get_title(self) -> str | None:
        """Extract the article title from the front-matter.

        Looks for the title in ``<article-meta>/<title-group>/<article-title>``.

        Returns:
            The article title as a plain-text string, or ``None`` if not found.
        """
        if self.content_raw is None:
            return None
        root = etree.fromstring(f"<front>{self.content_raw}</front>")
        title_el = root.find(".//article-meta/title-group/article-title")
        if title_el is None:
            return None
        return "".join(str(t) for t in title_el.itertext()) or None

    @classmethod
    def _get_raw_content(cls, front: etree._Element) -> str | None:
        """Extract internal XML markup string from the JATS <front> node."""
        result = ""
        for elem in front:
            result += etree.tostring(elem, encoding="unicode")
        if result == "":
            return None
        return result
