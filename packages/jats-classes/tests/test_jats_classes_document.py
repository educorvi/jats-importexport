from pathlib import Path

import pytest
import jats_classes
import xmlschema
from jats_classes import JATSDocument
from jats_examples.base import MINIMAL_VALID_JATS, VALID_JATS_WITH_BACK
from jats_examples.invalid_structure import INVALID_STRUCTURE_LIST
from lxml.etree import XMLSyntaxError

XSD_PATH = str(Path(jats_classes.__file__).parent / "schema" / "dguv_jats.xsd")
XML_SCHEMA = xmlschema.XMLSchema(XSD_PATH)


# --------------------------------------------------
# Positive tests
# --------------------------------------------------


def test_jats_document_from_xml_minimal_valid():
    doc = JATSDocument.from_xml(MINIMAL_VALID_JATS, xsd_path=None)
    assert isinstance(doc, JATSDocument)
    assert doc.article.front.title == "Minimal Valid JATS Article"

    doc = JATSDocument.from_xml_with_parsed_schema(MINIMAL_VALID_JATS, xml_schema=XML_SCHEMA)
    assert isinstance(doc, JATSDocument)
    assert doc.article.front.title == "Minimal Valid JATS Article"


def test_jats_document_from_xml_valid_with_back():
    doc = JATSDocument.from_xml(VALID_JATS_WITH_BACK, xsd_path=None)
    assert isinstance(doc, JATSDocument)
    assert doc.article.front.title == "Minimal Valid JATS Article"

    doc = JATSDocument.from_xml_with_parsed_schema(VALID_JATS_WITH_BACK, xml_schema=XML_SCHEMA)
    assert isinstance(doc, JATSDocument)
    assert doc.article.front.title == "Minimal Valid JATS Article"


def test_jats_document_constructor_defaults():
    doc = JATSDocument.from_xml(MINIMAL_VALID_JATS, xsd_path=None)

    assert doc.related_articles == []
    assert doc.related_articles_translations == []


def test_jats_document_constructor_accepts_related_articles():
    article = JATSDocument.from_xml(MINIMAL_VALID_JATS, xsd_path=None).article
    related_articles = [("related/article/path", "http://localhost/related/article/url", article.front)]
    related_articles_translations = [("translated/article/path", "http://localhost/translated/article/url", article.front)]

    doc = JATSDocument(
        article=article,
        related_articles=related_articles,
        related_articles_translations=related_articles_translations,
    )

    assert doc.related_articles == related_articles
    assert doc.related_articles_translations == related_articles_translations


def test_jats_document_set_related_articles():
    doc = JATSDocument.from_xml(MINIMAL_VALID_JATS, xsd_path=None)
    related_articles = [("related/article/path", "http://localhost/related/article/url", doc.article.front)]

    doc.set_related_articles(related_articles)

    assert doc.related_articles == related_articles


def test_jats_document_set_related_articles_translations():
    doc = JATSDocument.from_xml(MINIMAL_VALID_JATS, xsd_path=None)
    related_articles_translations = [("translated/article/path", "http://localhost/translated/article/url", doc.article.front)]

    doc.set_related_articles_translations(related_articles_translations)

    assert doc.related_articles_translations == related_articles_translations


# --------------------------------------------------
# Negative tests
# --------------------------------------------------


def test_jats_document_from_xml_invalid_structure():
    for invalid_xml in INVALID_STRUCTURE_LIST:
        with pytest.raises(ValueError):
            JATSDocument.from_xml(invalid_xml, xsd_path=None)

    for invalid_xml in INVALID_STRUCTURE_LIST:
        with pytest.raises(ValueError):
            JATSDocument.from_xml_with_parsed_schema(invalid_xml, xml_schema=XML_SCHEMA)


@pytest.mark.parametrize("xml_content", ["", "<article>"])
def test_jats_document_from_xml_malformed_or_empty(xml_content):
    with pytest.raises(XMLSyntaxError):
        JATSDocument.from_xml(xml_content, xsd_path=None)


def test_jats_document_from_xml_xsd_not_found():
    with pytest.raises(FileNotFoundError, match="XSD file not found"):
        JATSDocument.from_xml(MINIMAL_VALID_JATS, xsd_path="nonexistent_file.xsd")
