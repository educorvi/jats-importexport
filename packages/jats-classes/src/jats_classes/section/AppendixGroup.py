"""JATS AppendixGroup model.

Represents a JATS <app-group> container wrapping multiple Appendix sections.
"""

from __future__ import annotations

from lxml import etree

from ..JATSClassInterface import JATSClassInterface
from .Appendix import Appendix
from .GenericSection import GenericSection
from .RefList import RefList


class AppendixGroup(GenericSection, JATSClassInterface):
    """Represents a JATS <app-group> container wrapping Appendix elements."""

    _sections: list[Appendix | RefList]

    def __init__(
        self,
        sec_type: str | None,
        label_title_raw: str,
        content_raw: str | None,
        sections: list[Appendix | RefList],
    ):
        """Initialize AppendixGroup containing child appendixes."""
        super().__init__(
            sec_type=sec_type,
            label_title_raw=label_title_raw,
            content_raw=content_raw,
        )
        self._sections = sections

    @property
    def sections(self) -> list[GenericSection]:
        return list(self._sections)

    @property
    def _tag_name(self) -> str:
        return "app-group"

    @property
    def _sec_type_attr_name(self) -> str:
        return "content-type"

    @classmethod
    def from_xml_element(cls, app_group: etree._Element) -> AppendixGroup:
        """Construct an AppendixGroup from an lxml <app-group> element.

        Args:
            app_group: lxml _Element node representing the <app-group> tag.

        Returns:
            An AppendixGroup instance.
        """
        content_type = app_group.attrib.get("content-type")
        label_title_raw = cls._get_raw_label_title(app_group)
        content_raw = cls._get_raw_content(app_group)

        sections: list[Appendix | RefList] = []
        for child in app_group:
            if child.tag == "app":
                sections.append(Appendix.from_xml_element(child))
            elif child.tag == "ref-list":
                sections.append(RefList.from_xml_element(child))

        return cls(
            sec_type=content_type,
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
