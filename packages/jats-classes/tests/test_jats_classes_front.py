import datetime
from pathlib import Path

import jats_classes
import pytest
from jats_classes import Front, JATSDocument
import xmlschema
from jats_examples.front import (
    ARTICLE_CATEGORIES,
    COMPLETE_FRONT,
    FRONT_WITH_WHITESPACE,
    FRONT_DICT,
    FRONT_MISSING_ARTICLE_META,
    FRONT_MISSING_JOURNAL_META,
    FRONT_WITHOUT_TITLE,
)
from lxml import etree

XSD_PATH = str(Path(jats_classes.__file__).parent / "schema" / "dguv_jats.xsd")
XML_SCHEMA = xmlschema.XMLSchema(XSD_PATH)


# --------------------------------------------------
# Validate complete front
# --------------------------------------------------

def _check_complete_front(front: Front):
    assert front.xml_lang == "de"
    assert front.journal_id == "journal-123"
    assert front.journal_title == "Journal of Testing"
    assert front.journal_subtitle == "Reliable XML"
    assert front.issn == "1234-5678"
    assert front.publisher_name == "Example Publisher"
    assert front.publisher_institution == "Testing Institute"
    assert front.publisher_addr_line == "Example Street 1"
    assert front.publisher_postal_code == "12345"
    assert front.publisher_city == "Test City"
    assert front.publisher_phone == "+49 123 456"
    assert front.publisher_email == "mail@example.test"
    assert front.publisher_uri == "https://example.test"

    assert front.article_id == "article-123"
    assert front.title == "Readable JATS Front"
    assert front.article_subtitle == ["First subtitle", "Second subtitle"]
    assert front.author_surname == "Author"
    assert front.co_author_surname == "Coauthor"
    assert front.co_author_aff == "Testing Department"
    assert front.self_uri == "https://example.test/article-123"
    assert front.article_categories == ARTICLE_CATEGORIES
    assert front.related_articles == ["p234"]
    assert front.related_articles_translations == ["p345"]

    assert front.pub_date_ausgabedatum == datetime.date(2024, 3, 2)
    assert front.pub_date_aktualisierte_fassung == datetime.date(2025, 1, 1)
    assert front.history_initial_publication == "2020"
    assert front.history_correction == "2021"
    assert front.history_latest_version == "2025"
    assert front.copyright_statement == "Copyright Example"
    assert front.copyright_holder == "Example Publisher"

    assert front.abstract_short_title == "Short abstract"
    assert front.abstract_short == "Short summary."
    assert front.abstract_summary_title == "Summary abstract"
    assert front.abstract_summary == "Long summary."
    assert front.subjects == ["XML", "Testing"]

    assert front.beschreibender_typ == "Beispielwert"
    assert front.bisherige_bestellnummer == "12345"
    assert front.webcode == "p123"
    assert front.organisationseinheit == "DGUV"
    assert front.fachbereich == "Fachbereich"
    assert front.sachgebiet == "Sachgebiet"
    assert front.veroeffentlichungsstatus == "veröffentlicht"
    assert front.bildnachweis == "Beispielbildnachweis"
    assert front.ueberschriften_mit_nummerierung is True


def _check_complete_front_xml(xml_element: etree._Element):
    assert xml_element.findtext("journal-meta/journal-id") == "journal-123"
    assert xml_element.findtext("journal-meta/journal-title-group/journal-title") == "Journal of Testing"
    assert xml_element.findtext("journal-meta/journal-title-group/journal-subtitle") == "Reliable XML"
    assert xml_element.findtext("journal-meta/issn") == "1234-5678"
    assert xml_element.findtext("journal-meta/publisher/publisher-name") == "Example Publisher"
    assert xml_element.findtext("journal-meta/publisher/publisher-loc/institution") == "Testing Institute"
    assert xml_element.findtext("journal-meta/publisher/publisher-loc/addr-line") == "Example Street 1"
    assert xml_element.findtext("journal-meta/publisher/publisher-loc/postal-code") == "12345"
    assert xml_element.findtext("journal-meta/publisher/publisher-loc/city") == "Test City"
    assert xml_element.findtext("journal-meta/publisher/publisher-loc/phone") == "+49 123 456"
    assert xml_element.findtext("journal-meta/publisher/publisher-loc/email") == "mail@example.test"
    assert xml_element.findtext("journal-meta/publisher/publisher-loc/uri") == "https://example.test"

    assert xml_element.findtext("article-meta/article-id") == "article-123"
    assert xml_element.findtext("article-meta/title-group/article-title") == "Readable JATS Front"
    assert xml_element.findtext("article-meta/title-group/subtitle[1]") == "First subtitle"
    assert xml_element.findtext("article-meta/title-group/subtitle[2]") == "Second subtitle"
    assert xml_element.findtext("article-meta/contrib-group/contrib[@contrib-type='Autor']/name/surname") == "Author"
    assert xml_element.findtext("article-meta/contrib-group/contrib[@contrib-type='Co-Autor']/name/surname") == "Coauthor"
    assert xml_element.findtext("article-meta/contrib-group/contrib[@contrib-type='Co-Autor']/aff") == "Testing Department"
    assert xml_element.find(f"article-meta/self-uri[@{{{"http://www.w3.org/1999/xlink"}}}href='https://example.test/article-123']") is not None
    assert xml_element.findtext("article-meta/article-categories/subj-group/subject") == "Fachbereich"
    assert xml_element.findtext("article-meta/article-categories/subj-group/subj-group/subject") == "Sachgebiet"
    assert xml_element.find(f"article-meta/related-article[@{{{"http://www.w3.org/1999/xlink"}}}href='p234']") is not None
    assert xml_element.find(f"article-meta/related-article[@{{{"http://www.w3.org/1999/xlink"}}}href='p345']") is not None

    assert xml_element.findtext("article-meta/pub-date[@date-type='Ausgabedatum']/day") == "2"
    assert xml_element.findtext("article-meta/pub-date[@date-type='Ausgabedatum']/month") == "3"
    assert xml_element.findtext("article-meta/pub-date[@date-type='Ausgabedatum']/year") == "2024"
    assert xml_element.findtext("article-meta/pub-date[@date-type='AktualisierteFassung']/day") == "1"
    assert xml_element.findtext("article-meta/pub-date[@date-type='AktualisierteFassung']/month") == "1"
    assert xml_element.findtext("article-meta/pub-date[@date-type='AktualisierteFassung']/year") == "2025"
    assert xml_element.findtext("article-meta/history/date[@date-type='initial-publication']/year") == "2020"
    assert xml_element.findtext("article-meta/history/date[@date-type='correction']/year") == "2021"
    assert xml_element.findtext("article-meta/history/date[@date-type='latest-version']/year") == "2025"
    assert xml_element.findtext("article-meta/permissions/copyright-statement") == "Copyright Example"
    assert xml_element.findtext("article-meta/permissions/copyright-holder") == "Example Publisher"

    assert xml_element.findtext("article-meta/abstract[@abstract-type='short']/title") == "Short abstract"
    assert xml_element.findtext("article-meta/abstract[@abstract-type='short']/p") == "Short summary."
    assert xml_element.findtext("article-meta/abstract[@abstract-type='summary']/title") == "Summary abstract"
    assert xml_element.findtext("article-meta/abstract[@abstract-type='summary']/p") == "Long summary."
    assert xml_element.findtext("article-meta/kwd-group/kwd[1]") == "XML"
    assert xml_element.findtext("article-meta/kwd-group/kwd[2]") == "Testing"

    assert xml_element.findtext("article-meta/custom-meta-group/custom-meta[meta-name='Beschreibender Typ']/meta-value") == "Beispielwert"
    assert xml_element.findtext("article-meta/custom-meta-group/custom-meta[meta-name='Bisherige Bestellnummer']/meta-value") == "12345"
    assert xml_element.findtext("article-meta/custom-meta-group/custom-meta[meta-name='Webcode']/meta-value") == "p123"
    assert xml_element.findtext("article-meta/custom-meta-group/custom-meta[meta-name='Organisationseinheit']/meta-value") == "DGUV"
    assert xml_element.findtext("article-meta/custom-meta-group/custom-meta[meta-name='Fachbereich']/meta-value") == "Fachbereich"
    assert xml_element.findtext("article-meta/custom-meta-group/custom-meta[meta-name='Sachgebiet']/meta-value") == "Sachgebiet"
    assert xml_element.findtext("article-meta/custom-meta-group/custom-meta[meta-name='Status']/meta-value") == "veröffentlicht"
    assert xml_element.findtext("article-meta/custom-meta-group/custom-meta[meta-name='Bildnachweis']/meta-value") == "Beispielbildnachweis"
    assert xml_element.findtext("article-meta/custom-meta-group/custom-meta[meta-name='Überschriften mit Nummerierung']/meta-value") == "ja"


# --------------------------------------------------
# Positive tests
# --------------------------------------------------


def test_front_from_xml_complete():
    doc = JATSDocument.from_xml_with_parsed_schema(COMPLETE_FRONT, XML_SCHEMA)
    front = doc.article.front
    _check_complete_front(front)


def test_front_empty_has_expected_defaults():
    front = Front.empty()

    assert front.xml_lang == "de"
    assert front.title is None
    assert front.article_subtitle == []
    assert front.subjects == []
    assert front.related_articles is None
    assert front.related_articles_translations is None
    assert front.ueberschriften_mit_nummerierung is False


def test_front_missing_title_returns_none():
    doc = JATSDocument.from_xml(FRONT_WITHOUT_TITLE, None)
    front = doc.article.front

    assert front.title is None
    assert front.article_subtitle == []


def test_front_from_xml_normalizes_metadata_whitespace():
    doc = JATSDocument.from_xml(FRONT_WITH_WHITESPACE, xsd_path=None)
    front = doc.article.front

    assert front.journal_id == "journal-123"
    assert front.journal_title == "Journal of Testing"
    assert front.title == "Readable JATS Front"
    assert front.article_subtitle == ["First subtitle"]
    assert front.self_uri == "https://example.test/article-123"
    assert front.related_articles == ["p234"]
    assert front.abstract_short == "Short summary ."
    assert front.subjects == ["XML", "Testing"]
    assert front.veroeffentlichungsstatus == "veröffentlicht"


def test_front_to_xml_contains_serialized_metadata():
    doc = JATSDocument.from_xml_with_parsed_schema(COMPLETE_FRONT, XML_SCHEMA)
    front = doc.article.front
    _check_complete_front(front)

    serialized = etree.fromstring(front.to_xml().encode("utf-8"))
    _check_complete_front_xml(serialized)

    new_front = Front.from_xml_element(serialized)
    _check_complete_front(new_front)


def test_front_to_xml_omits_empty_optional_elements():
    serialized = etree.fromstring(Front.empty().to_xml().encode("utf-8"))

    assert serialized.find("article-meta/title-group/subtitle") is not None
    assert serialized.find("article-meta/pub-date[@date-type='AktualisierteFassung']") is None
    assert serialized.find("article-meta/kwd-group") is None


def test_front_to_xml_preserves_related_article_titles():
    front = Front.empty()
    front.related_articles_map = {"p234": "Related article"}
    front.related_articles_translations_map = {"p345": "Translated article"}
    serialized = etree.fromstring(front.to_xml().encode("utf-8"))

    related_article = serialized.find("article-meta/related-article[@related-article-type='companion']")
    translated_article = serialized.find("article-meta/related-article[@related-article-type='translated-article']")

    assert related_article is not None
    assert translated_article is not None
    assert "".join(str(text) for text in related_article.itertext()).strip() == "Related article"
    assert "".join(str(text) for text in translated_article.itertext()).strip() == "Translated article"


def test_front_from_dict_accepts_complete_metadata():
    front = Front.from_dict(FRONT_DICT)
    _check_complete_front(front)


def test_front_to_dict_serializes_complete_metadata():
    doc = JATSDocument.from_xml_with_parsed_schema(COMPLETE_FRONT, XML_SCHEMA)
    front = doc.article.front
    assert front.to_dict() == FRONT_DICT


def test_front_from_dict_ignores_invalid_values_and_dates():
    front = Front.from_dict(
        {
            "article_subtitle": ["Valid subtitle", 42, None],
            "related_articles": ["p234", 42, None],
            "related_articles_translations": ["p345", 42, None],
            "subjects": ["XML", 42, None],
            "pub_date_ausgabedatum": "not-a-date",
            "pub_date_aktualisierte_fassung": "2025-99-99",
            "ueberschriften_mit_nummerierung": "ja",
        }
    )

    assert front.article_subtitle == ["Valid subtitle"]
    assert front.related_articles == ["p234"]
    assert front.related_articles_translations == ["p345"]
    assert front.subjects == ["XML"]
    assert front.pub_date_ausgabedatum is None
    assert front.pub_date_aktualisierte_fassung is None
    assert front.ueberschriften_mit_nummerierung is False


def test_front_from_dict_accepts_legacy_single_subtitle():
    front = Front.from_dict({"article_subtitle": "Legacy subtitle"})

    assert front.article_subtitle == ["Legacy subtitle"]


# --------------------------------------------------
# Negative tests
# --------------------------------------------------


@pytest.mark.parametrize(
    ("xml_content", "error_message"),
    [
        (FRONT_MISSING_JOURNAL_META, "journal-meta"),
        (FRONT_MISSING_ARTICLE_META, "article-meta"),
    ],
)
def test_front_requires_journal_and_article_metadata(xml_content, error_message):
    with pytest.raises(ValueError, match=error_message):
        doc = JATSDocument.from_xml(xml_content, xsd_path=None)
