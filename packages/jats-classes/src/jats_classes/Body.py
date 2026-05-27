from __future__ import annotations

from typing import Any

from lxml import etree

from .Section import Section


class Body:
    sections: list[Section]

    def __init__(self, sections: list[Section]):
        self.sections = sections

    @classmethod
    def from_xml_element(cls, body: etree._Element) -> Body:
        sections = [
            Section.from_xml_element(sec_elem) for sec_elem in body.findall("sec")
        ]
        return cls(sections=sections)

    @classmethod
    def from_plone(cls, plone_body: Any) -> Body:
        if getattr(plone_body, "portal_type", None) != "Body":
            raise ValueError("Provided object is not a Body")
        sections = []
        for sec in plone_body.restrictedTraverse("contentlisting")():
            sec = sec.getObject()
            if getattr(sec, "portal_type", None) == "Section":
                sections.append(Section.from_plone(sec))
        return cls(sections=sections)
