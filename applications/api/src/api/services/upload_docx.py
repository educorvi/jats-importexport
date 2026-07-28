from fastapi import HTTPException
from lxml import etree

# Helper functions for DOCX processing and metadata extraction


XML_WORD_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE article PUBLIC
    "-//NLM//DTD JATS (Z39.96) Journal Publishing DTD with OASIS Tables with MathML3 v1.1 20151215//EN"
    "JATS-journalpublishing-oasis-article1-mathml3.dtd">
<article xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink"
    xml:lang="de" article-type="DGUV Vorschriften- und Regelwerk" dtd-version="1.1">
    <front>
        <journal-meta>
            <journal-id></journal-id>
            <journal-title-group><journal-title></journal-title></journal-title-group>
            <issn></issn>
            <publisher><publisher-name></publisher-name></publisher>
        </journal-meta>
        <article-meta>
            <article-id></article-id>
            <title-group><article-title></article-title></title-group>
            <permissions></permissions>
        </article-meta>
    </front>
    <body>
        {docx_content}
    </body>
</article>
"""


def get_xml_from_docx_content(docx_content: str) -> str:
    """Wrap the converted DOCX content in a JATS XML structure."""
    return XML_WORD_TEMPLATE.format(docx_content=docx_content)


def _get_metadata_dict_from_docx_tree(xml_tree: etree._Element) -> dict[str, str]:
    """Extract metadata from the converted and parsed DOCX content represented as an lxml XML tree.
    The document must contain a table at the beginning with two columns.
    """

    metadata_dict: dict[str, str] = {}
    body = xml_tree.find("body")
    if body is None:
        raise HTTPException(status_code=400, detail="Converted DOCX content does not contain a body.")
    if len(body) == 0 or body[0].tag != "table-wrap":
        return metadata_dict
    table_wrap = body[0]
    if table_wrap is None:
        return metadata_dict
    table = table_wrap.find("table")
    if table is None:
        return metadata_dict
    table_body = table.find("tbody")
    if table_body is None:
        return metadata_dict

    for row in table_body.findall("tr"):
        cells = row.findall("td")
        if len(cells) != 2:
            continue
        key = " ".join(" ".join(str(t).split()) for t in cells[0].itertext()).strip()
        # if key.startswith("Autor"): import pdb; pdb.set_trace()
        value = " ".join(" ".join(str(t).split()) for t in cells[1].itertext()).strip()
        if key:
            metadata_dict[key] = value

    return metadata_dict


def _parse_author_name(name_str: str) -> dict[str, str]:
    """Parse an author name string into its components (prefix, given-names, surname, aff).
    Returns a dictionary of the parsed name components.
    If the name is not a real person name (e.g., an organization), the dictionary will only contain the 'surname' key.
    """
    if not name_str.strip():
        return {"surname": ""}

    # Parse name components
    parts = name_str.split(",", 1)
    if len(parts) == 1:
        return {"surname": parts[0].strip()}  # No aff part, likely an organization name

    name_part = parts[0].strip()
    aff_part = parts[1].strip()

    # Parse name (handle prefix like "Dr.")
    name_tokens = name_part.split()
    prefix = ""
    given_names = ""
    surname = ""

    if name_tokens:
        if len(name_tokens) == 1:
            surname = name_tokens[0]
        else:
            # Check if first token is a prefix
            if name_tokens[0] in ["Dr.", "Prof.", "Prof", "Dr"]:
                prefix = name_tokens[0]
                name_tokens = name_tokens[1:]

            if len(name_tokens) >= 2:
                given_names = " ".join(name_tokens[:-1])
                surname = name_tokens[-1]
            elif len(name_tokens) == 1:
                surname = name_tokens[0]

    return {
        "prefix": prefix,
        "given-names": given_names,
        "surname": surname,
        "aff": aff_part,
    }


def _add_author_to_contrib(contrib: etree._Element, name_dict: dict[str, str]) -> None:
    """Add name components to a <contrib> element in the XML tree."""
    name = etree.SubElement(contrib, "name")
    surname_elem = etree.SubElement(name, "surname")

    if name_dict.get("surname"):
        surname_elem.text = name_dict["surname"]

    if name_dict.get("given-names"):
        given_names_elem = etree.SubElement(name, "given-names")
        given_names_elem.text = name_dict["given-names"]

    if name_dict.get("prefix"):
        prefix_elem = etree.SubElement(name, "prefix")
        prefix_elem.text = name_dict["prefix"]

    if name_dict.get("aff"):
        aff = etree.SubElement(contrib, "aff")
        aff.text = name_dict["aff"]


def parse_and_add_metadata_to_docx_tree(xml_tree: etree._Element, XML_NAMESPACE: str, XLINK_NAMESPACE: str) -> None:
    """Parse the metadata from the converted DOCX content represented as an lxml XML tree
    and add it to the <front> section of the JATS XML structure.
    """
    metadata_dict = _get_metadata_dict_from_docx_tree(xml_tree)

    article = xml_tree

    # === Article Attributes ===

    # lang attribute
    if "Sprache" in metadata_dict:
        article.set(f"{{{XML_NAMESPACE}}}lang", metadata_dict["Sprache"])

    # article-type attribute
    if "Article-Type" in metadata_dict:
        article.set("article-type", metadata_dict["Article-Type"])

    # === Front Section ===

    front = article.find("front")
    if front is None:
        return
    for child in list(front):
        front.remove(child)

    journal_meta = etree.SubElement(front, "journal-meta")
    article_meta = etree.SubElement(front, "article-meta")

    # === Journal Meta ===

    # Journal ID (empty)
    etree.SubElement(journal_meta, "journal-id")

    # Journal Title and Subtitle
    journal_title_group = etree.SubElement(journal_meta, "journal-title-group")
    journal_title = etree.SubElement(journal_title_group, "journal-title")
    if "Journal-Titel" in metadata_dict:
        journal_title.text = metadata_dict["Journal-Titel"]
    if "Journal-Untertitel" in metadata_dict:
        journal_subtitle = etree.SubElement(journal_title_group, "journal-subtitle")
        journal_subtitle.text = metadata_dict["Journal-Untertitel"]

    # ISSN
    issn = etree.SubElement(journal_meta, "issn")
    if "ISSN" in metadata_dict:
        issn.text = metadata_dict["ISSN"]

    # Publisher
    publisher = etree.SubElement(journal_meta, "publisher")
    publisher_name = etree.SubElement(publisher, "publisher-name")
    if "Herausgeber" in metadata_dict:
        publisher_name.text = metadata_dict["Herausgeber"]
    if (
        "Adresse Strasse" in metadata_dict
        or "Adresse Hausnummer" in metadata_dict
        or "Postleitzahl" in metadata_dict
        or "Ort" in metadata_dict
        or "Telefonnummer" in metadata_dict
        or "E-Mail-Adresse" in metadata_dict
        or "Webseite" in metadata_dict
    ):
        publisher_loc = etree.SubElement(publisher, "publisher-loc")
        if "Herausgeber" in metadata_dict:
            institution = etree.SubElement(publisher_loc, "institution")
            institution.text = metadata_dict["Herausgeber"]
        if "Adresse Strasse" in metadata_dict or "Adresse Hausnummer" in metadata_dict:
            addr_line = etree.SubElement(publisher_loc, "addr-line")
            street = metadata_dict.get("Adresse Strasse", "")
            number = metadata_dict.get("Adresse Hausnummer", "")
            addr_line.text = f"{street} {number}".strip()
        if "Postleitzahl" in metadata_dict:
            postal_code = etree.SubElement(publisher_loc, "postal-code")
            postal_code.text = metadata_dict["Postleitzahl"]
        if "Ort" in metadata_dict:
            city = etree.SubElement(publisher_loc, "city")
            city.text = metadata_dict["Ort"]
        if "Telefonnummer" in metadata_dict:
            phone = etree.SubElement(publisher_loc, "phone")
            phone.text = metadata_dict["Telefonnummer"]
        if "E-Mail-Adresse" in metadata_dict:
            email = etree.SubElement(publisher_loc, "email")
            email.text = metadata_dict["E-Mail-Adresse"]
        if "Webseite" in metadata_dict:
            uri = etree.SubElement(publisher_loc, "uri")
            uri.text = metadata_dict["Webseite"]

    # === Article Meta ===

    # Article ID
    article_id = etree.SubElement(article_meta, "article-id")
    if "Titel-Nummer" in metadata_dict:
        article_id.set("pub-id-type", "publisher-id")
        article_id.text = metadata_dict["Titel-Nummer"]

    # Article Categories
    if "Fachbereich" in metadata_dict or "Sachgebiet" in metadata_dict:
        article_categories = etree.SubElement(article_meta, "article-categories")
        subj_group = etree.SubElement(article_categories, "subj-group")
        if "Fachbereich" not in metadata_dict:
            subject = etree.SubElement(subj_group, "subject")
            subject.text = metadata_dict["Sachgebiet"]
        else:
            subject = etree.SubElement(subj_group, "subject")
            subject.text = metadata_dict["Fachbereich"]
            if "Sachgebiet" in metadata_dict:
                subj_subgroup = etree.SubElement(subj_group, "subj-group")
                subject = etree.SubElement(subj_subgroup, "subject")
                subject.text = metadata_dict["Sachgebiet"]

    # Title and Subtitles
    title_group = etree.SubElement(article_meta, "title-group")
    article_title = etree.SubElement(title_group, "article-title")
    if "Titel" in metadata_dict:
        article_title.text = metadata_dict["Titel"]
    for key in sorted(metadata_dict.keys()):
        if key.startswith("Untertitel"):
            subtitle = etree.SubElement(title_group, "subtitle")
            subtitle.text = metadata_dict[key]

    # Contributors (Authors)
    if "Autor" in metadata_dict or "Co-Autor" in metadata_dict:
        contrib_group = etree.SubElement(article_meta, "contrib-group")

        # Main Author
        if "Autor" in metadata_dict:
            contrib = etree.SubElement(contrib_group, "contrib")
            contrib.set("contrib-type", "Autor")
            name_dict = _parse_author_name(metadata_dict["Autor"])
            _add_author_to_contrib(contrib, name_dict)

        # Co-Authors
        if "Co-Autor" in metadata_dict:
            co_author_text = metadata_dict["Co-Autor"]
            # Parse co-authors - they are separated by semicolons
            co_authors = [ca.strip() for ca in co_author_text.split(";")]

            for co_author in co_authors:
                contrib = etree.SubElement(contrib_group, "contrib")
                contrib.set("contrib-type", "Co-Autor")
                name_dict = _parse_author_name(co_author)
                _add_author_to_contrib(contrib, name_dict)

    # Publication Dates
    date_mappings = [
        ("Ausgabe", "Ausgabedatum"),
        ("Aktualisierte Fassung", "AktualisierteFassung"),
        ("Korrekturdatum", "Korrekturdatum"),
        ("Erstveröffentlichung", "Erstveröffentlichung"),
    ]

    for date_key, date_type in date_mappings:
        if date_key in metadata_dict:
            # Parse date (format: YYYY-MM-DD)
            date_str = metadata_dict[date_key]
            date_parts = date_str.split("-")
            if len(date_parts) == 3:
                pub_date = etree.SubElement(article_meta, "pub-date")
                pub_date.set("date-type", date_type)

                year, month, day = date_parts

                day_elem = etree.SubElement(pub_date, "day")
                day_elem.text = day.lstrip("0") or "0"

                month_elem = etree.SubElement(pub_date, "month")
                month_elem.text = month.lstrip("0") or "0"

                year_elem = etree.SubElement(pub_date, "year")
                year_elem.text = year

    # Permissions
    permissions = etree.SubElement(article_meta, "permissions")
    if "Copyright" in metadata_dict:
        copyright_statement = etree.SubElement(permissions, "copyright-statement")
        copyright_statement.text = metadata_dict["Copyright"]

    if "Herausgeber" in metadata_dict:
        copyright_holder = etree.SubElement(permissions, "copyright-holder")
        copyright_holder.text = metadata_dict["Herausgeber"]

    # Self URI
    if "URL online Veröffentlichung" in metadata_dict:
        self_uri = etree.SubElement(article_meta, "self-uri")
        self_uri.set(f"{{{XLINK_NAMESPACE}}}href", metadata_dict["URL online Veröffentlichung"])

    # Abstracts
    short_abstract_key = None
    summary_abstract_key = None

    for key in metadata_dict.keys():
        if "Kurzbeschreibung" in key:
            short_abstract_key = key
        if "Detailbeschreibung" in key:
            summary_abstract_key = key

    if short_abstract_key:
        abstract = etree.SubElement(article_meta, "abstract")
        abstract.set("abstract-type", "short")
        title = etree.SubElement(abstract, "title")
        title.text = "Zusammenfassung"
        p = etree.SubElement(abstract, "p")
        p.text = metadata_dict[short_abstract_key]

    if summary_abstract_key:
        abstract = etree.SubElement(article_meta, "abstract")
        abstract.set("abstract-type", "summary")
        title = etree.SubElement(abstract, "title")
        title.text = "Zusammenfassung"
        p = etree.SubElement(abstract, "p")
        p.text = metadata_dict[summary_abstract_key]

    # Keywords
    keywords_key = None
    for key in metadata_dict.keys():
        if "Schlagworte" in key:
            keywords_key = key
            break

    if keywords_key:
        keywords_str = metadata_dict[keywords_key]
        keywords = [kw.strip() for kw in keywords_str.split(";")]

        kwd_group = etree.SubElement(article_meta, "kwd-group")
        kwd_group.set("kwd-group-type", "author-generated")

        for kwd in keywords:
            if kwd:
                kwd_elem = etree.SubElement(kwd_group, "kwd")
                kwd_elem.text = kwd

    # Custom metadata
    custom_meta_keys = [
        "Beschreibender Typ",
        "Bestellnummer",
        "Bisherige Bestellnummer",
        "Webcode",
        "Organisationseinheit",
        "Fachbereich",
        "Sachgebiet",
        "Status",
        "Bildnachweis",
        "Überschriften mit Nummerierung",
    ]

    has_custom_meta = any(key in metadata_dict for key in custom_meta_keys)
    if has_custom_meta:
        custom_meta_group = etree.SubElement(article_meta, "custom-meta-group")
        for key in custom_meta_keys:
            if key in metadata_dict:
                custom_meta = etree.SubElement(custom_meta_group, "custom-meta")
                meta_name = etree.SubElement(custom_meta, "meta-name")
                meta_name.text = key
                meta_value = etree.SubElement(custom_meta, "meta-value")
                meta_value.text = metadata_dict[key]
