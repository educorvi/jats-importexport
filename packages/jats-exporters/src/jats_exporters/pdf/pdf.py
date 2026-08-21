"""PDF Exporter for JATS Documents."""

import datetime
import pathlib
from functools import lru_cache
from typing import Any

from bs4 import BeautifulSoup
from jats_classes import JATSDocument
from jinja2 import Template
from weasyprint import HTML

from jats_exporters import Exporter, HtmlExporter


class PdfExporter(Exporter[str]):
    """Exporter that converts a JATSDocument to a PDF using WeasyPrint."""

    ROOT = pathlib.Path(__file__).parent.resolve()
    TEMPLATE = ROOT / "template.html"
    STYLE = ROOT / "style.css"

    html_exporter: HtmlExporter

    def __init__(self):
        """Initialize the PDF exporter with an HTML exporter."""
        self.html_exporter = HtmlExporter()

    @lru_cache(maxsize=128)
    def export(self, document: JATSDocument) -> tuple[bytes, str]:
        """Export the JATSDocument to a PDF file using WeasyPrint.
        Returns:
            A tuple containing the PDF bytes and the suggested filename.
        """
        template_context = self._get_template_context(document)
        html = HTML(string=self._get_html(template_context), base_url=f"{self.ROOT.as_uri()}/")
        pdf_bytes = html.write_pdf()

        title_escaped = "".join(c if c.isalnum() else "_" for c in document.article.front.title or "Dokument")
        filename = f"{title_escaped}.pdf"

        return pdf_bytes, filename

    def _get_html(self, context: dict[str, Any]) -> str:
        """Load and render the HTML for PDF generation."""
        with open(self.TEMPLATE, encoding="utf-8") as template_file:
            template: Template = Template(template_file.read())
            return template.render(**context)

    def _get_template_context(self, document: JATSDocument) -> dict[str, Any]:
        """Prepare the context for rendering the PDF template."""
        front = document.article.front
        article_metadata = front.to_dict()
        article_metadata["pub_date_ausgabedatum_german"] = self._to_german_date(front.pub_date_ausgabedatum)
        article_metadata["pub_date_aktualisierte_fassung_german"] = self._to_german_date(
            front.pub_date_aktualisierte_fassung
        )

        html_content = self.html_exporter.export(document)
        css = self._get_css()

        toc_html = self._get_toc_html(html_content)

        generated_at = self._to_german_date(datetime.datetime.now())

        return {
            "metadata": article_metadata,
            "css_content": css,
            "html_content": html_content,
            "tocHtml": toc_html,
            "generated_at": generated_at,
        }

    def _get_css(self) -> str:
        """Load the CSS for PDF generation."""
        with open(self.STYLE, encoding="utf-8") as css_file:
            return css_file.read()

    def _get_toc_html(self, html_content: str) -> str:
        """Extract the table of contents from the HTML content."""
        soup = BeautifulSoup(html_content, "html.parser")
        toc_div = soup.find("nav", class_="jats-html-export-toc")
        return str(toc_div) if toc_div else ""

    def _to_german_date(self, date_obj: datetime.date | datetime.datetime | None) -> str | None:
        """Convert a datetime.date object to a German date string (DD. MMMM YYYY)."""
        if date_obj is None:
            return None
        GERMAN_MONTHS = {
            1: "Januar",
            2: "Februar",
            3: "März",
            4: "April",
            5: "Mai",
            6: "Juni",
            7: "Juli",
            8: "August",
            9: "September",
            10: "Oktober",
            11: "November",
            12: "Dezember",
        }
        if isinstance(date_obj, datetime.datetime):
            return f"{date_obj.strftime('%d.')} {GERMAN_MONTHS[date_obj.month]} {date_obj.strftime('%Y %H:%M:%S')}"
        else:
            return f"{date_obj.strftime('%d.')} {GERMAN_MONTHS[date_obj.month]} {date_obj.strftime('%Y')}"
