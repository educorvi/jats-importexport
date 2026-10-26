"""JATS Back model.

Defines the structure of a JATS <back> element containing appendix groups.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import override

from lxml import etree

from .JATSClassInterface import JATSClassInterface
from .section import AppendixGroup


class Back(JATSClassInterface):
    """Represents a JATS <back> element containing a list of appendix groups."""

    appendix_groups: list[AppendixGroup]

    def __init__(self, appendix_groups: list[AppendixGroup]):
        """Initialize the Back model with a list of child appendix groups."""
        self.appendix_groups = appendix_groups

    @classmethod
    def from_xml_element(cls, element: etree._Element) -> Back:
        """Construct a Back instance from an lxml <back> element.

        Args:
            element: lxml _Element node representing the <back> tag.

        Returns:
            A Back instance.
        """
        appendix_groups = [AppendixGroup.from_xml_element(app_group) for app_group in element.findall("app-group")]
        return cls(appendix_groups=appendix_groups)

    @override
    def to_xml(self) -> str:
        """Serialize the Back instance back to XML."""
        content = "\n".join(ag.to_xml() for ag in self.appendix_groups)
        if content:
            content = f"{content}\n"
        return f"<back>\n{content}</back>"

    def extract_keywords(self) -> list[str]:
        keywords = []
        for appendix_group in self.appendix_groups:
            group_keywords = appendix_group.extract_keywords()
            keywords.extend(k for k in group_keywords if k not in keywords)
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
        for appendix_group in self.appendix_groups:
            appendix_group._replace_media_links(replaced_links, media_link_conversion, media_downloader)
