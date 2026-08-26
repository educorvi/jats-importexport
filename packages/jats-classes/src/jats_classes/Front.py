"""JATS Front model.

Represents article front-matter metadata, publisher, author, and journal info.
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, fields
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

_XLINK_NS = "http://www.w3.org/1999/xlink"
_XLINK_HREF = f"{{{_XLINK_NS}}}href"


def _text(element: etree._Element | None, xpath: str) -> str | None:
    """Return stripped text of the first matching element, or None."""
    if element is None:
        return None
    found = element.find(xpath)
    if found is None or found.text is None:
        return None
    return found.text.strip() or None


def _itertext(element: etree._Element | None, xpath: str) -> str | None:
    """Return concatenated text of all matching elements, or None."""
    if element is None:
        return None
    found = element.find(xpath)
    if found is None:
        return None
    return "".join(str(t) for t in found.itertext()).strip() or None


def _date(element: etree._Element | None, xpath: str) -> datetime.date | None:
    """Parse a JATS date element (day/month/year children) into a datetime.date object,
    or return None if not found or invalid.
    """
    if element is None:
        return None
    date_elem = element.find(xpath)
    if date_elem is None:
        return None
    try:
        year_text = _text(date_elem, "year")
        if year_text is None:
            return None
        year = int(year_text)
        month = int(_text(date_elem, "month") or 1)
        day = int(_text(date_elem, "day") or 1)
        return datetime.date(year, month, day)
    except ValueError:
        return None


def _xlink_href(element: etree._Element | None, xpath: str) -> str | None:
    """Return the xlink:href attribute of the first matching element, or None."""
    if element is None:
        return None
    found = element.find(xpath)
    if found is None:
        return None
    return found.get(_XLINK_HREF)


def _text_list(element: etree._Element | None, xpath: str) -> list[str]:
    """Return a list of stripped text from all matching elements."""
    if element is None:
        return []
    found = element.findall(xpath)
    return [f.text.strip() for f in found if f.text and f.text.strip()]


def _itertext_list(element: etree._Element | None, xpath: str) -> list[str]:
    """Return normalized text from every matching element."""
    if element is None:
        return []
    return [
        text
        for found in element.findall(xpath)
        if (text := " ".join("".join(str(t) for t in found.itertext()).split()))
    ]


def _dict(element: etree._Element | None, xpath: str, key_xpath: str, value_xpath: str) -> dict[str, str]:
    """Return a dictionary of key-value pairs from matching elements."""
    if element is None:
        return {}
    found = element.findall(xpath)
    result: dict[str, str] = {}
    for f in found:
        key = _text(f, key_xpath)
        value = _text(f, value_xpath)
        if key is not None and value is not None:
            result[key] = value
    return result


# def _create_tag(parent: etree._Element, tag: str, text: str | None = None) -> etree._Element:
#     """Create subelement with the given tag and text."""
#     elem = etree.SubElement(parent, tag)
#     elem.text = text
#     return elem


def _create_tag(
    tag: str,
    text: str | None = None,
    nsmap: dict[str, str] = {},
    attributes: dict[str, str] = {},
    children: list[etree._Element] = [],
) -> etree._Element:
    elem = etree.Element(tag, nsmap=nsmap, attrib=attributes)
    elem.text = text
    for child in children:
        elem.append(child)
    return elem


@dataclass
class Front:
    """Represents a JATS <front> element containing article metadata."""

    # -- Journal Metadata (JATS: journal-meta) --
    # JATS: journal-id
    journal_id: str | None
    # JATS: journal-title-group/journal-title
    journal_title: str | None
    # JATS: journal-title-group/journal-subtitle
    journal_subtitle: str | None
    # JATS: issn
    issn: str | None
    # JATS: publisher/publisher-name
    publisher_name: str | None
    # JATS: publisher/publisher-loc/institution
    publisher_institution: str | None
    # JATS: publisher/publisher-loc/addr-line
    publisher_addr_line: str | None
    # JATS: publisher/publisher-loc/postal-code
    publisher_postal_code: str | None
    # JATS: publisher/publisher-loc/city
    publisher_city: str | None
    # JATS: publisher/publisher-loc/phone
    publisher_phone: str | None
    # JATS: publisher/publisher-loc/email
    publisher_email: str | None
    # JATS: publisher/publisher-loc/uri
    publisher_uri: str | None

    # -- Article Metadata (JATS: article-meta) --

    # --- General Article Metadata ---
    # JATS: article-id@pub-id-type="publisher-id"
    article_id: str | None
    # JATS: title-group/article-title
    title: str | None
    # JATS: title-group/subtitle
    article_subtitle: list[str]
    # JATS: contrib-group/contrib[@contrib-type='Autor']/name/surname # TODO
    author_surname: str | None
    # JATS: contrib-group/contrib[@contrib-type='Co-Autor']/name/surname # TODO
    co_author_surname: str | None
    # JATS: contrib-group/contrib[@contrib-type='Co-Autor']/aff # TODO
    co_author_aff: str | None
    # JATS: self-uri[@href]
    self_uri: str | None
    # JATS: article-categories
    # Raw xml snippet
    article_categories: str | None
    # JATS: related-article[@href]
    related_articles: list[str] | None

    # --- Publication Dates ---
    # JATS: pub-date@date-type="Ausgabedatum"
    pub_date_ausgabedatum: datetime.date | None
    # JATS: pub-date@date-type="AktualisierteFassung"
    pub_date_aktualisierte_fassung: datetime.date | None
    # JATS: history/date@date-type="initial-publication"/year
    history_initial_publication: str | None
    # JATS: history/date@date-type="correction"/year
    history_correction: str | None
    # JATS: history/date@date-type="latest-version"/year
    history_latest_version: str | None

    # --- Copyright ---
    # JATS: permissions/copyright-statement
    copyright_statement: str | None
    # JATS: permissions/copyright-holder
    copyright_holder: str | None

    # --- Abstracts & Keywords ---
    # JATS: abstract@abstract-type="short"/title
    abstract_short_title: str | None
    # JATS: abstract@abstract-type="short"/p
    abstract_short: str | None
    # JATS: abstract@abstract-type="summary"/title
    abstract_summary_title: str | None
    # JATS: abstract@abstract-type="summary"/p
    abstract_summary: str | None
    # JATS: kwd-group@kwd-group-type="author-generated"/kwd
    subjects: list[str] | None  # formerly keywords: list[str] | None

    # --- DGUV Metadata ---
    # JATS: custom-meta-group/custom-meta/meta-name - /meta-value
    # JATS: meta-name > "Beschreibender Typ"
    beschreibender_typ: str | None
    # JATS: meta-name > "Bisherige Bestellnummer"
    bisherige_bestellnummer: str | None
    # JATS: meta-name > "Webcode"
    webcode: str | None
    # JATS: meta-name > "Organisationseinheit"
    organisationseinheit: str | None
    # JATS: meta-name > "Fachbereich"
    fachbereich: str | None
    # JATS: meta-name > "Sachgebiet"
    sachgebiet: str | None
    # JATS: meta-name > "Status"
    veroeffentlichungsstatus: str | None
    # JATS: meta-name > "Bildnachweis"
    bildnachweis: str | None
    # JATS: meta-name > "Überschriften mit Nummerierung"
    ueberschriften_mit_nummerierung: bool | None

    @classmethod
    def from_xml_element(cls, element: etree._Element) -> Front:
        """Construct a Front instance from an lxml element representing a JATS <front>.

        Args:
            element: lxml _Element node representing the <front> tag.

        Returns:
            A Front instance.
        """

        journal_meta = element.find("journal-meta")
        if journal_meta is None:
            raise ValueError("Front element must contain 'journal-meta' element")
        article_meta = element.find("article-meta")
        if article_meta is None:
            raise ValueError("Front element must contain 'article-meta' element")

        # Journal Metadata
        journal_id = _text(journal_meta, "journal-id")
        journal_title = _text(journal_meta, "journal-title-group/journal-title")
        journal_subtitle = _text(journal_meta, "journal-title-group/journal-subtitle")
        issn = _text(journal_meta, "issn")
        publisher_name = _text(journal_meta, "publisher/publisher-name")

        _publisher_loc = journal_meta.find("publisher/publisher-loc")
        publisher_institution = _text(_publisher_loc, "institution")
        publisher_addr_line = _text(_publisher_loc, "addr-line")
        publisher_postal_code = _text(_publisher_loc, "postal-code")
        publisher_city = _text(_publisher_loc, "city")
        publisher_phone = _text(_publisher_loc, "phone")
        publisher_email = _text(_publisher_loc, "email")
        publisher_uri = _text(_publisher_loc, "uri")

        # Article Metadata
        article_id = _text(article_meta, "article-id[@pub-id-type='publisher-id']")
        title = _itertext(article_meta, "title-group/article-title")
        article_subtitle = _itertext_list(article_meta, "title-group/subtitle")
        author_surname = _text(article_meta, "contrib-group/contrib[@contrib-type='Autor']/name/surname")
        co_author_surname = _text(article_meta, "contrib-group/contrib[@contrib-type='Co-Autor']/name/surname")
        co_author_aff = _text(article_meta, "contrib-group/contrib[@contrib-type='Co-Autor']/aff")
        self_uri = _xlink_href(article_meta, "self-uri")
        _article_categories = article_meta.find("article-categories")
        article_categories = (
            etree.tostring(_article_categories, encoding="unicode", with_tail=False)
            if _article_categories is not None
            else None
        )
        _related_articles = article_meta.findall("related-article")
        related_articles = []
        for ra in _related_articles:
            href = _xlink_href(ra, ".")
            if href is not None:
                related_articles.append(href)

        # Publication Dates
        pub_date_ausgabedatum = _date(article_meta, "pub-date[@date-type='Ausgabedatum']")
        pub_date_aktualisierte_fassung = _date(article_meta, "pub-date[@date-type='AktualisierteFassung']")
        history_initial_publication = _text(article_meta, "history/date[@date-type='initial-publication']/year")
        history_correction = _text(article_meta, "history/date[@date-type='correction']/year")
        history_latest_version = _text(article_meta, "history/date[@date-type='latest-version']/year")

        # Copyright
        copyright_statement = _text(article_meta, "permissions/copyright-statement")
        copyright_holder = _text(article_meta, "permissions/copyright-holder")

        # Abstracts & Keywords
        abstract_short_title = _text(article_meta, "abstract[@abstract-type='short']/title")
        abstract_short = _itertext(article_meta, "abstract[@abstract-type='short']/p")
        abstract_summary_title = _text(article_meta, "abstract[@abstract-type='summary']/title")
        abstract_summary = _itertext(article_meta, "abstract[@abstract-type='summary']/p")
        subjects = _text_list(article_meta, "kwd-group[@kwd-group-type='author-generated']/kwd")

        # DGUV Metadata
        _custom_meta_dict = _dict(article_meta, "custom-meta-group/custom-meta", "meta-name", "meta-value")
        beschreibender_typ = _custom_meta_dict.get("Beschreibender Typ")
        bisherige_bestellnummer = _custom_meta_dict.get("Bisherige Bestellnummer")
        webcode = _custom_meta_dict.get("Webcode")
        organisationseinheit = _custom_meta_dict.get("Organisationseinheit")
        fachbereich = _custom_meta_dict.get("Fachbereich")
        sachgebiet = _custom_meta_dict.get("Sachgebiet")
        veroeffentlichungsstatus = _custom_meta_dict.get("Status")
        bildnachweis = _custom_meta_dict.get("Bildnachweis")
        _ueberschriften_mit_nummerierung_str = _custom_meta_dict.get("Überschriften mit Nummerierung")
        ueberschriften_mit_nummerierung = (
            _ueberschriften_mit_nummerierung_str is not None and _ueberschriften_mit_nummerierung_str.lower() == "ja"
        )

        return cls(
            journal_id=journal_id,
            journal_title=journal_title,
            journal_subtitle=journal_subtitle,
            issn=issn,
            publisher_name=publisher_name,
            publisher_institution=publisher_institution,
            publisher_addr_line=publisher_addr_line,
            publisher_postal_code=publisher_postal_code,
            publisher_city=publisher_city,
            publisher_phone=publisher_phone,
            publisher_email=publisher_email,
            publisher_uri=publisher_uri,
            article_id=article_id,
            title=title,
            article_subtitle=article_subtitle,
            author_surname=author_surname,
            co_author_surname=co_author_surname,
            co_author_aff=co_author_aff,
            self_uri=self_uri,
            article_categories=article_categories,
            related_articles=related_articles,
            pub_date_ausgabedatum=pub_date_ausgabedatum,
            pub_date_aktualisierte_fassung=pub_date_aktualisierte_fassung,
            history_initial_publication=history_initial_publication,
            history_correction=history_correction,
            history_latest_version=history_latest_version,
            copyright_statement=copyright_statement,
            copyright_holder=copyright_holder,
            abstract_short_title=abstract_short_title,
            abstract_short=abstract_short,
            abstract_summary_title=abstract_summary_title,
            abstract_summary=abstract_summary,
            subjects=subjects,
            beschreibender_typ=beschreibender_typ,
            bisherige_bestellnummer=bisherige_bestellnummer,
            webcode=webcode,
            organisationseinheit=organisationseinheit,
            fachbereich=fachbereich,
            sachgebiet=sachgebiet,
            veroeffentlichungsstatus=veroeffentlichungsstatus,
            bildnachweis=bildnachweis,
            ueberschriften_mit_nummerierung=ueberschriften_mit_nummerierung,
        )

    # fmt: off
    def to_xml(self) -> str:
        """Serialize the Front instance to a JATS <front> XML string."""
        front = _create_tag("front", children=[
            _create_tag("journal-meta", children=[
                _create_tag("journal-id", text=self.journal_id),
                _create_tag("journal-title-group", children=[
                    _create_tag("journal-title", text=self.journal_title),
                    _create_tag("journal-subtitle", text=self.journal_subtitle),
                ]),
                _create_tag("issn", text=self.issn),
                _create_tag("publisher", children=[
                    _create_tag("publisher-name", text=self.publisher_name),
                    _create_tag("publisher-loc", children=[
                        _create_tag("institution", text=self.publisher_institution),
                        _create_tag("addr-line", text=self.publisher_addr_line),
                        _create_tag("postal-code", text=self.publisher_postal_code),
                        _create_tag("city", text=self.publisher_city),
                        _create_tag("phone", text=self.publisher_phone),
                        _create_tag("email", text=self.publisher_email),
                        _create_tag("uri", text=self.publisher_uri),
                    ]),
                ]),
            ]),
            _create_tag("article-meta", children=[
                _create_tag("article-id", text=self.article_id, attributes={"pub-id-type": "publisher-id"}),
                *([etree.fromstring(self.article_categories)] if self.article_categories else []),
                _create_tag("title-group", children=[
                    _create_tag("article-title", text=self.title),
                    *[_create_tag("subtitle", text=subtitle) for subtitle in self.article_subtitle],
                ]),
                _create_tag("contrib-group", children=[
                    _create_tag("contrib", attributes={"contrib-type": "Autor"}, children=[
                        _create_tag("name", children=[
                            _create_tag("surname", text=self.author_surname),
                        ]),
                    ]),
                    _create_tag("contrib", attributes={"contrib-type": "Co-Autor"}, children=[
                        _create_tag("name", children=[
                            _create_tag("surname", text=self.co_author_surname),
                        ]),
                        _create_tag("aff", text=self.co_author_aff),
                    ]),
                ]),
                _create_tag("pub-date", attributes={"date-type": "Ausgabedatum"}, children=[
                    _create_tag("day", text=str(self.pub_date_ausgabedatum.day) if self.pub_date_ausgabedatum else None), # noqa: E501
                    _create_tag("month", text=str(self.pub_date_ausgabedatum.month) if self.pub_date_ausgabedatum else None), # noqa: E501
                    _create_tag("year", text=str(self.pub_date_ausgabedatum.year) if self.pub_date_ausgabedatum else None),  # noqa: E501
                ]),
                _create_tag("pub-date", attributes={"date-type": "AktualisierteFassung"}, children=[
                    _create_tag("day", text=str(self.pub_date_aktualisierte_fassung.day) if self.pub_date_aktualisierte_fassung else None), # noqa: E501
                    _create_tag("month", text=str(self.pub_date_aktualisierte_fassung.month) if self.pub_date_aktualisierte_fassung else None), # noqa: E501
                    _create_tag("year", text=str(self.pub_date_aktualisierte_fassung.year) if self.pub_date_aktualisierte_fassung else None), # noqa: E501
                ]),
                _create_tag("history", children=[
                    _create_tag("date", attributes={"date-type": "initial-publication"}, children=[
                        _create_tag("year", text=self.history_initial_publication),
                    ]),
                    _create_tag("date", attributes={"date-type": "correction"}, children=[
                        _create_tag("year", text=self.history_correction),
                    ]),
                    _create_tag("date", attributes={"date-type": "latest-version"}, children=[
                        _create_tag("year", text=self.history_latest_version),
                    ]),
                ]),
                _create_tag("permissions", children=[
                    _create_tag("copyright-statement", text=self.copyright_statement),
                    _create_tag("copyright-holder", text=self.copyright_holder),
                ]),
                _create_tag("self-uri", nsmap={"xlink": _XLINK_NS}, attributes={_XLINK_HREF: self.self_uri or ""}),
                *[_create_tag("related-article",
                              attributes={"related-article-type": "companion",
                                          "ext-link-type": "publisher-id",
                                          _XLINK_HREF: related_article} )
                                          for related_article in self.related_articles or []],
                _create_tag("abstract", attributes={"abstract-type": "short"}, children=[
                    _create_tag("title", text=self.abstract_short_title),
                    _create_tag("p", text=self.abstract_short),
                ]),
                _create_tag("abstract", attributes={"abstract-type": "summary"}, children=[
                    _create_tag("title", text=self.abstract_summary_title),
                    _create_tag("p", text=self.abstract_summary),
                ]),
                _create_tag("kwd-group", attributes={"kwd-group-type": "author-generated"}, children=[
                    *[_create_tag("kwd", text=kw) for kw in self.subjects or []],
                ]),
                _create_tag("custom-meta-group", children=[
                    _create_tag("custom-meta", children=[
                        _create_tag("meta-name", text="Beschreibender Typ"),
                        _create_tag("meta-value", text=self.beschreibender_typ),
                    ]),
                    _create_tag("custom-meta", children=[
                        _create_tag("meta-name", text="Bisherige Bestellnummer"),
                        _create_tag("meta-value", text=self.bisherige_bestellnummer),
                    ]),
                    _create_tag("custom-meta", children=[
                        _create_tag("meta-name", text="Webcode"),
                        _create_tag("meta-value", text=self.webcode),
                    ]),
                    _create_tag("custom-meta", children=[
                        _create_tag("meta-name", text="Organisationseinheit"),
                        _create_tag("meta-value", text=self.organisationseinheit),
                    ]),
                    _create_tag("custom-meta", children=[
                        _create_tag("meta-name", text="Fachbereich"),
                        _create_tag("meta-value", text=self.fachbereich),
                    ]),
                    _create_tag("custom-meta", children=[
                        _create_tag("meta-name", text="Sachgebiet"),
                        _create_tag("meta-value", text=self.sachgebiet),
                    ]),
                    _create_tag("custom-meta", children=[
                        _create_tag("meta-name", text="Status"),
                        _create_tag("meta-value", text=self.veroeffentlichungsstatus),
                    ]),
                    _create_tag("custom-meta", children=[
                        _create_tag("meta-name", text="Bildnachweis"),
                        _create_tag("meta-value", text=self.bildnachweis),
                    ]),
                    _create_tag("custom-meta", children=[
                        _create_tag("meta-name", text="Überschriften mit Nummerierung"),
                        _create_tag("meta-value", text="ja" if self.ueberschriften_mit_nummerierung else "nein"),
                    ]),
                ]),
            ]),
        ])
        return etree.tostring(front, pretty_print=True, encoding="unicode")
    # fmt: on

    @classmethod
    def empty(cls) -> Front:
        """Return an empty Front instance with all fields set to None or empty."""
        return cls(
            journal_id=None,
            journal_title=None,
            journal_subtitle=None,
            issn=None,
            publisher_name=None,
            publisher_institution=None,
            publisher_addr_line=None,
            publisher_postal_code=None,
            publisher_city=None,
            publisher_phone=None,
            publisher_email=None,
            publisher_uri=None,
            article_id=None,
            title=None,
            article_subtitle=[],
            author_surname=None,
            co_author_surname=None,
            co_author_aff=None,
            self_uri=None,
            article_categories=None,
            related_articles=[],
            pub_date_ausgabedatum=None,
            pub_date_aktualisierte_fassung=None,
            history_initial_publication=None,
            history_correction=None,
            history_latest_version=None,
            copyright_statement=None,
            copyright_holder=None,
            abstract_short_title=None,
            abstract_short=None,
            abstract_summary_title=None,
            abstract_summary=None,
            subjects=[],
            beschreibender_typ=None,
            bisherige_bestellnummer=None,
            webcode=None,
            organisationseinheit=None,
            fachbereich=None,
            sachgebiet=None,
            veroeffentlichungsstatus=None,
            bildnachweis=None,
            ueberschriften_mit_nummerierung=False,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of the Front instance."""
        result = {f.name: getattr(self, f.name) for f in fields(self)}
        result["pub_date_ausgabedatum"] = self.pub_date_ausgabedatum.isoformat() if self.pub_date_ausgabedatum else None
        result["pub_date_aktualisierte_fassung"] = (
            self.pub_date_aktualisierte_fassung.isoformat() if self.pub_date_aktualisierte_fassung else None
        )
        print(result)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Front:
        """Construct a Front instance from a dictionary of metadata."""
        front = cls.empty()

        # Journal Metadata
        if isinstance((journal_id := data.get("journal_id")), str):
            front.journal_id = journal_id
        if isinstance((journal_title := data.get("journal_title")), str):
            front.journal_title = journal_title
        if isinstance((journal_subtitle := data.get("journal_subtitle")), str):
            front.journal_subtitle = journal_subtitle
        if isinstance((issn := data.get("issn")), str):
            front.issn = issn
        if isinstance((publisher_name := data.get("publisher_name")), str):
            front.publisher_name = publisher_name
        if isinstance((publisher_institution := data.get("publisher_institution")), str):
            front.publisher_institution = publisher_institution
        if isinstance((publisher_addr_line := data.get("publisher_addr_line")), str):
            front.publisher_addr_line = publisher_addr_line
        if isinstance((publisher_postal_code := data.get("publisher_postal_code")), str):
            front.publisher_postal_code = publisher_postal_code
        if isinstance((publisher_city := data.get("publisher_city")), str):
            front.publisher_city = publisher_city
        if isinstance((publisher_phone := data.get("publisher_phone")), str):
            front.publisher_phone = publisher_phone
        if isinstance((publisher_email := data.get("publisher_email")), str):
            front.publisher_email = publisher_email
        if isinstance((publisher_uri := data.get("publisher_uri")), str):
            front.publisher_uri = publisher_uri

        # Article Metadata
        if isinstance((article_id := data.get("article_id")), str):
            front.article_id = article_id
        if isinstance((title := data.get("title")), str):
            front.title = title
        article_subtitle = data.get("article_subtitle")
        if isinstance(article_subtitle, list):
            front.article_subtitle = [subtitle for subtitle in article_subtitle if isinstance(subtitle, str)]
        elif isinstance(article_subtitle, str):
            # Compatibility with Plone records created before subtitles became a list.
            front.article_subtitle = [article_subtitle]
        if isinstance((author_surname := data.get("author_surname")), str):
            front.author_surname = author_surname
        if isinstance((co_author_surname := data.get("co_author_surname")), str):
            front.co_author_surname = co_author_surname
        if isinstance((co_author_aff := data.get("co_author_aff")), str):
            front.co_author_aff = co_author_aff
        if isinstance((self_uri := data.get("self_uri")), str):
            front.self_uri = self_uri
        if isinstance((article_categories := data.get("article_categories")), str):
            front.article_categories = article_categories
        related_articles = data.get("related_articles")
        if isinstance(related_articles, list):
            front.related_articles = [ra for ra in related_articles if isinstance(ra, str)]

        # Publication Dates
        if isinstance((pub_date_ausgabedatum := data.get("pub_date_ausgabedatum")), datetime.date):
            front.pub_date_ausgabedatum = pub_date_ausgabedatum
        elif isinstance(pub_date_ausgabedatum, str):
            try:
                front.pub_date_ausgabedatum = datetime.date.fromisoformat(pub_date_ausgabedatum)
            except ValueError:
                logger.warning(f"Invalid date for pub_date_ausgabedatum: {pub_date_ausgabedatum}")
        if isinstance(
            (pub_date_aktualisierte_fassung := data.get("pub_date_aktualisierte_fassung")),
            datetime.date,
        ):
            front.pub_date_aktualisierte_fassung = pub_date_aktualisierte_fassung
        elif isinstance(pub_date_aktualisierte_fassung, str):
            try:
                front.pub_date_aktualisierte_fassung = datetime.date.fromisoformat(pub_date_aktualisierte_fassung)
            except ValueError:
                logger.warning(f"Invalid date for pub_date_aktualisierte_fassung: {pub_date_aktualisierte_fassung}")
        if isinstance(
            (history_initial_publication := data.get("history_initial_publication")),
            str,
        ):
            front.history_initial_publication = history_initial_publication
        if isinstance((history_correction := data.get("history_correction")), str):
            front.history_correction = history_correction
        if isinstance((history_latest_version := data.get("history_latest_version")), str):
            front.history_latest_version = history_latest_version

        # Copyright
        if isinstance((copyright_statement := data.get("copyright_statement")), str):
            front.copyright_statement = copyright_statement
        if isinstance((copyright_holder := data.get("copyright_holder")), str):
            front.copyright_holder = copyright_holder

        # Abstracts & Keywords
        if isinstance((abstract_short_title := data.get("abstract_short_title")), str):
            front.abstract_short_title = abstract_short_title
        if isinstance((abstract_short := data.get("abstract_short")), str):
            front.abstract_short = abstract_short
        if isinstance((abstract_summary_title := data.get("abstract_summary_title")), str):
            front.abstract_summary_title = abstract_summary_title
        if isinstance((abstract_summary := data.get("abstract_summary")), str):
            front.abstract_summary = abstract_summary
        if isinstance((subjects := data.get("subjects")), list):
            front.subjects = [kw for kw in subjects if isinstance(kw, str)]

        # DGUV Metadata
        if isinstance((beschreibender_typ := data.get("beschreibender_typ")), str):
            front.beschreibender_typ = beschreibender_typ
        if isinstance((bisherige_bestellnummer := data.get("bisherige_bestellnummer")), str):
            front.bisherige_bestellnummer = bisherige_bestellnummer
        if isinstance((webcode := data.get("webcode")), str):
            front.webcode = webcode
        if isinstance((organisationseinheit := data.get("organisationseinheit")), str):
            front.organisationseinheit = organisationseinheit
        if isinstance((fachbereich := data.get("fachbereich")), str):
            front.fachbereich = fachbereich
        if isinstance((sachgebiet := data.get("sachgebiet")), str):
            front.sachgebiet = sachgebiet
        if isinstance((veroeffentlichungsstatus := data.get("veroeffentlichungsstatus")), str):
            front.veroeffentlichungsstatus = veroeffentlichungsstatus
        if isinstance((bildnachweis := data.get("bildnachweis")), str):
            front.bildnachweis = bildnachweis
        if isinstance(
            (ueberschriften_mit_nummerierung := data.get("ueberschriften_mit_nummerierung")),
            bool,
        ):
            front.ueberschriften_mit_nummerierung = ueberschriften_mit_nummerierung

        return front
