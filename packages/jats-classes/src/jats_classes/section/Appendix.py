"""JATS Appendix model.

Defines a JATS <app> (Appendix) element and its parser/converter logic.
"""

from __future__ import annotations

from lxml import etree

from .GenericSection import GenericSection
from .Section import Section


class Appendix(GenericSection):
    """Represents a JATS <app> (Appendix) element containing nested Sections."""

    _sections: list[Section]

    def __init__(
        self,
        sec_type: str | None,
        label_title_raw: str,
        content_raw: str | None,
        sections: list[Section],
    ):
        """Initialize Appendix with metadata and nested sections."""
        super().__init__(
            sec_type=sec_type,
            label_title_raw=label_title_raw,
            content_raw=content_raw,
        )
        self._sections = sections

    @property
    def sections(self) -> list[GenericSection]:
        return list(self._sections)

    @classmethod
    def from_xml_element(cls, app: etree._Element) -> Appendix:
        """Construct an Appendix from an lxml element representing a JATS <app> tag.

        Args:
            app: lxml _Element node representing the <app> tag.

        Returns:
            An Appendix instance.
        """
        app_type = app.attrib.get("app-type")
        label_title_raw = cls._get_raw_label_title(app)
        content_raw = cls._get_raw_content(app)
        sections = [Section.from_xml_element(sec_elem) for sec_elem in app.findall("sec")]
        return cls(
            sec_type=app_type,
            label_title_raw=label_title_raw,
            content_raw=content_raw,
            sections=sections,
        )

    def extract_keywords(self) -> list[str]:
        keywords = super().extract_keywords()
        for section in self._sections:
            section_keywords = section.extract_keywords()
            keywords.extend(k for k in section_keywords if k not in keywords)
        return keywords
