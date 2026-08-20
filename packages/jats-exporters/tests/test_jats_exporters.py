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
from jats_exporters import (
    HtmlExporter,
    HtmlExporterStandalone,
    JatsExporter,
)

# ----------------------------------------------------
# Helpers to build a mock JATSDocument
# ----------------------------------------------------


def create_mock_document() -> JATSDocument:
    front = Front(
        content_raw="<article-meta><title-group><article-title>Exporter Test Article</article-title></title-group></article-meta>"
    )

    sub_section = Section(
        sec_type="subsection",
        label="1.1",
        title="Sub-title",
        label_title_raw="<label>1.1</label><title>Sub-title</title>",
        content_raw="<p>Nested section content.</p>",
        sections=[],
    )

    main_section = Section(
        sec_type="intro",
        label="1.",
        title="Intro title",
        label_title_raw="<label>1.</label><title>Intro title</title>",
        content_raw="<p>Intro content.</p>",
        sections=[sub_section],
    )

    body = Body(sections=[main_section])

    app_sec = Section(
        sec_type=None,
        label=None,
        title="Appendix Subsection",
        label_title_raw="<title>Appendix Subsection</title>",
        content_raw="<p>Appendix sub-content.</p>",
        sections=[],
    )

    appendix = Appendix(
        sec_type="annex",
        label="A",
        title="Annex Title",
        label_title_raw="<label>A</label><title>Annex Title</title>",
        content_raw="<p>Appendix raw content.</p>",
        sections=[app_sec],
    )

    app_group = AppendixGroup(
        sec_type="appendices",
        label="Group Label",
        title="Group Title",
        label_title_raw="<label>Group Label</label><title>Group Title</title>",
        content_raw="<p>Group content.</p>",
        appendixes=[appendix],
    )

    back = Back(appendix_groups=[app_group])

    article = Article(front=front, body=body, back=back)
    return JATSDocument(article=article)


# ----------------------------------------------------
# Tests for JatsExporter
# ----------------------------------------------------


def test_jats_exporter_caching():
    doc = create_mock_document()
    exporter = JatsExporter()

    # Clear cache first to be absolutely clean
    exporter.export.cache_clear()

    xml1 = exporter.export(doc)
    # The cache should now have 1 item
    info = exporter.export.cache_info()
    assert info.misses == 1
    assert info.hits == 0

    xml2 = exporter.export(doc)
    # This call should be a cache hit
    info = exporter.export.cache_info()
    assert info.misses == 1
    assert info.hits == 1
    assert xml1 == xml2


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


def test_html_exporter_standalone_transform():
    doc = create_mock_document()
    exporter = HtmlExporterStandalone()

    html_output = exporter.export(doc)
    assert isinstance(html_output, str)
    # Standalone stylesheet converts document to HTML with doctype, html, head, and body tags.
    assert "<!DOCTYPE html" in html_output or "<html" in html_output
    assert "Intro title" in html_output


def test_html_exporter_caching():
    doc = create_mock_document()
    exporter = HtmlExporter()

    # Clear lru_cache on both export and internal _transform
    exporter.export.cache_clear()
    exporter._transform.cache_clear()

    html1 = exporter.export(doc)
    info_export = exporter.export.cache_info()
    assert info_export.misses == 1
    assert info_export.hits == 0

    html2 = exporter.export(doc)
    info_export2 = exporter.export.cache_info()
    assert info_export2.misses == 1
    assert info_export2.hits == 1
    assert html1 == html2
