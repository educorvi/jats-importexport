from lxml import etree

from jats_classes import Back, Glossary, Section, Appendix


EXAMPLE_GLOSSARY_XML = (
    "<glossary><label>Appendix A</label><title>Glossary</title>"
    "<def-list><def-item><term>XML</term><def><p>Markup language.</p></def></def-item></def-list>"
    "</glossary>"
)

EXAMPLE_GLOSSARY_XML_SHORT = "<glossary><title>Terms</title><p>Glossary content.</p></glossary>"


def test_glossary_from_xml_element_extracts_label_title_and_content():
    element = etree.fromstring(EXAMPLE_GLOSSARY_XML)

    glossary = Glossary.from_xml_element(element)

    assert glossary.label == "Appendix A"
    assert glossary.title == "Glossary"
    assert glossary.content_raw is not None
    assert "<term>XML</term>" in glossary.content_raw
    assert glossary.sections == []
    assert glossary.to_xml().replace("\n", "") == EXAMPLE_GLOSSARY_XML


def test_section_from_xml_element_parses_glossary_child():
    string = f"<sec><title>References</title><p>Section content.</p>{EXAMPLE_GLOSSARY_XML_SHORT}</sec>"
    element = etree.fromstring(
        string
    )

    section = Section.from_xml_element(element)

    assert section.content_raw is not None
    assert "Section content." in section.content_raw
    assert len(section.sections) == 1
    glossary = section.sections[0]
    assert isinstance(glossary, Glossary)
    assert glossary.title == "Terms"
    assert glossary.content_raw is not None
    assert "Glossary content." in glossary.content_raw
    assert section.to_xml().replace("\n", "") == string


def test_back_from_xml_element_parses_and_serializes_glossary():
    string = f"<back>{EXAMPLE_GLOSSARY_XML_SHORT}</back>"
    element = etree.fromstring(string)

    back = Back.from_xml_element(element)

    assert len(back.sections) == 1
    glossary = back.sections[0]
    assert isinstance(glossary, Glossary)
    assert glossary.title == "Terms"
    assert back.to_xml().replace("\n", "") == string

def test_appendix_from_xml_element_parses_glossary_child():
    string = f"<app><title>Appendix</title>{EXAMPLE_GLOSSARY_XML_SHORT}</app>"
    element = etree.fromstring(string)

    appendix = Appendix.from_xml_element(element)
    assert len(appendix.sections) == 1
    glossary = appendix.sections[0]
    assert isinstance(glossary, Glossary)
    assert glossary.title == "Terms"
    assert glossary.content_raw is not None
    assert "Glossary content." in glossary.content_raw
    assert appendix.to_xml().replace("\n", "") == string
