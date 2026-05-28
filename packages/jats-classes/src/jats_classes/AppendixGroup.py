"""JATS AppendixGroup model.

Represents a JATS <app-group> container wrapping multiple Appendix sections.
"""

from __future__ import annotations

from typing import Any

from lxml import etree

from .section import Appendix, GenericSection


class AppendixGroup(GenericSection):
    """Represents a JATS <app-group> container wrapping Appendix elements."""

    appendixes: list[Appendix]

    def __init__(
        self,
        sec_type: str | None,
        label: str | None,
        title: str | None,
        label_title_raw: str,
        content_raw: str | None,
        appendixes: list[Appendix],
    ):
        """Initialize AppendixGroup containing child appendixes."""
        super().__init__(
            sec_type=sec_type,
            label=label,
            title=title,
            label_title_raw=label_title_raw,
            content_raw=content_raw,
        )
        self.appendixes = appendixes

    @classmethod
    def from_xml_element(cls, app_group: etree._Element) -> AppendixGroup:
        """Construct an AppendixGroup from an lxml <app-group> element.

        Args:
            app_group: lxml _Element node representing the <app-group> tag.

        Returns:
            An AppendixGroup instance.
        """
        content_type = app_group.attrib.get("content-type")
        label, title, label_title_raw = cls._get_label_and_title(app_group)
        content_raw = cls._get_raw_content(app_group)
        appendixes = [
            Appendix.from_xml_element(app_elem) for app_elem in app_group.findall("app")
        ]
        return cls(
            sec_type=content_type,
            label=label,
            title=title,
            label_title_raw=label_title_raw,
            content_raw=content_raw,
            appendixes=appendixes,
        )

    @classmethod
    def from_plone(cls, plone_app_group: Any) -> AppendixGroup:
        """Construct an AppendixGroup from a Plone AppendixGroup object.

        Args:
            plone_app_group: A Plone AppendixGroup object.

        Returns:
            An AppendixGroup instance.
        """
        if getattr(plone_app_group, "portal_type", None) != "AppendixGroup":
            raise ValueError("Provided object is not an AppendixGroup")
        content_type = getattr(plone_app_group, "sec_type", None)
        label = getattr(plone_app_group, "label", None)
        title = getattr(plone_app_group, "title", None)
        label_title_raw = getattr(plone_app_group, "label_title_raw", "")
        content_raw = getattr(plone_app_group, "content_raw", None)
        appendixes = []
        for app in plone_app_group.restrictedTraverse("contentlisting")():
            app = app.getObject()
            if getattr(app, "portal_type", None) == "Appendix":
                appendixes.append(Appendix.from_plone(app))
        return cls(
            sec_type=content_type,
            label=label,
            title=title,
            label_title_raw=label_title_raw,
            content_raw=content_raw,
            appendixes=appendixes,
        )
