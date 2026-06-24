"""JATS Section model.

Defines a basic JATS <sec> (Section) element and its parser/converter logic.
"""

from __future__ import annotations

from lxml import etree

from .GenericSection import GenericSection


class Section(GenericSection):
    """Represents a basic JATS <sec> element which can recursively nest subsections."""

    def __init__(
        self,
        sec_type: str | None,
        label: str | None,
        title: str | None,
        label_title_raw: str,
        content_raw: str | None,
        sections: list[Section],
    ):
        """Initialize Section with type, title, label, contents, and nested sections."""
        super().__init__(
            sec_type=sec_type,
            label=label,
            title=title,
            label_title_raw=label_title_raw,
            content_raw=content_raw,
        )
        self.sections = sections

    @classmethod
    def _split_on_durchfuehrungsanweisung(cls, section: etree._Element) -> None:
        """Split section at italic 'Durchführungsanweisung' into a new subsection.

        If the section contains an <italic> element whose text includes
        "Durchführungsanweisung", the direct-child ancestor of that element
        (within this section) and all its following siblings are moved into a
        newly created <sec> child appended to the section.
        """
        xpath_result = section.xpath('.//italic[contains(.,"Durchführungsanweisung")]')
        if not isinstance(xpath_result, list):
            return
        raw_matches: list[etree._Element] = [e for e in xpath_result if isinstance(e, etree._Element)]
        if not raw_matches:
            return
        italic: etree._Element = raw_matches[0]
        stripped_text = (italic.text or "").strip()
        if stripped_text != "Durchführungsanweisung" and stripped_text != "Durchführungsanweisungen":
            return
        # Walk up to find the direct child of this section.
        node: etree._Element = italic
        while True:
            parent = node.getparent()
            if parent is None or parent is section:
                break
            node = parent
        if node.getparent() is not section or node.tag == "sec":
            return
        split_start = node
        siblings = list(section)
        idx = siblings.index(split_start)
        # Only split if there is actual content before the split point.
        if not any(s.tag not in ("label", "title") for s in siblings[:idx]):
            return
        to_move = siblings[idx:]
        new_sec = etree.Element("sec")
        new_sec.set("sec-type", "highlight-info")
        for elem in to_move:
            section.remove(elem)
            new_sec.append(elem)
        section.append(new_sec)

    @classmethod
    def _split_on_vorbemerkungen(cls, section: etree._Element) -> None:
        """Split section at span 'Vorbemerkungen' into a new subsection.

        If the section contains a <span> element whose text is exactly
        "Vorbemerkungen", the direct-child ancestor of that element
        (within this section) and all its following siblings are moved into a
        newly created <sec> child appended to the section.
        """
        xpath_result = section.xpath('.//named-content[text()="Vorbemerkungen"]')
        if not isinstance(xpath_result, list):
            return
        raw_matches: list[etree._Element] = [e for e in xpath_result if isinstance(e, etree._Element)]
        if not raw_matches:
            return
        span: etree._Element = raw_matches[0]
        # Walk up to find the direct child of this section.
        node: etree._Element = span
        while True:
            parent = node.getparent()
            if parent is None or parent is section:
                break
            node = parent
        if parent:
            parent.set("sec-type", "preamble")

    @classmethod
    def from_xml_element(cls, section: etree._Element) -> Section:
        """Construct a Section from an lxml element representing a JATS <sec> tag.

        Args:
            section: lxml _Element node representing the <sec> tag.

        Returns:
            A Section instance.
        """
        cls._split_on_durchfuehrungsanweisung(section)
        cls._split_on_vorbemerkungen(section)
        sec_type = section.attrib.get("sec-type")
        label, title, label_title_raw = cls._get_label_and_title(section)
        content_raw = cls._get_raw_content(section)
        sections = [cls.from_xml_element(sec_elem) for sec_elem in section.findall("sec")]

        return cls(
            sec_type=sec_type,
            label=label,
            title=title,
            label_title_raw=label_title_raw,
            content_raw=content_raw,
            sections=sections,
        )
