import datetime
import logging
import re

from lxml import etree

logger = logging.getLogger(__name__)

# Common utility functions for handling JATS XML elements and text.

_XLINK_HREF = "{http://www.w3.org/1999/xlink}href"


def clean_string(string: str) -> str:
    """Remove leading and trailing whitespace and newlines from a string."""
    return re.sub(r"[\s]+", " ", string).strip()


def clean_string_and_repair(string: str | None) -> str | None:
    """Remove leading and trailing whitespace and newlines from a string."""
    if string is None:
        return None
    repaired = try_repair_mojibake(string)
    return clean_string(repaired)


def element_text(element: etree._Element | None, xpath: str) -> str | None:
    """Return stripped text of the first matching element, or None."""
    if element is None:
        return None
    found = element.find(xpath)
    if found is None or found.text is None:
        return None
    return clean_string_and_repair(found.text) or None


def element_itertext(element: etree._Element | None, xpath: str) -> str | None:
    """Return concatenated text of the first matching element, or None."""
    if element is None:
        return None
    found = element.find(xpath)
    if found is None:
        return None
    return clean_string_and_repair("".join(str(t) for t in found.itertext())) or None


def element_date(element: etree._Element | None, xpath: str) -> datetime.date | None:
    """Parse a JATS date element (day/month/year children) into a datetime.date object,
    or return None if not found or invalid.
    """
    if element is None:
        return None
    date_elem = element.find(xpath)
    if date_elem is None:
        return None
    try:
        year_text = element_text(date_elem, "year")
        if year_text is None:
            return None
        year = int(year_text)
        month = int(element_text(date_elem, "month") or 1)
        day = int(element_text(date_elem, "day") or 1)
        return datetime.date(year, month, day)
    except ValueError:
        return None


def element_text_list(element: etree._Element | None, xpath: str) -> list[str]:
    """Return a list of stripped text from all matching elements."""
    if element is None:
        return []
    found = element.findall(xpath)
    result = []
    for f in found:
        if f.text and (cleaned := clean_string_and_repair(f.text)):
            result.append(cleaned)
    return result


def element_itertext_list(element: etree._Element | None, xpath: str) -> list[str]:
    """Return normalized text from every matching element."""
    if element is None:
        return []
    found = element.findall(xpath)
    result = []
    for f in found:
        if cleaned := clean_string_and_repair("".join(str(t) for t in f.itertext())):
            result.append(cleaned)
    return result


def element_dict(element: etree._Element | None, xpath: str, key_xpath: str, value_xpath: str) -> dict[str, str]:
    """Return a dictionary of key-value pairs from matching elements."""
    if element is None:
        return {}
    found = element.findall(xpath)
    result: dict[str, str] = {}
    for f in found:
        key = element_text(f, key_xpath)
        value = element_text(f, value_xpath)
        if key is not None and value is not None:
            result[key] = value
    return result


def element_attribute(element: etree._Element | None, xpath: str, attribute_name: str) -> str | None:
    """Return the specified attribute of the first matching element, or None."""
    if element is None:
        return None
    found = element.find(xpath)
    if found is None:
        return None
    return clean_string_and_repair(found.get(attribute_name)) or None


# Utilities for detecting and repairing typical CP1252 mojibake in text.


def _mojibake_score(text: str) -> int:
    """
    A simple heuristic score for typical mojibake patterns.
    The higher the score, the more suspicious the text is.
    """
    # Common mojibake characters
    SUSPICIOUS_CHARS = set("ÃÂâð")

    # Common mojibake sequences
    SUSPICIOUS_SEQUENCES = (
        "â€",
        "â†",
        "â„",
        "Ã¤",
        "Ã¶",
        "Ã¼",
        "ÃŸ",
        "Â°",
        "Â©",
        "Â®",
    )

    score = 0

    for char in text:
        if char in SUSPICIOUS_CHARS:
            score += 2

    for sequence in SUSPICIOUS_SEQUENCES:
        score += text.count(sequence) * 3

    return score


def _repair_once(text: str):
    """
    Try to repair typical CP1252 mojibake.
    Returns the repaired text if successful, otherwise None.
    """
    try:
        raw_bytes = bytearray()
        for char in text:
            try:
                raw_bytes.extend(char.encode("cp1252"))
            except UnicodeEncodeError:
                raw_bytes.extend(char.encode("utf-8"))

        decoded = raw_bytes.decode("utf-8", errors="surrogateescape")
    except UnicodeEncodeError:
        return None

    repaired = []
    for char in decoded:
        codepoint = ord(char)
        if 0xDC80 <= codepoint <= 0xDCFF:
            byte = codepoint - 0xDC00
            try:
                repaired.append(bytes((byte,)).decode("cp1252"))
            except UnicodeDecodeError:
                repaired.append(chr(byte))
        else:
            repaired.append(char)

    return "".join(repaired)


def try_repair_mojibake(text: str, max_rounds: int = 3):
    """
    Try to repair typical CP1252 mojibake in the given text.
    A repair is only accepted if it reduces the mojibake score.

    :param text: The text to attempt to repair.
    :param max_rounds: Maximum number of repair attempts.

    :return: The repaired text if successful, otherwise the original text.
    """
    current = text

    for _ in range(max_rounds):
        repaired = _repair_once(current)

        if repaired is None:
            break

        if _mojibake_score(repaired) >= _mojibake_score(current):
            break

        logger.debug(f"Repaired mojibake text:\n\tfrom: {current}\n\tto:  {repaired}")
        current = repaired

    return current


def try_repair_mojibake_element(element: etree._Element | None, max_rounds: int = 3) -> etree._Element | None:
    """Try to repair typical CP1252 mojibake in the text content of the given element."""
    if element is None:
        return None
    if element.text:
        element.text = try_repair_mojibake(element.text, max_rounds=max_rounds)
    if element.tail:
        element.tail = try_repair_mojibake(element.tail, max_rounds=max_rounds)
    for attr_name, attr_value in element.attrib.items():
        element.attrib[attr_name] = try_repair_mojibake(attr_value, max_rounds=max_rounds)
    for child in element:
        try_repair_mojibake_element(child, max_rounds=max_rounds)
    return element
