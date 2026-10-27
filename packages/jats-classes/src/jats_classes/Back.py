"""JATS Back model.

Defines the structure of a JATS <back> element containing appendix groups.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import override

from lxml import etree

from .JATSClassInterface import JATSClassInterface
from .section import AppendixGroup, GenericSection, Glossary, RefList


class Back(JATSClassInterface):
    """Represents a JATS <back> element containing a list of appendix groups."""

    _sections: list[AppendixGroup | Glossary | RefList]

    def __init__(self, sections: list[AppendixGroup | Glossary | RefList]):
        """Initialize the Back model with a list of child appendix groups."""
        self._sections = sections

    @property
    def sections(self) -> list[GenericSection]:
        return list(self._sections)

    @classmethod
    def from_xml_element(cls, element: etree._Element) -> Back:
        """Construct a Back instance from an lxml <back> element.

        Args:
            element: lxml _Element node representing the <back> tag.

        Returns:
            A Back instance.
        """
        sections = []
        for child in element:
            if child.tag == "app-group":
                sections.append(AppendixGroup.from_xml_element(child))
            elif child.tag == "glossary":
                sections.append(Glossary.from_xml_element(child))
            elif child.tag == "ref-list":
                sections.append(RefList.from_xml_element(child))
        return cls(sections=sections)

    @override
    def to_xml(self) -> str:
        """Serialize the Back instance back to XML."""
        content = "\n".join(section.to_xml() for section in self.sections)
        if content:
            content = f"{content}\n"
        return f"<back>\n{content}</back>"

    def extract_keywords(self) -> list[str]:
        keywords = []
        for section in self.sections:
            section_keywords = section.extract_keywords()
            keywords.extend(k for k in section_keywords if k not in keywords)
        return keywords

    @override
    def replace_media_links(
        self,
        media_link_conversion: Callable[[str, tuple[bytes, str] | None], str],
        media_downloader: Callable[[str], tuple[bytes, str]] | None = None,
    ) -> dict[str, tuple[str, tuple[bytes, str] | None]]:
        replaced_links = {}
        self._replace_media_links(replaced_links, media_link_conversion, media_downloader)
        return replaced_links

    def _replace_media_links(
        self,
        replaced_links: dict[str, tuple[str, tuple[bytes, str] | None]],
        media_link_conversion: Callable[[str, tuple[bytes, str] | None], str],
        media_downloader: Callable[[str], tuple[bytes, str]] | None = None,
    ) -> None:
        for section in self.sections:
            section._replace_media_links(replaced_links, media_link_conversion, media_downloader)
