"""JATS Glossary model.

Defines a basic JATS <glossary> element and its parser/converter logic.
"""

from __future__ import annotations

from typing import override

from lxml import etree

from ..JATSClassInterface import JATSClassInterface
from .GenericSection import GenericSection


class Glossary(GenericSection, JATSClassInterface):
    """Represents a basic JATS <glossary> element."""

    def __init__(
        self,
        label_title_raw: str,
        content_raw: str | None,
    ):
        """Initialize Glossary with title, label and contents."""
        super().__init__(
            sec_type="",
            label_title_raw=label_title_raw,
            content_raw=content_raw,
        )

    @property
    def sections(self) -> list[GenericSection]:
        """Return the list of nested sections (empty for Glossary)."""
        return []

    @property
    def _tag_name(self) -> str:
        return "glossary"

    @property
    def _sec_type_attr_name(self) -> str:
        return ""

    @classmethod
    def from_xml_element(cls, glossary: etree._Element) -> Glossary:
        """Construct a Glossary from an lxml element representing a JATS <glossary> tag.

        Args:
            glossary: lxml _Element node representing the <glossary> tag.

        Returns:
            A Glossary instance.
        """
        label_title_raw = cls._get_raw_label_title(glossary)
        content_raw = cls._get_raw_content(glossary)

        return cls(
            label_title_raw=label_title_raw,
            content_raw=content_raw,
        )

    @override
    def to_xml(self) -> str:
        """Serialize the Glossary back to XML."""
        content = self.content_raw or ""
        if content:
            content = f"{content}\n"
        return f"<glossary>\n{self.label_title_raw}\n{content}</glossary>"
