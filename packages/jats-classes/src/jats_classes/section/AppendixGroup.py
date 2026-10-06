"""JATS AppendixGroup model.

Represents a JATS <app-group> container wrapping multiple Appendix sections.
"""

from __future__ import annotations

from lxml import etree

from .Appendix import Appendix
from .GenericSection import GenericSection


class AppendixGroup(GenericSection):
    """Represents a JATS <app-group> container wrapping Appendix elements."""

    _appendixes: list[Appendix]

    def __init__(
        self,
        sec_type: str | None,
        label_title_raw: str,
        content_raw: str | None,
        appendixes: list[Appendix],
    ):
        """Initialize AppendixGroup containing child appendixes."""
        super().__init__(
            sec_type=sec_type,
            label_title_raw=label_title_raw,
            content_raw=content_raw,
        )
        self._appendixes = appendixes

    @property
    def sections(self) -> list[GenericSection]:
        return list(self._appendixes)

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
        appendixes = [Appendix.from_xml_element(app_elem) for app_elem in app_group.findall("app")]
        return cls(
            sec_type=content_type,
            label_title_raw=label_title_raw,
            content_raw=content_raw,
            appendixes=appendixes,
        )

    def extract_keywords(self) -> list[str]:
        keywords = super().extract_keywords()
        for appendix in self._appendixes:
            appendix_keywords = appendix.extract_keywords()
            keywords.extend(k for k in appendix_keywords if k not in keywords)
        return keywords
