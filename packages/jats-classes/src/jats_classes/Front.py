from __future__ import annotations

from typing import Any

from lxml import etree


class Front:
    content_raw: str | None

    def __init__(self, content_raw: str | None):
        self.content_raw = content_raw

    @classmethod
    def from_xml_element(cls, element: etree._Element) -> Front:
        content_raw = cls._get_raw_content(element)
        return cls(content_raw=content_raw)

    @classmethod
    def from_plone(cls, plone_front: Any) -> Front:
        if getattr(plone_front, "portal_type", None) != "Front":
            raise ValueError("Provided object is not a Front")
        content_raw = getattr(plone_front, "content_raw", None)
        return cls(content_raw=content_raw)

    @classmethod
    def _get_raw_content(cls, front: etree._Element) -> str | None:
        result = ""
        for elem in front:
            result += etree.tostring(elem, encoding="unicode")
        if result == "":
            return None
        return result
