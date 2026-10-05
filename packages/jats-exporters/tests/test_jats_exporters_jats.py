"""Tests for JatsExporter: serializing JATSDocument models back to JATS XML.

Covers structural correctness of the generated XML as well as validation against
the real DGUV JATS XSD schema. The XSD is parsed once at module scope since
parsing is expensive and the schema itself never changes between tests.
"""

from pathlib import Path

import jats_classes
import xmlschema
from jats_classes import Back
from jats_examples.jats_export_cases import (
    complete_front,
    empty_front,
    front_with_pub_date,
    make_appendix,
    make_appendix_group,
    make_document,
    make_section,
)
from jats_exporters import JatsExporter
from jats_exporters.jats import _get_general_section_jats
from lxml import etree

XSD_PATH = str(Path(jats_classes.__file__).parent / "schema" / "dguv_jats.xsd")
XML_SCHEMA = xmlschema.XMLSchema(XSD_PATH)


def schema_errors(xml: str) -> list[str]:
    """Return human readable XSD validation errors for the given XML string."""
    return [f"{error.path or '/'}: {error.reason}" for error in XML_SCHEMA.iter_errors(xml)]


# ----------------------------------------------------
# Positive tests: structure of the generated <article> wrapper
# ----------------------------------------------------


def test_export_wraps_content_in_article_with_doctype_and_attributes():
    doc = make_document(front=front_with_pub_date())
    xml = JatsExporter().export(doc)

    assert "<!DOCTYPE article PUBLIC" in xml
    assert 'article-type="DGUV Vorschriften- und Regelwerk"' in xml
    assert 'dtd-version="1.1"' in xml
    assert 'xml:lang="de"' in xml
    assert xml.strip().endswith("</article>")


def test_export_uses_front_xml_lang_attribute():
    doc = make_document(front=front_with_pub_date(xml_lang="en"))
    xml = JatsExporter().export(doc)

    assert 'xml:lang="en"' in xml


def test_export_defaults_to_german_when_xml_lang_not_set():
    front = empty_front()
    front.xml_lang = None  # type: ignore[assignment]
    doc = make_document(front=front)
    xml = JatsExporter().export(doc)

    assert 'xml:lang="de"' in xml


def test_export_body_is_wrapped_in_body_tag():
    section = make_section(title="Only section")
    doc = make_document(front=front_with_pub_date(), sections=[section])
    xml = JatsExporter().export(doc)

    assert "<body>" in xml
    assert "Only section" in xml


def test_export_back_omitted_entirely_when_none():
    doc = make_document(front=front_with_pub_date(), back=None)
    xml = JatsExporter().export(doc)

    assert "<back>" not in xml
    assert "<back/>" not in xml


def test_export_back_rendered_when_present():
    back = Back(appendix_groups=[make_appendix_group()])
    doc = make_document(front=front_with_pub_date(), back=back)
    xml = JatsExporter().export(doc)

    assert "<back>" in xml
    assert "Appendix group title" in xml


# ----------------------------------------------------
# Positive tests: section / appendix serialization
# ----------------------------------------------------


def test_export_section_includes_label_title_and_content():
    section = make_section(title="Intro", label="1.", content="<p>Body text.</p>")
    xml = _get_general_section_jats(section)

    assert xml.startswith("<sec")
    assert "<label>1.</label>" in xml
    assert "<title>Intro</title>" in xml
    assert "<p>Body text.</p>" in xml
    assert xml.endswith("</sec>")


def test_export_section_sec_type_attribute_rendered():
    section = make_section(sec_type="intro")
    xml = _get_general_section_jats(section)

    assert '<sec sec-type="intro">' in xml


def test_export_section_without_sec_type_omits_attribute():
    section = make_section(sec_type=None)
    xml = _get_general_section_jats(section)

    assert xml.startswith("<sec>")


def test_export_nested_sections_are_recursively_serialized():
    sub = make_section(title="Sub section")
    main = make_section(title="Main section", sections=[sub])
    xml = _get_general_section_jats(main)

    # nested <sec> must be inside the parent, after the parent's own content
    assert xml.count("<sec") == 2
    assert xml.index("Main section") < xml.index("Sub section")


def test_export_appendix_group_and_appendix_use_expected_tags():
    group = make_appendix_group(sec_type="appendices", appendixes=[make_appendix()])
    xml = _get_general_section_jats(group)

    assert xml.startswith('<app-group content-type="appendices">')
    assert "<app" in xml
    assert xml.endswith("</app-group>")


def test_export_appendix_group_with_multiple_appendixes():
    appendixes = [make_appendix(title="First"), make_appendix(title="Second")]
    group = make_appendix_group(appendixes=appendixes)
    xml = _get_general_section_jats(group)

    assert xml.count("<app>") == 2
    assert "First" in xml
    assert "Second" in xml


def test_export_raises_for_unsupported_section_type():
    class NotASection:
        sec_type = None

    try:
        _get_general_section_jats(NotASection())  # type: ignore[arg-type]
        raise AssertionError("expected ValueError for unsupported section type")
    except ValueError as error:
        assert "Unsupported section type" in str(error)


# ----------------------------------------------------
# Positive tests: caching behaviour
# ----------------------------------------------------


def test_export_caches_by_document_identity():
    exporter = JatsExporter()
    exporter.export.cache_clear()

    doc_a = make_document(front=front_with_pub_date())
    doc_b = make_document(front=front_with_pub_date())

    exporter.export(doc_a)
    exporter.export(doc_a)
    exporter.export(doc_b)

    info = exporter.export.cache_info()
    # doc_a and doc_b are different instances -> two cache misses, one hit for doc_a
    assert info.misses == 2
    assert info.hits == 1


# ----------------------------------------------------
# Schema validation tests (bug-hunting): validate exporter output against the
# real DGUV JATS XSD. It is expected/acceptable that some of these fail -
# that is the point of validating against the schema.
# ----------------------------------------------------


def test_export_of_complete_document_is_schema_valid():
    section = make_section(title="Intro", sec_type="intro", label="1.")
    back = Back(appendix_groups=[make_appendix_group(sec_type="appendices", appendixes=[make_appendix(sec_type=None)])])
    doc = make_document(front=complete_front(), sections=[section], back=back)

    xml = JatsExporter().export(doc)

    assert schema_errors(xml) == []


def test_export_of_empty_front_without_pub_date_is_not_schema_valid():
    """`Front.empty()` leaves pub-date fields unset, but the exporter still emits
    an empty <day> element for the required "Ausgabedatum" pub-date. The XSD
    requires <day> to contain a valid day-of-month value, so this is a real bug:
    documents built from an incomplete Front will fail schema validation.
    """
    doc = make_document(front=empty_front())
    xml = JatsExporter().export(doc)

    errors = schema_errors(xml)
    assert any("pub-date/day" in error for error in errors)


def test_export_of_appendix_with_sec_type_is_not_schema_valid():
    """The exporter writes the `sec_type` of an `Appendix` as an `app-type`
    attribute on <app>, but the DGUV schema only defines `content-type` for
    <app> (mirroring the `AppendixGroup`/`Section` attribute names is wrong).
    """
    appendix = make_appendix(sec_type="annex")
    group = make_appendix_group(appendixes=[appendix])
    back = Back(appendix_groups=[group])
    doc = make_document(front=complete_front(), back=back)

    xml = JatsExporter().export(doc)

    errors = schema_errors(xml)
    assert any("app-type" in error for error in errors)


def test_export_appendix_without_sec_type_is_schema_valid():
    """Without a sec_type, no (wrong) attribute is emitted, so this variant is fine."""
    appendix = make_appendix(sec_type=None)
    group = make_appendix_group(appendixes=[appendix])
    back = Back(appendix_groups=[group])
    doc = make_document(front=complete_front(), back=back)

    xml = JatsExporter().export(doc)

    assert schema_errors(xml) == []


# ----------------------------------------------------
# Negative tests: malformed input content
# ----------------------------------------------------


def test_export_does_not_escape_raw_content_special_characters():
    """`label_title_raw`/`content_raw` are embedded verbatim. If they contain an
    unescaped "&" (e.g. from a source that isn't already XML-escaped), the
    resulting document is not well-formed XML at all - the exporter performs no
    escaping/sanitization of raw string content.
    """
    section = make_section(title="Cats & Dogs")
    doc = make_document(front=front_with_pub_date(), sections=[section])
    xml = JatsExporter().export(doc)

    try:
        etree.fromstring(xml.encode("utf-8"))
        raise AssertionError("expected the unescaped '&' to break XML well-formedness")
    except etree.XMLSyntaxError:
        pass
