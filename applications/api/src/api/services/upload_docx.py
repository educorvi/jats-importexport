from pathlib import Path

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


def adapt_docx_xml(xml_tree: etree._Element, XML_NAMESPACE: str, XLINK_NAMESPACE: str, media_dir: Path) -> None:
    """Adapt the converted DOCX XML tree to conform to JATS structure and conventions."""

    # Before adding sec-type attributes to ensure correct labeling / numbering
    # Do not change the order of these function calls without testing
    _parse_and_add_metadata_to_docx_tree(xml_tree, XML_NAMESPACE, XLINK_NAMESPACE)
    has_toc = _remove_table_of_contents(xml_tree)
    _wrap_content_in_sections(xml_tree)
    _convert_textboxes_to_boxed_text(xml_tree)
    _update_image_names(xml_tree, XLINK_NAMESPACE, media_dir)
    _convert_graphics_to_figures(xml_tree, XLINK_NAMESPACE)
    _add_title_to_tables(xml_tree)

    _add_sec_type_to_sections(xml_tree)

    # After adding sec-type attributes (toc has no labels / numbering)
    if has_toc:
        _add_new_table_of_contents(xml_tree)


def _get_metadata_dict_from_docx_tree(xml_tree: etree._Element) -> dict[str, str]:
    """Extract metadata from the converted and parsed DOCX content represented as an lxml XML tree.
    The document must contain a table at the beginning with two columns.
    The table will be removed from the XML tree after extracting the metadata.
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

    # Remove the table from the XML tree after extracting metadata
    body.remove(table_wrap)

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


def _parse_and_add_metadata_to_docx_tree(xml_tree: etree._Element, XML_NAMESPACE: str, XLINK_NAMESPACE: str) -> None:
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


def _remove_table_of_contents(xml_tree: etree._Element) -> bool:
    """Remove the docx table of contents. Only works if the table of contents is
    the first element after the metadata table in the <body> section of the XML tree.
    """
    body = xml_tree.find("body")
    if body is None:
        return False
    if len(body) < 1 or body[0].tag != "sec":
        return False
    toc_sec = body[0]
    if toc_sec.attrib.get("id") != "inhaltsverzeichnis":
        return False

    if len(toc_sec) > 0 and (toc_title := toc_sec[0]).tag == "title":
        if toc_title.text:
            toc_title.text = toc_title.text + " (content)"
        else:
            toc_title.text = "Inhaltsverzeichnis (content)"

    is_in_toc = False
    for child in list(toc_sec):
        if child.tag == "p" and len(child) == 1 and child[0].tag == "xref":
            is_in_toc = True
            toc_sec.remove(child)
        elif is_in_toc:
            break
    return True


XML_TOC = """<sec sec-type="_1KapitelUeberschrift">
    <title>
        <named-content content-type="span" specific-use="keyword">Inhaltsverzeichnis</named-content>
    </title>
    <?dguv toc?>
    <p><?dguv pbr6?></p>
</sec>"""


def _add_new_table_of_contents(xml_tree: etree._Element) -> None:
    """Add a new table of contents in the converted DOCX content represented as an lxml XML tree
    with the typical JATS table of contents structure.
    """
    body = xml_tree.find("body")
    if body is None:
        return
    new_toc_sec = etree.fromstring(XML_TOC)
    body.insert(0, new_toc_sec)


def _get_sec_type_from_level(level: int) -> str | None:
    """Return the sec-type string based on the level of the section."""
    if level < 1:
        return None
    if level == 1:
        return "_1KapitelUeberschrift"
    else:
        return f"_1Ueberschrift{level}"


def _get_sec_label(parent_label: str, number: int) -> str:
    """Return the label string for the section based on the parent label and the section number."""
    if parent_label:
        return f"{parent_label}.{number}"
    else:
        return str(number)


def _add_sec_type_to_sections(xml_tree: etree._Element) -> None:
    """Add sec-type attributes to all <sec> elements in the XML tree based on their level.
    Embed the title of the section in a <named-content> element with content-type="span" and specific-use="keyword".
    Add a label based on the level.
    """
    body = xml_tree.find("body")
    if body is None:
        return
    _add_sec_type_to_sections_helper(body)


def _add_sec_type_to_sections_helper(xml_tree: etree._Element, level: int = 1, parent_label: str = "") -> None:
    """Helper function to recursively add sec-type attributes to <sec> elements."""
    for sec_num, sec in enumerate(xml_tree.findall("sec")):
        sec_type = _get_sec_type_from_level(level)
        if sec_type:
            sec.set("sec-type", sec_type)

        title_elem = sec.find("title")
        if title_elem is not None and title_elem.text:
            named_content = etree.Element("named-content")
            named_content.set("content-type", "span")
            named_content.set("specific-use", "keyword")
            named_content.text = title_elem.text
            title_elem.clear()
            title_elem.append(named_content)

        label = _get_sec_label(parent_label, sec_num + 1)
        label_elem = etree.Element("label")
        label_elem.text = label
        sec.insert(0, label_elem)

        _add_sec_type_to_sections_helper(sec, level + 1, label)


def _extract_textbox_metadata(table_wrap: etree._Element) -> dict:
    """Extract metadata from a textbox table-wrap element.

    Returns a dictionary with:
    - content_type: The box type (e.g., "oct_ext_Blau")
    - title: The title of the textbox
    - keywords: List of keywords
    """
    metadata: dict[str, str | list[str] | None] = {
        "content_type": None,
        "title": None,
        "keywords": [],
    }

    table = table_wrap.find("table")
    if table is None:
        return metadata

    tbody = table.find("tbody")
    if tbody is None:
        return metadata

    rows = tbody.findall("tr")
    if len(rows) < 2:
        return metadata

    # First row contains metadata tables (Box-Type and Title/Keywords)
    first_row = rows[0]
    first_td = first_row.find("td")
    if first_td is None:
        return metadata

    # Extract Box-Type from first metadata table
    metadata_tables = first_td.findall(".//table-wrap")
    for meta_table_wrap in metadata_tables:
        meta_table = meta_table_wrap.find("table")
        if meta_table is None:
            continue

        # Look for the Box-Type table
        thead = meta_table.find("thead")
        if thead is not None:
            header_row = thead.find("tr")
            if header_row is not None:
                header_cell = header_row.find("th")
                if header_cell is not None:
                    header_text = "".join(str(t) for t in header_cell.itertext()).strip()

                    # This is the Box-Type table
                    if "Box-Type" in header_text:
                        meta_tbody = meta_table.find("tbody")
                        if meta_tbody is not None:
                            # Look for rows with box types and check which one is marked
                            for row in meta_tbody.findall("tr"):
                                cells = row.findall("td")
                                if len(cells) >= 2:
                                    box_type_text = "".join(str(t) for t in cells[0].itertext()).strip()
                                    is_marked = "".join(str(t) for t in cells[1].itertext()).strip()
                                    # Check if this is marked (has content in second cell)
                                    if is_marked and box_type_text:
                                        metadata["content_type"] = box_type_text
                                        break

                    # This is the Metadata table (Title and Keywords)
                    elif "Metadaten" in header_text:
                        meta_tbody = meta_table.find("tbody")
                        if meta_tbody is not None:
                            for row in meta_tbody.findall("tr"):
                                cells = row.findall("td")
                                if len(cells) >= 2:
                                    key = "".join(str(t) for t in cells[0].itertext()).strip()
                                    value = "".join(str(t) for t in cells[1].itertext()).strip()

                                    if key == "Titel":
                                        metadata["title"] = value
                                    elif key == "Stichwörter":
                                        # Split keywords by comma
                                        keywords = [kw.strip() for kw in value.split(",")]
                                        metadata["keywords"] = keywords

    return metadata


def _convert_textboxes_to_boxed_text(xml_tree: etree._Element) -> None:
    """Convert textboxes represented as <table-wrap> elements in the XML tree to <boxed-text> elements."""
    body = xml_tree.find("body")
    if body is None:
        return
    _convert_textboxes_to_boxed_text_helper(body)


def _convert_textboxes_to_boxed_text_helper(xml_tree: etree._Element) -> None:
    """Helper function to recursively convert textboxes to boxed-text."""
    indices_to_replace = []

    for index, child in enumerate(list(xml_tree)):
        if child.tag == "table-wrap":
            table = child.find("table")
            if table is None:
                _convert_textboxes_to_boxed_text_helper(child)
                continue

            thead = table.find("thead")
            if thead is None:
                _convert_textboxes_to_boxed_text_helper(child)
                continue

            first_row = thead.find("tr")
            if first_row is None:
                _convert_textboxes_to_boxed_text_helper(child)
                continue

            first_cell = first_row.find("th")
            if first_cell is None:
                first_cell = first_row.find("td")

            if first_cell is None:
                _convert_textboxes_to_boxed_text_helper(child)
                continue

            header_text = "".join(str(t) for t in first_cell.itertext()).strip()

            # Check if this is a textbox (header contains "Textbox:")
            if not header_text.startswith("Textbox"):
                _convert_textboxes_to_boxed_text_helper(child)
                continue

            # This is a textbox - extract metadata
            metadata = _extract_textbox_metadata(child)

            # Get the content from the second row (the list)
            tbody = table.find("tbody")
            if tbody is None:
                _convert_textboxes_to_boxed_text_helper(child)
                continue

            rows = tbody.findall("tr")
            if len(rows) < 2:
                _convert_textboxes_to_boxed_text_helper(child)
                continue

            # Second row contains the actual content
            content_row = rows[1]
            content_td = content_row.find("td")
            if content_td is None:
                _convert_textboxes_to_boxed_text_helper(child)
                continue

            # Find the content (can be any element or multiple elements)
            if len(content_td) == 0:
                _convert_textboxes_to_boxed_text_helper(child)
                continue

            # Create the boxed-text element
            boxed_text = etree.Element("boxed-text")
            if metadata["content_type"]:
                boxed_text.set("content-type", metadata["content_type"])

            # Add sec-meta with keywords
            if metadata["keywords"]:
                sec_meta = etree.SubElement(boxed_text, "sec-meta")
                kwd_group = etree.SubElement(sec_meta, "kwd-group")
                for kwd in metadata["keywords"]:
                    kwd_elem = etree.SubElement(kwd_group, "kwd")
                    kwd_elem.text = kwd

            # Add caption with title
            if metadata["title"]:
                caption = etree.SubElement(boxed_text, "caption")
                title_elem = etree.SubElement(caption, "title")
                title_elem.text = metadata["title"]

            # Copy all content elements from the content_td
            for content_elem in content_td:
                content_copy = etree.fromstring(etree.tostring(content_elem))
                boxed_text.append(content_copy)

            # Replace the table-wrap with boxed-text
            indices_to_replace.append((index, boxed_text))
        else:
            _convert_textboxes_to_boxed_text_helper(child)

    # Replace in reverse order to maintain indices
    for index, boxed_text in reversed(indices_to_replace):
        xml_tree.remove(list(xml_tree)[index])
        xml_tree.insert(index, boxed_text)


def _wrap_content_in_sections(xml_tree: etree._Element) -> None:
    """Wrap all content in the <body> section that is currently not inside a <sec> element into new <sec> elements
    with sec-type="_1KapitelUeberschrift"."""
    body = xml_tree.find("body")
    if body is None:
        return

    new_sec = None
    for child in list(body):
        if child.tag != "sec":
            if new_sec is None:
                new_sec = etree.Element("sec")
                new_sec.set("sec-type", "_1KapitelUeberschrift")
                body.insert(body.index(child), new_sec)
            body.remove(child)
            new_sec.append(child)
        else:
            new_sec = None


def _update_image_names(xml_tree: etree._Element, XLINK_NAMESPACE: str, media_dir: Path) -> None:
    """Rename all local file references in xlink:href attributes by prefixing the filename
    with the article ID extracted from <front><article-meta><article-id>.
    The corresponding files in media_dir are also renamed to match.
    """
    # Extract article ID
    article_id_elem = xml_tree.find("front/article-meta/article-id")
    if article_id_elem is None or not article_id_elem.text:
        return
    article_id = article_id_elem.text.strip()
    if not article_id:
        return
    # replace all invalid characters in article_id with underscores for filenames
    article_id = "".join(c if c.isalnum() else "_" for c in article_id)

    href_attr = f"{{{XLINK_NAMESPACE}}}href"
    renamed_files: dict[str, str] = {}

    for element in xml_tree.iterfind(".//*[@xlink:href]", namespaces={"xlink": XLINK_NAMESPACE}):
        href_value = element.get(href_attr)
        if not href_value or href_value.startswith("#") or "://" in href_value:
            continue

        href_path = Path(href_value)
        original_filename = href_path.name
        new_filename = f"{article_id}_{original_filename}"
        new_href = str(href_path.parent / new_filename)
        new_path = Path(new_href)

        # Rename the actual file on disk if not already renamed
        if href_value not in renamed_files:
            if href_path.is_file() and not new_path.exists():
                href_path.rename(new_path)
            renamed_files[href_value] = new_href

        element.set(href_attr, renamed_files[href_value])


def _convert_graphics_to_figures(xml_tree: etree._Element, XLINK_NAMESPACE: str) -> None:
    """Convert all standalone <graphic> elements in the XML tree to <fig> elements.
    Expects the next sibling of each <graphic> to be a <p> with the pattern #label# caption text.
    """
    body = xml_tree.find("body")
    if body is None:
        return
    _convert_graphics_to_figures_helper(body, XLINK_NAMESPACE)


def _convert_graphics_to_figures_helper(xml_tree: etree._Element, XLINK_NAMESPACE: str) -> None:
    """Recursively find and convert standalone <graphic> elements to <fig> elements."""
    indices_to_replace: list[int] = []

    for i, child in enumerate(list(xml_tree)):
        if child.tag == "graphic":
            indices_to_replace.append(i)
        else:
            _convert_graphics_to_figures_helper(child, XLINK_NAMESPACE)

    for i in reversed(indices_to_replace):
        children = list(xml_tree)
        graphic = children[i]
        next_sibling = children[i + 1] if i + 1 < len(children) else None

        # Extract alt-text from graphic child element
        alt_text_elem = graphic.find("alt-text")
        alt_text = " ".join(str(t) for t in alt_text_elem.itertext()).strip() if alt_text_elem is not None else None

        # Extract label and caption from next sibling paragraph with pattern #label# caption
        label_text = None
        caption_text = None
        caption_p = None

        if next_sibling is not None and next_sibling.tag == "p":
            p_text = " ".join(str(t) for t in next_sibling.itertext()).strip()
            if p_text.startswith("#"):
                end_label = p_text.find("#", 1)
                if end_label != -1:
                    label_text = p_text[1:end_label].strip()
                    caption_text = p_text[end_label + 1 :].strip()
                    caption_p = next_sibling

        # Create <fig> element
        fig = etree.Element("fig")

        # Add label
        if label_text:
            label_elem = etree.SubElement(fig, "label")
            label_elem.text = label_text

        # Add caption with sentence breaks as <named-content specific-use="br"/>
        if caption_text:
            caption_elem = etree.SubElement(fig, "caption")
            title_elem = etree.SubElement(caption_elem, "title")
            title_elem.text = caption_text

        # Add alt-text (moved out of graphic)
        if alt_text:
            alt_elem = etree.SubElement(fig, "alt-text")
            alt_elem.text = alt_text

        # Add graphic (copy all attributes, add specific-use, omit alt-text child)
        new_graphic = etree.Element("graphic")
        for attr_name, attr_value in graphic.attrib.items():
            new_graphic.set(attr_name, attr_value)
        # new_graphic.set("specific-use", "image-size:l")
        fig.append(new_graphic)

        # Add empty permissions
        etree.SubElement(fig, "permissions")

        # Remove caption paragraph and replace graphic with fig
        if caption_p is not None:
            xml_tree.remove(caption_p)
        xml_tree.remove(graphic)
        xml_tree.insert(i, fig)


def _add_title_to_tables(xml_tree: etree._Element) -> None:
    """Add <label>, <caption> and <title> elements to <table-wrap> elements
    if a title exists as the previous sibling.
    """
    body = xml_tree.find("body")
    if body is None:
        return
    _add_title_to_tables_helper(body)


def _add_title_to_tables_helper(xml_tree: etree._Element) -> None:
    """Recursively add titles to <table-wrap> elements."""
    indices_to_process: list[int] = []

    for i, child in enumerate(list(xml_tree)):
        if child.tag == "table-wrap":
            indices_to_process.append(i)
        else:
            _add_title_to_tables_helper(child)

    for i in reversed(indices_to_process):
        children = list(xml_tree)
        table_wrap = children[i]
        prev_sibling = children[i - 1] if i > 0 else None

        # Check if previous sibling is a <p> with text (the title)
        if prev_sibling is not None and prev_sibling.tag == "p":
            title_text = " ".join(str(t) for t in prev_sibling.itertext()).strip()
            if title_text.startswith("#"):
                end_label = title_text.find("#", 1)
                if end_label != -1:
                    label_text = title_text[1:end_label].strip()
                    title_text = title_text[end_label + 1 :].strip()

                    # Create <label> element
                    if label_text:
                        label_elem = etree.Element("label")
                        label_elem.text = label_text
                        table_wrap.insert(0, label_elem)

                    # Create <caption> and <title> elements
                    if title_text:
                        caption_elem = etree.Element("caption")
                        title_elem = etree.SubElement(caption_elem, "title")
                        title_elem.text = title_text
                        table_wrap.insert(0, caption_elem)

                    # Remove the previous sibling paragraph
                    xml_tree.remove(prev_sibling)
