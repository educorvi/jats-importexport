"""Fixtures for JatsExporter tests.

Provides builders for domain model instances (Front, Body, Back, Section, ...)
used to exercise `JatsExporter`. Complex fixtures are built by parsing small,
hand-written JATS XML fragments through the real `jats_classes` parsers, so the
resulting objects are realistic and consistent with how imported documents look.
"""

from __future__ import annotations

import datetime

from jats_classes import (
    Appendix,
    AppendixGroup,
    Article,
    Back,
    Body,
    Front,
    JATSDocument,
    Section,
)
from lxml import etree

# --------------------------------------------------
# Front fixtures
# --------------------------------------------------


def empty_front(title: str = "Test Article", xml_lang: str = "de") -> Front:
    """A Front with only a title set, all other fields empty/None."""
    front = Front.empty()
    front.xml_lang = xml_lang
    front.title = title
    return front


def front_with_pub_date(**overrides) -> Front:
    """An otherwise-empty Front but with a valid Ausgabedatum pub-date set."""
    front = empty_front(**overrides)
    front.pub_date_ausgabedatum = datetime.date(2024, 3, 2)
    return front


# A fully populated <front> fragment, parsed via `Front.from_xml_element` so every
# field is realistically set (mirrors a document parsed from real JATS input).
_COMPLETE_FRONT_XML = """<front xmlns:xlink="http://www.w3.org/1999/xlink">
    <journal-meta>
        <journal-id>journal-123</journal-id>
        <journal-title-group>
            <journal-title>Journal of Testing</journal-title>
            <journal-subtitle>Reliable XML</journal-subtitle>
        </journal-title-group>
        <issn>1234-5678</issn>
        <publisher>
            <publisher-name>Example Publisher</publisher-name>
            <publisher-loc>
                <institution>Testing Institute</institution>
                <addr-line>Example Street 1</addr-line>
                <postal-code>12345</postal-code>
                <city>Test City</city>
                <phone>+49 123 456</phone>
                <email>mail@example.test</email>
                <uri>https://example.test</uri>
            </publisher-loc>
        </publisher>
    </journal-meta>
    <article-meta>
        <article-id pub-id-type="publisher-id">article-123</article-id>
        <title-group>
            <article-title>Complete JATS Front</article-title>
            <subtitle>First subtitle</subtitle>
        </title-group>
        <contrib-group>
            <contrib contrib-type="Autor"><name><surname>Author</surname></name></contrib>
            <contrib contrib-type="Co-Autor">
                <name><surname>Coauthor</surname></name>
                <aff>Testing Department</aff>
            </contrib>
        </contrib-group>
        <pub-date date-type="Ausgabedatum">
            <day>2</day><month>3</month><year>2024</year>
        </pub-date>
        <history>
            <date date-type="initial-publication"><year>2020</year></date>
            <date date-type="correction"><year>2021</year></date>
            <date date-type="latest-version"><year>2025</year></date>
        </history>
        <permissions>
            <copyright-statement>Copyright Example</copyright-statement>
            <copyright-holder>Example Publisher</copyright-holder>
        </permissions>
        <self-uri xlink:href="https://example.test/article-123"/>
        <abstract abstract-type="short">
            <title>Short abstract</title>
            <p>Short summary.</p>
        </abstract>
        <abstract abstract-type="summary">
            <title>Summary abstract</title>
            <p>Long summary.</p>
        </abstract>
        <kwd-group kwd-group-type="author-generated">
            <kwd>XML</kwd><kwd>Testing</kwd>
        </kwd-group>
        <custom-meta-group>
            <custom-meta><meta-name>Beschreibender Typ</meta-name><meta-value>Beispielwert</meta-value></custom-meta>
            <custom-meta><meta-name>Bisherige Bestellnummer</meta-name><meta-value>12345</meta-value></custom-meta>
            <custom-meta><meta-name>Webcode</meta-name><meta-value>p123</meta-value></custom-meta>
            <custom-meta><meta-name>Organisationseinheit</meta-name><meta-value>DGUV</meta-value></custom-meta>
            <custom-meta><meta-name>Fachbereich</meta-name><meta-value>Fachbereich</meta-value></custom-meta>
            <custom-meta><meta-name>Sachgebiet</meta-name><meta-value>Sachgebiet</meta-value></custom-meta>
            <custom-meta><meta-name>Status</meta-name><meta-value>veroeffentlicht</meta-value></custom-meta>
            <custom-meta><meta-name>Bildnachweis</meta-name><meta-value>Beispielbildnachweis</meta-value></custom-meta>
            <custom-meta><meta-name>Ueberschriften mit Nummerierung</meta-name><meta-value>ja</meta-value></custom-meta>
        </custom-meta-group>
    </article-meta>
</front>"""


def complete_front(xml_lang: str = "de") -> Front:
    """A fully populated Front, parsed from a realistic JATS <front> fragment."""
    element = etree.fromstring(_COMPLETE_FRONT_XML.encode("utf-8"))
    return Front.from_xml_element(element, xml_lang=xml_lang)


# --------------------------------------------------
# Section / Appendix / AppendixGroup fixtures
# --------------------------------------------------


def make_section(
    title: str = "Section title",
    sec_type: str | None = None,
    label: str | None = None,
    content: str = "<p>Section content.</p>",
    sections: list[Section] | None = None,
) -> Section:
    label_xml = f"<label>{label}</label>" if label else ""
    return Section(
        sec_type=sec_type,
        label_title_raw=f"{label_xml}<title>{title}</title>",
        content_raw=content,
        sections=sections or [],
    )


def make_appendix(
    title: str = "Appendix title",
    sec_type: str | None = None,
    content: str = "<p>Appendix content.</p>",
    sections: list[Section] | None = None,
) -> Appendix:
    return Appendix(
        sec_type=sec_type,
        label_title_raw=f"<title>{title}</title>",
        content_raw=content,
        sections=sections or [],
    )


def make_appendix_group(
    title: str = "Appendix group title",
    sec_type: str | None = None,
    appendixes: list[Appendix] | None = None,
) -> AppendixGroup:
    return AppendixGroup(
        sec_type=sec_type,
        label_title_raw=f"<title>{title}</title>",
        content_raw=None,
        appendixes=appendixes or [make_appendix()],
    )


# --------------------------------------------------
# Full document builder
# --------------------------------------------------


def make_document(
    front: Front | None = None,
    sections: list[Section] | None = None,
    back: Back | None = None,
) -> JATSDocument:
    front = front if front is not None else front_with_pub_date()
    body = Body(sections=sections if sections is not None else [])
    article = Article(front=front, body=body, back=back)
    return JATSDocument(article=article)
