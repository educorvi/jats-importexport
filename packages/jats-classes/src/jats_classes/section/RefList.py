"""JATS Reference List model.

Defines a basic JATS <ref-list> element and its parser/converter logic.
"""

from __future__ import annotations

from typing import override

from lxml import etree

from ..JATSClassInterface import JATSClassInterface
from .GenericSection import GenericSection


class RefList(GenericSection, JATSClassInterface):
    """Represents a basic JATS <ref-list> element."""

    def __init__(
        self,
        label_title_raw: str,
        content_raw: str | None,
    ):
        """Initialize RefList with title, label and contents."""
        super().__init__(
            sec_type="",
            label_title_raw=label_title_raw,
            content_raw=content_raw,
        )

    @property
    def sections(self) -> list[GenericSection]:
        """Return the list of nested sections (empty for RefList)."""
        return []

    @property
    def _tag_name(self) -> str:
        return "ref-list"

    @property
    def _sec_type_attr_name(self) -> str:
        return ""

    @classmethod
    def from_xml_element(cls, ref_list: etree._Element) -> RefList:
        """Construct a RefList from an lxml element representing a JATS <ref-list> tag.

        Args:
            ref_list: lxml _Element node representing the <ref-list> tag.

        Returns:
            A RefList instance.
        """
        label_title_raw = cls._get_raw_label_title(ref_list)
        content_raw = cls._get_raw_content(ref_list)

        return cls(
            label_title_raw=label_title_raw,
            content_raw=content_raw,
        )

    @override
    def to_xml(self) -> str:
        """Serialize the RefList back to XML."""
        content = self.content_raw or ""
        if content:
            content = f"{content}\n"
        return f"<ref-list>\n{self.label_title_raw}\n{content}</ref-list>"