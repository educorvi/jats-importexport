"""Parsing the metadata of a JATSDocument from the content_raw of the <front> element."""

import datetime
from collections.abc import Callable
from typing import Any

from lxml import etree as ET

_XLINK_NS = "http://www.w3.org/1999/xlink"
_XLINK_HREF = f"{{{_XLINK_NS}}}href"

# Ordered list of custom-meta entries: (meta-name, article field, to_xml, from_xml)
_CUSTOM_META: list[tuple[str, str, Callable[[Any], Any] | None, Callable[[Any], Any] | None]] = [
    ("Beschreibender Typ", "beschreibender_typ", None, None),
    ("Bisherige Bestellnummer", "bisherige_bestellnummer", None, None),
    ("Webcode", "webcode", None, None),
    ("Organisationseinheit", "organisationseinheit", None, None),
    ("Fachbereich", "fachbereich", None, None),
    ("Sachgebiet", "sachgebiet", None, None),
    ("Status", "veroeffentlichungsstatus", None, None),
    ("Bildnachweis", "bildnachweis", None, None),
    (
        "Überschriften mit Nummerierung",
        "ueberschriften_mit_nummerierung",
        lambda v: "ja" if v else "nein",
        lambda v: v.lower() == "ja" if v else False,
    ),
]


def get_article_metadata(content_raw: str | None) -> dict[str, Any]:
    """Extract metadata from the raw content of the <front> element of a JATSDocument.

    Args:
        content_raw: The raw XML string of the <front> element.

    Returns:
        A dictionary containing the extracted metadata.
    """
    metadata: dict[str, Any] = {}

    if content_raw is None:
        return metadata

    root = _parse_front_content(content_raw)
    if root is None:
        return metadata

    jm = root.find("journal-meta")
    if jm is not None:
        metadata.update(_read_journal_meta(jm))

    am = root.find("article-meta")
    if am is not None:
        metadata.update(_read_article_meta(am))

    return metadata


def _parse_front_content(content_raw: str):
    """Wrap content_raw in <front> and parse it; return root or None on error."""
    try:
        return ET.fromstring(f"<front>{content_raw}</front>".encode())
    except ET.XMLSyntaxError:
        return None


def _text(element: ET._Element, xpath: str) -> str | None:
    """Return stripped text of the first matching element, or None."""
    found = element.find(xpath)
    if found is not None and found.text:
        return found.text.strip() or None
    return None


def _parse_date(element: ET._Element, xpath: str) -> datetime.date | None:
    """Parse a JATS date element (day/month/year children) into a date."""
    date_el = element.find(xpath)
    if date_el is None:
        return None
    year = _text(date_el, "year")
    month = _text(date_el, "month")
    day = _text(date_el, "day")
    if not year:
        return None
    try:
        return datetime.date(
            int(year),
            int(month) if month else 1,
            int(day) if day else 1,
        )
    except (ValueError, TypeError):
        return None


def _read_journal_meta(jm: ET._Element):
    result: dict[str, Any] = {}
    result["journal_id"] = _text(jm, "journal-id")
    result["journal_title"] = _text(jm, "journal-title-group/journal-title")
    result["journal_subtitle"] = _text(jm, "journal-title-group/journal-subtitle")
    result["issn"] = _text(jm, "issn")
    result["publisher_name"] = _text(jm, "publisher/publisher-name")
    loc = jm.find("publisher/publisher-loc")
    if loc is not None:
        result["publisher_institution"] = _text(loc, "institution")
        result["publisher_addr_line"] = _text(loc, "addr-line")
        result["publisher_postal_code"] = _text(loc, "postal-code")
        result["publisher_city"] = _text(loc, "city")
        result["publisher_phone"] = _text(loc, "phone")
        result["publisher_email"] = _text(loc, "email")
        result["publisher_uri"] = _text(loc, "uri")
    else:
        for field in (
            "publisher_institution",
            "publisher_addr_line",
            "publisher_postal_code",
            "publisher_city",
            "publisher_phone",
            "publisher_email",
            "publisher_uri",
        ):
            result[field] = None
    return result


def _read_article_meta(am: ET._Element):
    result: dict[str, Any] = {}
    article_id_el = am.find("article-id[@pub-id-type='publisher-id']")
    result["article_id"] = article_id_el.text.strip() if article_id_el is not None and article_id_el.text else None

    result["article_subtitle"] = _text(am, "title-group/subtitle")

    author = am.find("contrib-group/contrib[@contrib-type='Autor']")
    result["author_surname"] = _text(author, "name/surname") if author is not None else None

    co_author = am.find("contrib-group/contrib[@contrib-type='Co-Autor']")
    if co_author is not None:
        result["co_author_surname"] = _text(co_author, "name/surname")
        result["co_author_aff"] = _text(co_author, "aff")
    else:
        result["co_author_surname"] = None
        result["co_author_aff"] = None

    result["pub_date_ausgabedatum"] = _parse_date(am, "pub-date[@date-type='Ausgabedatum']")
    result["pub_date_aktualisierte_fassung"] = _parse_date(am, "pub-date[@date-type='AktualisierteFassung']")

    result["history_initial_publication"] = _text(am, "history/date[@date-type='initial-publication']/year")
    result["history_correction"] = _text(am, "history/date[@date-type='correction']/year")
    result["history_latest_version"] = _text(am, "history/date[@date-type='latest-version']/year")

    result["copyright_statement"] = _text(am, "permissions/copyright-statement")
    result["copyright_holder"] = _text(am, "permissions/copyright-holder")

    self_uri_el = am.find("self-uri")
    result["self_uri"] = self_uri_el.get(_XLINK_HREF) or None if self_uri_el is not None else None

    abstract_short = am.find("abstract[@abstract-type='short']")
    if abstract_short is not None:
        result["abstract_short_title"] = _text(abstract_short, "title")
        result["abstract_short"] = _text(abstract_short, "p")
    else:
        result["abstract_short_title"] = None
        result["abstract_short"] = None

    abstract_summary = am.find("abstract[@abstract-type='summary']")
    if abstract_summary is not None:
        result["abstract_summary_title"] = _text(abstract_summary, "title")
        result["abstract_summary"] = _text(abstract_summary, "p")
    else:
        result["abstract_summary_title"] = None
        result["abstract_summary"] = None

    kwd_group = am.find("kwd-group[@kwd-group-type='author-generated']")
    result["keywords"] = (
        [kwd.text.strip() for kwd in kwd_group.findall("kwd") if kwd.text and kwd.text.strip()]
        if kwd_group is not None
        else []
    )

    custom_meta_map = {
        name_el.text.strip(): (value_el.text.strip() if value_el is not None and value_el.text else None)
        for cm in am.findall("custom-meta-group/custom-meta")
        if (name_el := cm.find("meta-name")) is not None and name_el.text
        for value_el in [cm.find("meta-value")]
    }

    for meta_name, field, _to_xml, from_xml in _CUSTOM_META:
        raw = custom_meta_map.get(meta_name)
        result[field] = from_xml(raw) if from_xml else raw

    return result
