import datetime

import pytest
from jats_classes import Front
from jats_examples.front import (
    FRONT_MISSING_ARTICLE_META,
    FRONT_MISSING_JOURNAL_META,
    FRONT_WITHOUT_TITLE,
    FRONT_XML,
)
from lxml import etree


def get_front(xml_content=FRONT_XML, xml_lang="en"):
    return Front.from_xml_element(etree.fromstring(xml_content), xml_lang=xml_lang)


# --------------------------------------------------
# Positive tests
# --------------------------------------------------


def test_front_from_xml_reads_journal_and_article_metadata():
    front = get_front()

    assert front.xml_lang == "en"
    assert front.journal_id == "journal-123"
    assert front.journal_title == "Journal of Testing"
    assert front.journal_subtitle == "Reliable XML"
    assert front.issn == "1234-5678"
    assert front.publisher_name == "Example Publisher"
    assert front.publisher_city == "Test City"
    assert front.article_id == "article-123"
    assert front.title == "Readable JATS Front"
    assert front.article_subtitle == ["First subtitle", "Second subtitle"]
    assert front.author_surname == "Author"
    assert front.co_author_surname == "Coauthor"
    assert front.co_author_aff == "Testing Department"
    assert front.self_uri == "https://example.test/article-123"


def test_front_from_xml_reads_dates_related_articles_and_content():
    front = get_front()

    assert front.pub_date_ausgabedatum == datetime.date(2024, 3, 2)
    assert front.pub_date_aktualisierte_fassung == datetime.date(2025, 1, 1)
    assert front.history_initial_publication == "2020"
    assert front.history_correction == "2021"
    assert front.history_latest_version == "2025"
    assert front.related_articles == ["https://example.test/related"]
    assert front.related_articles_translations == ["https://example.test/translation"]
    assert front.abstract_short_title == "Short abstract"
    assert front.abstract_short == "Short summary."
    assert front.abstract_summary_title == "Summary abstract"
    assert front.abstract_summary == "Long summary."
    assert front.subjects == ["XML", "Testing"]
    assert front.webcode == "WEB-123"
    assert front.ueberschriften_mit_nummerierung is True


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
    front = get_front(FRONT_WITHOUT_TITLE)

    assert front.title is None
    assert front.article_subtitle == []


def test_front_to_dict_and_from_dict_preserve_parsed_values():
    original = get_front()

    restored = Front.from_dict(original.to_dict())

    assert restored.xml_lang == original.xml_lang
    assert restored.title == original.title
    assert restored.article_subtitle == original.article_subtitle
    assert restored.pub_date_ausgabedatum == original.pub_date_ausgabedatum
    assert restored.pub_date_aktualisierte_fassung == original.pub_date_aktualisierte_fassung
    assert restored.related_articles == original.related_articles
    assert restored.related_articles_translations == original.related_articles_translations
    assert restored.subjects == original.subjects
    assert restored.webcode == original.webcode


def test_front_from_dict_accepts_legacy_single_subtitle():
    front = Front.from_dict({"article_subtitle": "Legacy subtitle"})

    assert front.article_subtitle == ["Legacy subtitle"]


def test_front_to_xml_contains_serialized_metadata():
    front = get_front()

    serialized = etree.fromstring(front.to_xml().encode("utf-8"))

    assert serialized.tag == "front"
    assert serialized.findtext("article-meta/title-group/article-title") == "Readable JATS Front"
    assert serialized.xpath("article-meta/title-group/subtitle/text()") == ["First subtitle", "Second subtitle"]
    assert serialized.find("article-meta/related-article[@related-article-type='companion']") is not None
    assert serialized.find("article-meta/related-article[@related-article-type='translated-article']") is not None


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
        get_front(xml_content)
