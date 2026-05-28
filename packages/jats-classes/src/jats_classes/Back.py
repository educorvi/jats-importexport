"""JATS Back model.

Defines the structure of a JATS <back> element containing appendix groups.
"""

from __future__ import annotations

from typing import Any

from lxml import etree

from .AppendixGroup import AppendixGroup


class Back:
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
        appendix_groups = [
            AppendixGroup.from_xml_element(app_group)
            for app_group in element.findall("app-group")
        ]
        return cls(appendix_groups=appendix_groups)
