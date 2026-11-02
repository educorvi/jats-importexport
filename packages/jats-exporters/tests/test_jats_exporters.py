import base64

import pytest
from bs4 import BeautifulSoup

from jats_classes import (
    Appendix,
    AppendixGroup,
    Article,
    Back,
    Body,
    Front,
    JATSDocument,
    Section,
    Glossary,
    RefList,
)
from jats_exporters import (
    HtmlExporter,
    HtmlExporterStandalone,
    JatsExporter,
    MarkdownExporter,
    PdfExporter,
)
from lxml import etree

# ----------------------------------------------------
# Helpers to build a mock JATSDocument
# ----------------------------------------------------


def create_mock_document() -> JATSDocument:
    front = Front.empty()
    front.title = "Exporter Test Article"

    sub_section = Section(
        sec_type="subsection",
        label_title_raw="<label>1.1</label><title>Sub-title</title>",
        content_raw="<p>Nested section content.</p>",
        sections=[],
    )

    main_section = Section(
        sec_type="intro",
        label_title_raw="<label>1.</label><title>Intro title</title>",
        content_raw="<p>Intro content.</p>",
        sections=[sub_section],
    )

    body = Body(sections=[main_section])

    app_sec = Section(
        sec_type=None,
        label_title_raw="<title>Appendix Subsection</title>",
        content_raw="<p>Appendix sub-content.</p>",
        sections=[],
    )

    appendix = Appendix(
        sec_type="annex",
        label_title_raw="<label>A</label><title>Annex Title</title>",
        content_raw="<p>Appendix raw content.</p>",
        sections=[app_sec],
    )

    glossary = Glossary(
        label_title_raw="<label>G</label><title>Glossary Title</title>",
        content_raw="<p>Glossary content.</p>",
    )

    ref_list = RefList(
        label_title_raw="<label>R</label><title>References</title>",
        content_raw="<p>Reference content.</p>",
    )

    app_group = AppendixGroup(
        sec_type="appendices",
        label_title_raw="<label>Group Label</label><title>Group Title</title>",
        content_raw="<p>Group content.</p>",
        sections=[appendix, ref_list],
    )

    back = Back(sections=[app_group, glossary])

    article = Article(front=front, body=body, back=back)
    return JATSDocument(article=article)




# ----------------------------------------------------
# Tests for HtmlExporter & HtmlExporterStandalone
# ----------------------------------------------------


def test_html_exporter_transform():
    doc = create_mock_document()
    exporter = HtmlExporter()

    html_output = exporter.export(doc)
    assert isinstance(html_output, str)
    # It should have transformed the JATS document to HTML.
    # The XSL stylesheet typically converts body, sections, titles, and paragraphs.
    assert "Intro title" in html_output
    assert "Annex Title" in html_output


def test_html_exporter_renders_nested_toc_sections():
    xml = etree.fromstring(
        b"""<article>
            <front/>
            <body>
                <sec id="parent" sec-type="intro">
                    <title>Parent section</title>
                    <sec id="child" sec-type="subsection"><title>Child section</title></sec>
                </sec>
            </body>
        </article>"""
    )

    html_output = str(HtmlExporter().transform(xml))
    soup = BeautifulSoup(html_output, "html.parser")
    toc = soup.select_one(".jats-html-export-toc")
    assert toc is not None
    parent = toc.find("a", href="#parent")
    assert parent is not None
    assert parent.get_text() == "Parent section"
    li = parent.find_parent("li")
    assert li is not None
    ul = li.select_one("ul a[href='#child']")
    assert ul is not None
    assert ul.get_text() == "Child section"


def test_html_exporter_styles_glossary_titles_like_section_titles():
    xml = etree.fromstring(
        b"""<article>
            <front/>
            <body>
                <sec id="section" sec-type="intro">
                    <title>Section title</title>
                    <glossary id="nested-glossary">
                        <label>N</label><title>Nested glossary</title>
                    </glossary>
                </sec>
                <glossary id="body-glossary">
                    <label>B</label><title>Body glossary</title>
                </glossary>
                <gloss-group id="gloss-group">
                    <label>G</label><title>Glossary group</title>
                    <glossary id="grouped-glossary"><title>Grouped glossary</title></glossary>
                </gloss-group>
            </body>
            <back>
                <title>Back title</title>
                <glossary id="back-glossary">
                    <label>R</label><title>Back glossary</title>
                </glossary>
            </back>
        </article>"""
    )

    soup = BeautifulSoup(str(HtmlExporter().transform(xml)), "html.parser")
    glossary_titles = {
        heading.get_text(" ", strip=True): heading.name
        for heading in soup.select("#article-body .glossary > .title")
    }
    glossary_labels = soup.select(
        "#article-body .glossary .label, #article-back > .section > .title .label"
    )

    heading = soup.select_one("#article-body > .section > h2.title")
    assert heading is not None
    assert heading.get_text(" ", strip=True) == "Section title"
    assert glossary_titles == {
        "N Nested glossary": "h3",
        "B Body glossary": "h2",
        "G Glossary group": "h2",
        "Grouped glossary": "h3",
    }
    heading = soup.select_one("#article-back > .section > h3.title")
    assert heading is not None
    assert heading.get_text(" ", strip=True) == "R Back glossary"
    assert [label.get_text(strip=True) for label in glossary_labels] == ["N", "B", "G", "R"]
    assert all(
        label.parent is not None and label.parent.name in {"h2", "h3"}
        for label in glossary_labels
    )


def test_html_exporter_renders_back_ref_list_and_nested_ref_list():
    xml = etree.fromstring(
        b"""<article>
            <front/>
            <body/>
            <back>
                <ref-list id="references">
                    <ref id="ref-one">
                        <label>1</label>
                        <mixed-citation>First citation.</mixed-citation>
                    </ref>
                    <ref-list id="online-references">
                        <title>Online references</title>
                        <ref id="ref-two">
                            <label>2</label>
                            <mixed-citation>Second citation.</mixed-citation>
                        </ref>
                    </ref-list>
                </ref-list>
            </back>
        </article>"""
    )

    soup = BeautifulSoup(str(HtmlExporter().transform(xml)), "html.parser")
    back = soup.select_one("#article-back")
    assert back is not None
    ref_list = back.select_one(".section.ref-list")
    assert ref_list is not None
    nested_ref_list = ref_list.select_one(".ref-list")
    assert nested_ref_list is not None

    heading = back.select_one("h2.main-title")
    assert heading is not None
    assert heading.get_text(" ", strip=True) == "Literaturverzeichnis"
    assert [item.get_text(" ", strip=True) for item in ref_list.select(":scope > ul > li")] == [
        "1 First citation."
    ]
    heading_nested = nested_ref_list.select_one(":scope > h3.title")
    assert heading_nested is not None
    assert heading_nested.get_text(" ", strip=True) == "Online references"
    assert [item.get_text(" ", strip=True) for item in nested_ref_list.select(":scope > ul > li")] == [
        "2 Second citation."
    ]


def test_html_exporter_standalone_transform():
    doc = create_mock_document()
    exporter = HtmlExporterStandalone()

    html_output = exporter.export(doc)
    assert isinstance(html_output, str)
    # Standalone stylesheet converts document to HTML with doctype, html, head, and body tags.
    assert "<!DOCTYPE html" in html_output or "<html" in html_output
    assert "Intro title" in html_output




@pytest.mark.parametrize("exporter_class", [HtmlExporter, HtmlExporterStandalone])
@pytest.mark.parametrize("prefix", ["mml:", "other:", ""])
@pytest.mark.parametrize("formula, display", [("disp-formula", "block"), ("inline-formula", "inline")])
def test_html_exporter_uses_unprefixed_mathml(exporter_class, prefix, formula, display):
    namespace = "http://www.w3.org/1998/Math/MathML"
    declaration = f"xmlns:{prefix[:-1]}" if prefix else "xmlns"
    math_xml = f"""<{prefix}math {declaration}="{namespace}" display="{display}">
        <{prefix}mrow><{prefix}mfrac>
            <{prefix}mi mathvariant="italic">E</{prefix}mi>
            <{prefix}mn>2</{prefix}mn>
        </{prefix}mfrac><{prefix}mo>≤</{prefix}mo><{prefix}mn>1</{prefix}mn></{prefix}mrow>
    </{prefix}math>"""
    xml = etree.fromstring(
        f"<article><body><p><{formula}>{math_xml}</{formula}></p></body></article>".encode()
    )

    result = exporter_class().transform(xml)
    math_nodes = result.xpath("//m:math", namespaces={"m": namespace})
    assert len(math_nodes) == 1
    math = math_nodes[0]
    assert math.get("display") == display
    for element in math.iter():
        assert etree.QName(element).namespace == namespace
        assert element.prefix is None
    assert math.find(f".//{{{namespace}}}mi").get("mathvariant") == "italic"
    assert math.find(f".//{{{namespace}}}mo").text == "≤"
    assert "<math " in str(result)
    assert "<mfrac>" in str(result)


def test_html_exporter_only_renders_non_empty_permissions():
    exporter = HtmlExporter()
    xml = etree.fromstring(
        b"""<article xmlns:xlink="http://www.w3.org/1999/xlink">
            <body>
                <fig id="empty"><graphic xlink:href="empty.png"/><permissions/></fig>
                <fig id="set">
                    <graphic xlink:href="set.png"/>
                    <permissions>
                        <copyright-statement>Example Copyright</copyright-statement>
                        <copyright-holder>Example GmbH</copyright-holder>
                    </permissions>
                </fig>
            </body>
        </article>"""
    )

    html_output = str(exporter.transform(xml))

    assert html_output.count('class="permissions"') == 1
    assert "Example Copyright" in html_output
    assert "Example GmbH" not in html_output


@pytest.mark.parametrize("display", ["inline", "block"])
def test_markdown_exporter_preserves_mathml(display, monkeypatch):
    math = (
        f"<math xmlns='http://www.w3.org/1998/Math/MathML' display='{display}'>\n"
        '  <mrow><mi>x_y</mi><mo>&lt;</mo><mn>2</mn></mrow>\n'
        '</math>'
    )
    second_math = '<math><mi>a*b</mi><mo>&amp;</mo><mi>c</mi></math>'
    html = f'<p><strong>Before</strong> {math} between {second_math} after.</p>'
    monkeypatch.setattr(HtmlExporter, "export", lambda self, document: html)

    result = MarkdownExporter().export(create_mock_document())

    assert result == f'**Before** {math} between {second_math} after.'


# ----------------------------------------------------
# Tests for PdfExporter image embedding
# ----------------------------------------------------


@pytest.fixture
def mathml_equation():
    return """<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" id="equation-1"
        alttext="Sum of squared field ratios is at most one">
        <mrow><munder><mo>∑</mo><mi mathvariant="italic">k</mi></munder>
        <msup><mrow><mo stretchy="false">(</mo><mfrac>
        <msub><mi mathvariant="italic">E</mi><mi mathvariant="italic">k</mi></msub>
        <msub><mi mathvariant="italic">E</mi><mrow><mi mathvariant="italic">a</mi>
        <mo>,</mo><mi mathvariant="italic">k</mi></mrow></msub>
        </mfrac><mo stretchy="false">)</mo></mrow><mn>2</mn></msup>
        <mo>≤</mo><mn>1</mn></mrow></math>"""


@pytest.mark.parametrize("display", ["block", "inline", None])
def test_pdf_exporter_typesets_mathml_as_svg(mathml_equation, display):
    equation = mathml_equation.replace('display="block"', f'display="{display}"' if display else "")
    exporter = PdfExporter()
    result = exporter._render_mathml(f"<p>Before {equation} after.</p>")
    soup = BeautifulSoup(result, "html.parser")

    assert soup.find("math") is None
    assert soup.p is not None
    assert soup.p.get_text() == "Before  after."
    image = soup.find("img", class_="pdf-math")
    assert image is not None
    assert f"pdf-math--{display or 'inline'}" in image["class"]
    assert image["id"] == "equation-1"
    assert image["alt"] == "Sum of squared field ratios is at most one"
    assert "vertical-align: -" in image["style"]
    svg = etree.fromstring(base64.b64decode(str(image["src"]).split(",", 1)[1]))
    assert svg.tag == "{http://www.w3.org/2000/svg}svg"
    width = svg.get("width")
    height = svg.get("height")
    assert width is not None and float(width) > 0
    assert height is not None and float(height) > 0
    assert svg.findall(".//{http://www.w3.org/2000/svg}path")


def test_pdf_exporter_renders_mathml_document(mathml_equation, monkeypatch, caplog):
    doc = create_mock_document()
    exporter = PdfExporter()
    fragment = exporter.html_exporter.transform_xml(f"<disp-formula>{mathml_equation}</disp-formula>")
    monkeypatch.setattr(exporter.html_exporter, "export", lambda document: fragment)

    html = exporter._get_html(doc, doc.article.front)
    assert "<math" not in html
    assert "data:image/svg+xml;base64," in html
    pdf, filename = exporter.export(doc)
    assert pdf.startswith(b"%PDF-")
    assert filename == "Exporter_Test_Article.pdf"
    assert not [record for record in caplog.records if record.levelname == "ERROR"]


def test_pdf_exporter_leaves_html_without_mathml_untouched():
    html = '<p>Text <img src="figure.png"></p>'
    assert PdfExporter()._render_mathml(html) == html


# def test_pdf_exporter_embeds_remote_images_as_data_uris():
#     calls = []

#     def fake_downloader(url: str) -> tuple[bytes, str]:
#         calls.append(url)
#         return b"fake-bytes", "image/png"

#     exporter = PdfExporter(image_downloader=fake_downloader)
#     html_content = '<div><img src="http://plone.example.com/assets/figure.png" alt=""></div>'

#     result = exporter._embed_remote_images(html_content)

#     assert calls == ["http://plone.example.com/assets/figure.png"]
#     assert "data:image/png;base64," in result
#     assert "http://plone.example.com/assets/figure.png" not in result


# def test_pdf_exporter_leaves_html_untouched_without_downloader():
#     exporter = PdfExporter()
#     html_content = '<div><img src="http://plone.example.com/assets/figure.png" alt=""></div>'

#     result = exporter._embed_remote_images(html_content)

#     assert result == html_content


# def test_pdf_exporter_skips_image_on_download_failure():
#     def failing_downloader(url: str) -> tuple[bytes, str]:
#         raise ValueError("outside of allowed domain")

#     exporter = PdfExporter(image_downloader=failing_downloader)
#     html_content = '<div><img src="http://evil.example.com/figure.png" alt=""></div>'

#     result = exporter._embed_remote_images(html_content)

#     # Left as-is; WeasyPrint will simply fail to load this one image.
#     assert "http://evil.example.com/figure.png" in result
