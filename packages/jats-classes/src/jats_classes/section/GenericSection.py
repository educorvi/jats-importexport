"""Generic JATS section base class.

Defines properties and helper methods for extraction and representation shared by
Section and Appendix nodes.
"""

from __future__ import annotations

import abc
from collections.abc import Callable
from typing import override

from jats_classes.section.BaseSection import BaseSection


class GenericSection(BaseSection, metaclass=abc.ABCMeta):
    """Base class for JATS Section, Appendix and AppendixGroup components.

    Holds common fields such as label, title, section type, and raw markup content,
    and provides utility methods to extract these elements from raw XML elements.
    """

    sec_type: str | None

    def __init__(
        self,
        sec_type: str | None,
        label_title_raw: str,
        content_raw: str | None,
    ):
        """Initialize the GenericSection base properties."""
        super().__init__(label_title_raw, content_raw)
        self.sec_type = sec_type

    @property
    @abc.abstractmethod
    def sections(self) -> list[GenericSection]:
        """Return the list of nested sections."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def _tag_name(self) -> str:
        """Return the XML tag name for this section type."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def _sec_type_attr_name(self) -> str:
        """Return the name of the XML attribute that specifies the section type."""
        raise NotImplementedError

    @override
    def to_xml(self) -> str:
        """Serialize the GenericSection back to XML."""
        sec_type = f' {self._sec_type_attr_name}="{self.sec_type}"' if self.sec_type else ""
        sub_content = "\n".join(section.to_xml() for section in self.sections)
        if sub_content:
            sub_content = f"{sub_content}\n"
        content = self.content_raw or ""
        if content:
            content = f"{content}\n"
        return f"<{self._tag_name}{sec_type}>\n{self.label_title_raw}\n{content}{sub_content}</{self._tag_name}>"

    def _replace_media_links(
        self,
        replaced_links: dict[str, tuple[str, tuple[bytes, str] | None]],
        media_link_conversion: Callable[[str, tuple[bytes, str] | None], str],
        media_downloader: Callable[[str], tuple[bytes, str]] | None = None,
    ) -> None:
        self._replace_media_links_in_content(replaced_links, media_link_conversion, media_downloader)
        for section in self.sections:
            section._replace_media_links(replaced_links, media_link_conversion, media_downloader)
