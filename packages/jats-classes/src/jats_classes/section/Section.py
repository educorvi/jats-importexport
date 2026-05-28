from __future__ import annotations

from typing import Any

from lxml import etree

from .GenericSection import GenericSection


class Section(GenericSection):

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
    def from_xml_element(cls, section: etree._Element) -> Section:
        sec_type = section.attrib.get("sec-type")
        label, title, label_title_raw = cls._get_label_and_title(section)
        content_raw = cls._get_raw_content(section)
        sections = [
            cls.from_xml_element(sec_elem) for sec_elem in section.findall("sec")
        ]
        return cls(
            sec_type=sec_type,
            label=label,
            title=title,
            label_title_raw=label_title_raw,
            content_raw=content_raw,
            sections=sections,
        )

    @classmethod
    def from_plone(cls, plone_section: Any) -> Section:
        if getattr(plone_section, "portal_type", None) != "Section":
            raise ValueError("Provided object is not a Section")
        sec_type = getattr(plone_section, "sec_type", None)
        label = getattr(plone_section, "label", None)
        title = getattr(plone_section, "title", None)
        label_title_raw = getattr(plone_section, "label_title_raw", "")
        content_raw = getattr(plone_section, "content_raw", None)
        sections = []
        for sec in plone_section.restrictedTraverse("contentlisting")():
            sec = sec.getObject()
            if getattr(sec, "portal_type", None) == "Section":
                sections.append(cls.from_plone(sec))
        return cls(
            sec_type=sec_type,
            label=label,
            title=title,
            label_title_raw=label_title_raw,
            content_raw=content_raw,
            sections=sections,
        )
