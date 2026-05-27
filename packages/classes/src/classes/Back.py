from __future__ import annotations

from typing import Any

from lxml import etree

from .AppendixGroup import AppendixGroup


class Back:
    appendix_groups: list[AppendixGroup]

    def __init__(self, appendix_groups: list[AppendixGroup]):
        self.appendix_groups = appendix_groups

    @classmethod
    def from_xml_element(cls, element: etree._Element) -> Back:
        appendix_groups = [
            AppendixGroup.from_xml_element(app_group)
            for app_group in element.findall("app-group")
        ]
        return cls(appendix_groups=appendix_groups)

    @classmethod
    def from_plone(cls, plone_back: Any) -> Back:
        if getattr(plone_back, "portal_type", None) != "Back":
            raise ValueError("Provided object is not a Back")
        appendix_groups = []
        for app_group in plone_back.restrictedTraverse("contentlisting")():
            app_group = app_group.getObject()
            if getattr(app_group, "portal_type", None) == "AppendixGroup":
                appendix_groups.append(AppendixGroup.from_plone(app_group))
        return cls(appendix_groups=appendix_groups)
