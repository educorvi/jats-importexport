from lxml import etree

from jats_classes import Back, RefList, Section, Appendix, AppendixGroup


EXAMPLE_REFLIST_XML = (
    "<ref-list><label>Appendix A</label><title>RefList</title>"
    "<def-list><def-item><term>XML</term><def><p>Markup language.</p></def></def-item></def-list>"
    "</ref-list>"
)

EXAMPLE_REFLIST_XML_SHORT = "<ref-list><title>Terms</title><p>RefList content.</p></ref-list>"


def test_reflist_from_xml_element_extracts_label_title_and_content():
    element = etree.fromstring(EXAMPLE_REFLIST_XML)

    reflist = RefList.from_xml_element(element)

    assert reflist.label == "Appendix A"
    assert reflist.title == "RefList"
    assert reflist.content_raw is not None
    assert "<term>XML</term>" in reflist.content_raw
    assert reflist.sections == []
    assert reflist.to_xml().replace("\n", "") == EXAMPLE_REFLIST_XML


def test_section_from_xml_element_parses_reflist_child():
    string = f"<sec><title>References</title><p>Section content.</p>{EXAMPLE_REFLIST_XML_SHORT}</sec>"
    element = etree.fromstring(
        string
    )

    section = Section.from_xml_element(element)

    assert section.content_raw is not None
    assert "Section content." in section.content_raw
    assert len(section.sections) == 1
    reflist = section.sections[0]
    assert isinstance(reflist, RefList)
    assert reflist.title == "Terms"
    assert reflist.content_raw is not None
    assert "RefList content." in reflist.content_raw
    assert section.to_xml().replace("\n", "") == string


def test_back_from_xml_element_parses_and_serializes_reflist():
    string = f"<back>{EXAMPLE_REFLIST_XML_SHORT}</back>"
    element = etree.fromstring(string)

    back = Back.from_xml_element(element)

    assert len(back.sections) == 1
    reflist = back.sections[0]
    assert isinstance(reflist, RefList)
    assert reflist.title == "Terms"
    assert back.to_xml().replace("\n", "") == string

def test_appendix_from_xml_element_parses_reflist_child():
    string = f"<app><title>Appendix</title>{EXAMPLE_REFLIST_XML_SHORT}</app>"
    element = etree.fromstring(string)

    appendix = Appendix.from_xml_element(element)
    assert len(appendix.sections) == 1
    reflist = appendix.sections[0]
    assert isinstance(reflist, RefList)
    assert reflist.title == "Terms"
    assert reflist.content_raw is not None
    assert "RefList content." in reflist.content_raw
    assert appendix.to_xml().replace("\n", "") == string

def test_appgroup_from_xml_element_parses_reflist_child():
    string = f"<app-group><title>Appendix Group</title>{EXAMPLE_REFLIST_XML_SHORT}</app-group>"
    element = etree.fromstring(string)

    appgroup = AppendixGroup.from_xml_element(element)
    assert len(appgroup.sections) == 1
    reflist = appgroup.sections[0]
    assert isinstance(reflist, RefList)
    assert reflist.title == "Terms"
    assert reflist.content_raw is not None
    assert "RefList content." in reflist.content_raw
    assert appgroup.to_xml().replace("\n", "") == string

def test_reflist_in_reflist():
    string = f"<ref-list>{EXAMPLE_REFLIST_XML_SHORT}</ref-list>"
    element = etree.fromstring(string)

    reflist = RefList.from_xml_element(element)
    assert len(reflist.sections) == 0
    assert reflist.content_raw is not None
    assert reflist.content_raw == EXAMPLE_REFLIST_XML_SHORT
    assert reflist.to_xml().replace("\n", "") == string
