from pathlib import Path

import jats_classes
import pytest
import xmlschema
from jats_classes import Appendix, AppendixGroup, Back, Body, GenericSection, JATSDocument, Section
from jats_examples.sections import (
	APP_GROUP_MULTIPLE_APPENDIXES,
	APP_GROUP_WITHOUT_OPTIONAL_ATTRIBUTES,
	BACK_MULTIPLE_APPENDIX_GROUPS,
	BACK_NO_APP_GROUP,
	BODY_WITHOUT_STRAY_CONTENT,
	BODY_WITH_STRAY_CONTENT,
	EMPTY_SECTION,
	INVALID_DOC_REF_LIST_BEFORE_SEC,
	INVALID_DOC_SEC_MISSING_TITLE_AND_LABEL,
	INVALID_SEC_MISSING_TITLE_AND_LABEL,
	SCHEMA_VALID_SECTION_DOCUMENT,
	SECTION_DOCUMENT,
	SECTION_EMPTY_TITLE,
	SECTION_LABEL_ONLY,
	SECTION_TITLE_ONLY,
	SECTION_TITLE_WITH_BOLD,
	SECTION_TITLE_WITH_NAMED_CONTENT,
	SECTION_WITH_CONTENT_AFTER_NESTED_SEC,
	SECTION_WITH_RAW_CONTENT,
)
from lxml import etree

XSD_PATH = str(Path(jats_classes.__file__).parent / "schema" / "dguv_jats.xsd")
XML_SCHEMA = xmlschema.XMLSchema(XSD_PATH)


# --------------------------------------------------
# Positive tests
# --------------------------------------------------


def test_body_and_sections_recursive():
	doc = JATSDocument.from_xml(SECTION_DOCUMENT, xsd_path=None)
	body = doc.article.body
	assert isinstance(body, Body)
	assert len(body.sections) == 1

	sec = body.sections[0]
	assert isinstance(sec, Section)
	assert sec.sec_type == "intro"
	assert sec.label == "1."
	assert sec.title == "Introduction"
	assert "1." in sec.label_title_raw
	assert "Introduction" in sec.label_title_raw
	assert sec.content_raw is not None
	assert "This is the first paragraph." in sec.content_raw

	# Check subsection
	assert len(sec.sections) == 1
	sub_sec = sec.sections[0]
	assert isinstance(sub_sec, Section)
	assert sub_sec.sec_type == "subsection"
	assert sub_sec.label == "1.1"
	assert sub_sec.title == "Nested Subsection"
	assert sub_sec.content_raw is not None
	assert "Nested content." in sub_sec.content_raw


def test_back_appendix_parsing():
	doc = JATSDocument.from_xml(SECTION_DOCUMENT, xsd_path=None)
	back = doc.article.back
	assert isinstance(back, Back)
	assert len(back.appendix_groups) == 1

	app_group = back.appendix_groups[0]
	assert isinstance(app_group, AppendixGroup)
	assert app_group.sec_type == "appendices"  # maps to content-type attribute
	assert app_group.label == "Appendix Group Label"
	assert app_group.title == "Appendix Group Title"

	assert len(app_group.sections) == 1
	app = app_group.sections[0]
	assert isinstance(app, Appendix)
	assert app.sec_type == "annex"  # maps to app-type attribute
	assert app.label == "A"
	assert app.title == "First Appendix"
	assert app.content_raw is not None
	assert "Appendix text content." in app.content_raw

	# Check subsection inside appendix
	assert len(app.sections) == 1
	app_sub_sec = app.sections[0]
	assert isinstance(app_sub_sec, Section)
	assert app_sub_sec.title == "Appendix Subsection"
	assert app_sub_sec.content_raw is not None
	assert "Subtext." in app_sub_sec.content_raw


def test_generic_section_content_raw_extraction_edge_cases():
	elem = etree.fromstring(SECTION_WITH_RAW_CONTENT)
	content_raw = GenericSection._get_raw_content(elem)
	assert content_raw is not None
	assert "Text node here" in content_raw
	assert "<p>Another paragraph</p>" in content_raw
	assert "This is a comment" in content_raw

	elem_empty = etree.fromstring(EMPTY_SECTION)
	assert GenericSection._get_raw_content(elem_empty) is None


def test_section_label_only_has_no_title():
	elem = etree.fromstring(SECTION_LABEL_ONLY)
	sec = Section.from_xml_element(elem)
	assert sec.label == "2."
	assert sec.title is None
	assert sec.content_raw is not None
	assert "Content with a label but no title." in sec.content_raw


def test_section_title_only_has_no_label():
	elem = etree.fromstring(SECTION_TITLE_ONLY)
	sec = Section.from_xml_element(elem)
	assert sec.title == "Title Only Section"
	assert sec.label is None


def test_section_empty_title_resolves_to_none():
	elem = etree.fromstring(SECTION_EMPTY_TITLE)
	sec = Section.from_xml_element(elem)
	assert sec.title is None


def test_section_content_raw_stops_before_nested_sec():
	elem = etree.fromstring(SECTION_WITH_CONTENT_AFTER_NESTED_SEC)
	sec = Section.from_xml_element(elem)
	assert sec.content_raw is not None
	assert "Before nested section." in sec.content_raw
	assert "Nested content." not in sec.content_raw
	assert len(sec.sections) == 1
	assert sec.sections[0].content_raw is not None
	assert "Nested content." in sec.sections[0].content_raw


def test_section_title_resolves_named_content_but_drops_other_tags():
	elem = etree.fromstring(SECTION_TITLE_WITH_NAMED_CONTENT)
	sec = Section.from_xml_element(elem)
	assert sec.title == "Intro Term tail"

	# Non-phrase-content tags such as <bold> are not recursed into: only
	# their tail text survives, the inner text itself is dropped.
	elem_bold = etree.fromstring(SECTION_TITLE_WITH_BOLD)
	sec_bold = Section.from_xml_element(elem_bold)
	assert sec_bold.title == "Intro  tail"
	assert "Bold" not in sec_bold.title


def test_body_moves_stray_content_into_leading_section():
	body_elem = etree.fromstring(f"<body>{BODY_WITH_STRAY_CONTENT}</body>")
	body = Body.from_xml_element(body_elem)
	assert len(body.sections) == 2

	stray_section = body.sections[0]
	assert stray_section.sec_type is None
	assert stray_section.title is None
	assert stray_section.content_raw is not None
	assert "Stray paragraph before any section." in stray_section.content_raw

	real_section = body.sections[1]
	assert real_section.title == "Real Section"


def test_body_without_stray_content_has_no_extra_section():
	body_elem = etree.fromstring(f"<body>{BODY_WITHOUT_STRAY_CONTENT}</body>")
	body = Body.from_xml_element(body_elem)
	assert len(body.sections) == 1
	assert body.sections[0].title == "Only Section"


def test_back_without_app_group_has_no_appendix_groups():
	back_elem = etree.fromstring(f"<back>{BACK_NO_APP_GROUP}</back>")
	back = Back.from_xml_element(back_elem)
	assert back.appendix_groups == []


def test_back_multiple_appendix_groups():
	back_elem = etree.fromstring(f"<back>{BACK_MULTIPLE_APPENDIX_GROUPS}</back>")
	back = Back.from_xml_element(back_elem)
	assert len(back.appendix_groups) == 2
	assert back.appendix_groups[0].title == "First Group"
	assert back.appendix_groups[1].title == "Second Group"
	assert back.appendix_groups[0].sections[0].title == "First Group Appendix"
	assert back.appendix_groups[1].sections[0].title == "Second Group Appendix"


def test_appendix_group_with_multiple_appendixes():
	elem = etree.fromstring(APP_GROUP_MULTIPLE_APPENDIXES)
	app_group = AppendixGroup.from_xml_element(elem)
	assert len(app_group.sections) == 2
	assert [a.label for a in app_group.sections] == ["A", "B"]
	assert [a.title for a in app_group.sections] == ["Appendix A", "Appendix B"]


def test_appendix_group_without_content_type_has_none_sec_type():
	elem = etree.fromstring(APP_GROUP_WITHOUT_OPTIONAL_ATTRIBUTES)
	app_group = AppendixGroup.from_xml_element(elem)
	assert app_group.sec_type is None


def test_appendix_without_app_type_has_none_sec_type():
	elem = etree.fromstring(APP_GROUP_WITHOUT_OPTIONAL_ATTRIBUTES)
	app_group = AppendixGroup.from_xml_element(elem)
	assert app_group.sections[0].sec_type is None


# --------------------------------------------------
# Negative tests
# --------------------------------------------------


def test_generic_section_get_title_returns_none_for_malformed_raw_xml():
	section = Section(sec_type=None, label_title_raw="<title>Unclosed", content_raw=None, sections=[])
	assert section.title is None


def test_generic_section_get_label_returns_none_for_malformed_raw_xml():
	section = Section(sec_type=None, label_title_raw="<label>Unclosed", content_raw=None, sections=[])
	assert section.label is None


def test_generic_section_get_title_returns_none_when_title_missing():
	section = Section(sec_type=None, label_title_raw="<label>1.</label>", content_raw=None, sections=[])
	assert section.title is None


def test_section_missing_title_and_label_parses_but_has_no_metadata():
	elem = etree.fromstring(INVALID_SEC_MISSING_TITLE_AND_LABEL)
	sec = Section.from_xml_element(elem)
	assert sec.title is None
	assert sec.label is None
	assert sec.content_raw is not None
	assert "Content without any title or label." in sec.content_raw


def test_jats_document_rejects_sec_missing_title_and_label_against_schema():
	with pytest.raises(ValueError):
		JATSDocument.from_xml(INVALID_DOC_SEC_MISSING_TITLE_AND_LABEL, xsd_path=XSD_PATH)

	with pytest.raises(ValueError):
		JATSDocument.from_xml_with_parsed_schema(INVALID_DOC_SEC_MISSING_TITLE_AND_LABEL, xml_schema=XML_SCHEMA)


def test_jats_document_rejects_ref_list_before_nested_sec_against_schema():
	with pytest.raises(ValueError):
		JATSDocument.from_xml(INVALID_DOC_REF_LIST_BEFORE_SEC, xsd_path=XSD_PATH)

	with pytest.raises(ValueError):
		JATSDocument.from_xml_with_parsed_schema(INVALID_DOC_REF_LIST_BEFORE_SEC, xml_schema=XML_SCHEMA)


def test_jats_document_accepts_section_document_against_schema():
	doc = JATSDocument.from_xml(SCHEMA_VALID_SECTION_DOCUMENT, xsd_path=XSD_PATH)
	assert doc.article.body.sections[0].title == "Introduction"
	assert doc.article.back is not None
	assert doc.article.back.appendix_groups[0].sections[0].title == "First Appendix"
