from __future__ import annotations

from typing import Any

from lxml import etree

from .GenericSection import GenericSection
from .Section import Section


class Appendix(GenericSection):
    sections: list[Section]

    def __init__(
        self,
        sec_type: str | None,
        label: str | None,
        title: str | None,
        label_title_raw: str,
        content_raw: str | None,
        sections: list[Section],
    ):
        super().__init__(
            sec_type=sec_type,
            label=label,
            title=title,
            label_title_raw=label_title_raw,
            content_raw=content_raw,
        )
        self.sections = sections

    @classmethod
    def from_xml_element(cls, app: etree._Element) -> Appendix:
        app_type = app.attrib.get("app-type")
        label, title, label_title_raw = cls._get_label_and_title(app)
        content_raw = cls._get_raw_content(app)
        sections = [
            Section.from_xml_element(sec_elem) for sec_elem in app.findall("sec")
        ]
        return cls(
            sec_type=app_type,
            label=label,
            title=title,
            label_title_raw=label_title_raw,
            content_raw=content_raw,
            sections=sections,
        )

    @classmethod
    def from_plone(cls, plone_appendix: Any) -> Appendix:
        if getattr(plone_appendix, "portal_type", None) != "Appendix":
            raise ValueError("Provided object is not an Appendix")
        app_type = getattr(plone_appendix, "sec_type", None)
        label = getattr(plone_appendix, "label", None)
        title = getattr(plone_appendix, "title", None)
        label_title_raw = getattr(plone_appendix, "label_title_raw", "")
        content_raw = getattr(plone_appendix, "content_raw", None)
        sections = []
        for sec in plone_appendix.restrictedTraverse("contentlisting")():
            sec = sec.getObject()
            if getattr(sec, "portal_type", None) == "Section":
                sections.append(Section.from_plone(sec))
        return cls(
            sec_type=app_type,
            label=label,
            title=title,
            label_title_raw=label_title_raw,
            content_raw=content_raw,
            sections=sections,
        )
