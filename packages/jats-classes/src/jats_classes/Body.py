"""JATS Body model.

Represents the article body containing nested Section structures.
"""

from __future__ import annotations

import logging

from lxml import etree

from .section import Section
from .section.GenericSection import GenericSection

logger = logging.getLogger(__name__)


_DUMMY_TITLE = (
    """<title xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink"></title>"""
)


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

        # move body content to a section
        body_content_raw = GenericSection.get_raw_content(body)
        if body_content_raw:
            logger.warning(
                "Body element contains raw content outside of <sec> elements. Content will be moved to a new section."
            )
            body_as_section = Section(
                sec_type=None, label_title_raw=_DUMMY_TITLE, content_raw=body_content_raw, sections=[]
            )
            sections.insert(0, body_as_section)

        return cls(sections=sections)
