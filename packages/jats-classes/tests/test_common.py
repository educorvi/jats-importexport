from lxml import etree

from jats_classes.common import try_repair_mojibake, try_repair_mojibake_element


def test_repair_mojibake_next_to_german_characters():
    text = (
        "Unfallverhütungsvorschrift: 90Â° können; "
        "gibtâ€™damit Durchführungsanweisungen."
    )

    repaired = (
        "Unfallverhütungsvorschrift: 90° können; "
        "gibt’damit Durchführungsanweisungen."
    )

    assert try_repair_mojibake(text) == repaired


def test_repair_mojibake_preserves_characters_outside_cp1252():
    assert try_repair_mojibake("日本語 🙂 90Â°") == "日本語 🙂 90°"


def test_repair_mojibake_element_repairs_mixed_text_and_tail():
    element = etree.fromstring(
        "<p>Unfallverhütung <i>90Â°</i> können und gibtâ€™damit.</p>"
    )

    try_repair_mojibake_element(element)

    assert element.text == "Unfallverhütung "
    assert element[0].text == "90°"
    assert element[0].tail == " können und gibt’damit."
