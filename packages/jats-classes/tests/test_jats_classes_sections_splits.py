from jats_classes import Appendix, AppendixGroup, Back, Body, GenericSection, JATSDocument, Section
from jats_examples.sections_split import (
	SECTION_WITH_CONTENTS,
	SECTION_WITH_DURCHFUEHRUNGSANWEISUNG,
	SECTION_WITH_DURCHFUEHRUNGSANWEISUNG_AS_FIRST_CONTENT,
	SECTION_WITH_DURCHFUEHRUNGSANWEISUNGEN_PLURAL,
	SECTION_WITH_INHALT,
	SECTION_WITH_INHALTSVERZEICHNIS,
	SECTION_WITH_MANUAL_INHALTSVERZEICHNIS,
	SECTION_WITH_NESTED_DURCHFUEHRUNGSANWEISUNG,
	SECTION_WITH_NESTED_VORBEMERKUNGEN,
	SECTION_WITH_NESTED_VORBEMERKUNGEN_NAMED_CONTENT,
	SECTION_WITH_PARTIAL_VORBEMERKUNGEN,
	SECTION_WITH_TABLE_OF_CONTENTS,
	SECTION_WITH_TOC_BY_ID,
	SECTION_WITH_VORBEMERKUNGEN,
	SECTION_WITHOUT_DURCHFUEHRUNGSANWEISUNG,
	SECTION_WITHOUT_TOC_HEADING,
)
from lxml import etree
import pytest


# ----------------------------------------------------
# Tests for Durchführungsanweisung subsection split
# ----------------------------------------------------


def test_section_split_on_durchfuehrungsanweisung():
	elem = etree.fromstring(SECTION_WITH_DURCHFUEHRUNGSANWEISUNG)
	sec = Section.from_xml_element(elem)

	assert sec.content_raw is not None
	assert "Normal content." in sec.content_raw
	assert len(sec.sections) == 1
	sub = sec.sections[0]
	assert sub.content_raw is not None
	assert "Durchführungsanweisung" in sub.content_raw
	assert "Following content." in sub.content_raw


def test_section_no_split_without_durchfuehrungsanweisung():
	elem = etree.fromstring(SECTION_WITHOUT_DURCHFUEHRUNGSANWEISUNG)
	sec = Section.from_xml_element(elem)
	assert len(sec.sections) == 0
	assert sec.content_raw is not None
	assert "Some content." in sec.content_raw


def test_section_split_ignores_italic_in_nested_sec():
	elem = etree.fromstring(SECTION_WITH_NESTED_DURCHFUEHRUNGSANWEISUNG)
	sec = Section.from_xml_element(elem)
	assert len(sec.sections) == 1
	assert sec.sections[0].title == "Nested"


# ----------------------------------------------------
# Tests for Vorbemerkungen subsection split
# ----------------------------------------------------


def test_section_no_split_without_vorbemerkungen():
	elem = etree.fromstring(SECTION_WITHOUT_DURCHFUEHRUNGSANWEISUNG)
	sec = Section.from_xml_element(elem)
	assert len(sec.sections) == 0
	assert sec.content_raw is not None
	assert "Some content." in sec.content_raw


def test_section_split_ignores_span_in_nested_sec():
	elem = etree.fromstring(SECTION_WITH_NESTED_VORBEMERKUNGEN)
	sec = Section.from_xml_element(elem)
	assert len(sec.sections) == 1
	assert sec.sections[0].title == "Nested"


def test_section_no_split_vorbemerkungen_partial_text():
	elem = etree.fromstring(SECTION_WITH_PARTIAL_VORBEMERKUNGEN)
	sec = Section.from_xml_element(elem)
	assert len(sec.sections) == 0


def test_section_split_on_vorbemerkungen_sets_preamble_sec_type():
	"""Regression test: the existing "ignores span in nested sec" tests use
	<span>, which the xpath never matches, so they never actually exercised
	the Vorbemerkungen split. This uses the real <named-content> tag.
	"""
	elem = etree.fromstring(SECTION_WITH_VORBEMERKUNGEN)
	sec = Section.from_xml_element(elem)
	assert sec.sec_type == "preamble"


def test_section_split_on_vorbemerkungen_cascades_into_nested_sections():
	"""Documents current (likely unintended) behavior: unlike
	_split_on_durchfuehrungsanweisung, _apply_section_type_based_on_heading has
	no guard against matching inside an already-nested <sec>, so the "preamble"
	sec-type leaks onto every ancestor section, not just the one that directly
	contains the heading.
	"""
	elem = etree.fromstring(SECTION_WITH_NESTED_VORBEMERKUNGEN_NAMED_CONTENT)
	sec = Section.from_xml_element(elem)
	assert sec.sec_type == "preamble"
	assert len(sec.sections) == 1
	assert sec.sections[0].title == "Nested"
	assert sec.sections[0].sec_type == "preamble"


# ----------------------------------------------------
# Tests for Inhaltsverzeichnis / table-of-contents subsection split
# ----------------------------------------------------


@pytest.mark.parametrize(
	"xml",
	[
		pytest.param(SECTION_WITH_INHALTSVERZEICHNIS, id="Inhaltsverzeichnis"),
		pytest.param(SECTION_WITH_INHALT, id="Inhalt"),
		pytest.param(SECTION_WITH_CONTENTS, id="Contents"),
		pytest.param(SECTION_WITH_TABLE_OF_CONTENTS, id="Table of Contents"),
	],
)
def test_section_split_on_toc_heading_variants(xml):
	elem = etree.fromstring(xml)
	sec = Section.from_xml_element(elem)
	assert sec.sec_type == "toc"


def test_section_split_on_manual_inhaltsverzeichnis_via_nested_bold():
	elem = etree.fromstring(SECTION_WITH_MANUAL_INHALTSVERZEICHNIS)
	sec = Section.from_xml_element(elem)
	assert sec.sec_type == "toc"


def test_section_split_on_toc_by_named_content_id():
	elem = etree.fromstring(SECTION_WITH_TOC_BY_ID)
	sec = Section.from_xml_element(elem)
	assert sec.sec_type == "toc"


def test_section_no_split_without_toc_heading():
	elem = etree.fromstring(SECTION_WITHOUT_TOC_HEADING)
	sec = Section.from_xml_element(elem)
	assert sec.sec_type is None


# ----------------------------------------------------
# Additional Durchführungsanweisung edge cases
# ----------------------------------------------------


def test_section_split_on_durchfuehrungsanweisungen_plural():
	elem = etree.fromstring(SECTION_WITH_DURCHFUEHRUNGSANWEISUNGEN_PLURAL)
	sec = Section.from_xml_element(elem)
	assert len(sec.sections) == 1
	assert sec.sections[0].content_raw is not None
	assert "Durchführungsanweisungen" in sec.sections[0].content_raw


def test_section_no_split_when_durchfuehrungsanweisung_is_first_content():
	elem = etree.fromstring(SECTION_WITH_DURCHFUEHRUNGSANWEISUNG_AS_FIRST_CONTENT)
	sec = Section.from_xml_element(elem)
	assert len(sec.sections) == 0


def test_section_split_durchfuehrungsanweisung_subsection_has_no_title_or_label():
	"""Regression test for the fix that gives the synthetic split-off
	subsection a (dummy) <title>, so accessing .title/.label never raises.
	"""
	elem = etree.fromstring(SECTION_WITH_DURCHFUEHRUNGSANWEISUNG)
	sec = Section.from_xml_element(elem)
	sub = sec.sections[0]
	assert sub.sec_type == "highlight-info"
	assert sub.title is None
	assert sub.label is None
