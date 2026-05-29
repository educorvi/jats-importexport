"""JATS Body model.

Represents the article body containing nested Section structures.
"""

from __future__ import annotations

from lxml import etree

from .section import Section


class Body:
    """Represents a JATS <body> element containing nested Section structures."""

    sections: list[Section]

    def __init__(self, sections: list[Section]):
        """Initialize the Body model with a list of child sections."""
        self.sections = sections

    @classmethod
    def from_xml_element(cls, body: etree._Element) -> Body:
        """Construct a Body instance from an lxml <body> element.

        Args:
            body: lxml _Element node representing the <body> tag.

        Returns:
            A Body instance.
        """
        sections = [Section.from_xml_element(sec_elem) for sec_elem in body.findall("sec")]
        return cls(sections=sections)
