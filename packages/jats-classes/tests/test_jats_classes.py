import os
import tempfile

import pytest
from jats_classes import (
    Appendix,
    AppendixGroup,
    Article,
    Back,
    Body,
    Front,
    GenericSection,
    JATSDocument,
    Section,
)
from lxml import etree

# ----------------------------------------------------
# XML Snippets for testing
# ----------------------------------------------------

VALID_JATS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" article-type="research-article">
    <front>
        <journal-meta>
            <journal-id/>
            <issn/>
        </journal-meta>
        <article-meta>
            <title-group>
                <article-title>My Test JATS Article</article-title>
            </title-group>
        </article-meta>
    </front>
    <body>
        <sec sec-type="intro">
            <label>1.</label>
            <title>Introduction</title>
            <p>This is the first paragraph.</p>
            <sec sec-type="subsection">
                <label>1.1</label>
                <title>Nested Subsection</title>
                <p>Nested content.</p>
            </sec>
        </sec>
    </body>
    <back>
        <app-group content-type="appendices">
            <label>Appendix Group Label</label>
            <title>Appendix Group Title</title>
            <app app-type="annex">
                <label>A</label>
                <title>First Appendix</title>
                <p>Appendix text content.</p>
                <sec>
                    <title>Appendix Subsection</title>
                    <p>Subtext.</p>
                </sec>
            </app>
        </app-group>
    </back>
</article>
"""


# ----------------------------------------------------
# Tests for Body & Sections
# ----------------------------------------------------


def test_body_and_sections_recursive():
    doc = JATSDocument.from_xml(VALID_JATS_XML, xsd_path=None)
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
    assert "This is the first paragraph." in sec.content_raw

    # Check subsection
    assert len(sec.sections) == 1
    sub_sec = sec.sections[0]
    assert isinstance(sub_sec, Section)
    assert sub_sec.sec_type == "subsection"
    assert sub_sec.label == "1.1"
    assert sub_sec.title == "Nested Subsection"
    assert "Nested content." in sub_sec.content_raw


# ----------------------------------------------------
# Tests for Back, AppendixGroups, Appendices
# ----------------------------------------------------


def test_back_appendix_parsing():
    doc = JATSDocument.from_xml(VALID_JATS_XML, xsd_path=None)
    back = doc.article.back
    assert isinstance(back, Back)
    assert len(back.appendix_groups) == 1

    app_group = back.appendix_groups[0]
    assert isinstance(app_group, AppendixGroup)
    assert app_group.sec_type == "appendices"  # maps to content-type attribute
    assert app_group.label == "Appendix Group Label"
    assert app_group.title == "Appendix Group Title"

    assert len(app_group.appendixes) == 1
    app = app_group.appendixes[0]
    assert isinstance(app, Appendix)
    assert app.sec_type == "annex"  # maps to app-type attribute
    assert app.label == "A"
    assert app.title == "First Appendix"
    assert "Appendix text content." in app.content_raw

    # Check subsection inside appendix
    assert len(app.sections) == 1
    app_sub_sec = app.sections[0]
    assert isinstance(app_sub_sec, Section)
    assert app_sub_sec.title == "Appendix Subsection"
    assert "Subtext." in app_sub_sec.content_raw


def test_generic_section_content_raw_extraction_edge_cases():
    # Test GenericSection._get_raw_content with comments or non-element nodes
    xml_str = """
    <sec>
        <label>L</label>
        <title>T</title>
        <!-- This is a comment -->
        Text node here
        <p>Another paragraph</p>
    </sec>
    """
    elem = etree.fromstring(xml_str)
    content_raw = GenericSection._get_raw_content(elem)
    assert "Text node here" in content_raw
    assert "<p>Another paragraph</p>" in content_raw
    # Comments shouldn't break parsing
    assert "This is a comment" in content_raw

    # Empty content section should return None
    xml_empty = "<sec><label>L</label><title>T</title></sec>"
    elem_empty = etree.fromstring(xml_empty)
    assert GenericSection._get_raw_content(elem_empty) is None


# ----------------------------------------------------
# Tests for Durchführungsanweisung subsection split
# ----------------------------------------------------


def test_section_split_on_durchfuehrungsanweisung():
    xml_str = """
    <sec>
        <label>1.</label>
        <title>Main Section</title>
        <p>Normal content.</p>
        <p><italic>Durchführungsanweisung</italic> instruction text</p>
        <p>Following content.</p>
    </sec>
    """
    elem = etree.fromstring(xml_str)
    sec = Section.from_xml_element(elem)

    # Main section still has normal content before split point
    assert "Normal content." in sec.content_raw

    # One auto-generated subsection containing split content
    assert len(sec.sections) == 1
    sub = sec.sections[0]
    assert "Durchführungsanweisung" in sub.content_raw
    assert "Following content." in sub.content_raw


def test_section_no_split_without_durchfuehrungsanweisung():
    xml_str = """
    <sec>
        <label>1.</label>
        <title>Main Section</title>
        <p>Some content.</p>
        <p>More content.</p>
    </sec>
    """
    elem = etree.fromstring(xml_str)
    sec = Section.from_xml_element(elem)
    assert len(sec.sections) == 0
    assert "Some content." in sec.content_raw


def test_section_split_ignores_italic_in_nested_sec():
    xml_str = """
    <sec>
        <label>1.</label>
        <title>Main Section</title>
        <p>Intro content.</p>
        <sec>
            <title>Nested</title>
            <p><italic>Durchführungsanweisung</italic> inside nested sec</p>
        </sec>
    </sec>
    """
    elem = etree.fromstring(xml_str)
    sec = Section.from_xml_element(elem)
    # The italic is inside an existing nested sec — no extra split at top level
    assert len(sec.sections) == 1
    assert sec.sections[0].title == "Nested"


# ----------------------------------------------------
# Tests for Vorbemerkungen subsection split
# ----------------------------------------------------


def test_section_no_split_without_vorbemerkungen():
    xml_str = """
    <sec>
        <label>1.</label>
        <title>Main Section</title>
        <p>Some content.</p>
        <p>More content.</p>
    </sec>
    """
    elem = etree.fromstring(xml_str)
    sec = Section.from_xml_element(elem)
    assert len(sec.sections) == 0
    assert "Some content." in sec.content_raw


def test_section_split_ignores_span_in_nested_sec():
    xml_str = """
    <sec>
        <label>1.</label>
        <title>Main Section</title>
        <p>Intro content.</p>
        <sec>
            <title>Nested</title>
            <p><span>Vorbemerkungen</span> inside nested sec</p>
        </sec>
    </sec>
    """
    elem = etree.fromstring(xml_str)
    sec = Section.from_xml_element(elem)
    # The span is inside an existing nested sec — no extra split at top level
    assert len(sec.sections) == 1
    assert sec.sections[0].title == "Nested"


def test_section_no_split_vorbemerkungen_partial_text():
    xml_str = """
    <sec>
        <label>1.</label>
        <title>Main Section</title>
        <p>Normal content.</p>
        <p><span>Vorbemerkungen und mehr</span> extra text</p>
        <p>Following content.</p>
    </sec>
    """
    elem = etree.fromstring(xml_str)
    sec = Section.from_xml_element(elem)
    # Partial text match should not trigger a split
    assert len(sec.sections) == 0
