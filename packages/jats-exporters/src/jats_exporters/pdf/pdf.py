"""PDF Exporter for JATS Documents."""

import base64
import datetime
import logging
import pathlib
from collections.abc import Callable
from typing import Any
from xml.etree import ElementTree

from bs4 import BeautifulSoup
from jats_classes import Front, JATSClassInterface, JATSDocument
from jinja2 import Template
from weasyprint import HTML
from ziamath import Math

from jats_exporters import HtmlExporter

logger = logging.getLogger(__name__)

ImageDownloader = Callable[[str], tuple[bytes, str]]


class PdfExporter:
    """Exporter that converts a JATSDocument to a PDF using WeasyPrint."""

    ROOT = pathlib.Path(__file__).parent.resolve()
    TEMPLATE = ROOT / "template.html"
    STYLE = ROOT / "style.css"

    html_exporter: HtmlExporter

    def __init__(self):
        """Initialize the PDF exporter with an HTML exporter."""
        self.html_exporter = HtmlExporter()

    def export(self, document: JATSDocument, pdf_variant: str = "pdf/ua-2") -> tuple[bytes, str]:
        """Export the JATSDocument to a PDF file using WeasyPrint.
        Returns:
            A tuple containing the PDF bytes and the suggested filename.
        """
        front = document.article.front
        html = HTML(string=self._get_html(document, front), base_url=f"{self.ROOT.as_uri()}/")
        pdf_bytes = html.write_pdf(pdf_variant=pdf_variant)

        title_escaped = "".join(c if c.isalnum() else "_" for c in front.title or "Dokument")
        filename = f"{title_escaped}.pdf"

        return pdf_bytes, filename

    def export_partial(
        self, part: JATSClassInterface, front: Front, pdf_variant: str = "pdf/ua-2"
    ) -> tuple[bytes, str]:
        """Export a part of the JATSDocument to a PDF file using WeasyPrint.
        Returns:
            A tuple containing the PDF bytes and the suggested filename.
        """
        html = HTML(string=self._get_html(part, front), base_url=f"{self.ROOT.as_uri()}/")
        pdf_bytes = html.write_pdf(pdf_variant=pdf_variant)

        title_escaped = "".join(c if c.isalnum() else "_" for c in front.title or "Dokument")
        filename = f"{title_escaped}.pdf"

        return pdf_bytes, filename

    def _get_html(self, part: JATSClassInterface, front: Front) -> str:
        """Load and render the HTML for PDF generation."""
        context = self._get_template_context(part, front)
        with open(self.TEMPLATE, encoding="utf-8") as template_file:
            template: Template = Template(template_file.read())
            return self._render_mathml(template.render(**context))

    def _render_mathml(self, html_content: str) -> str:
        """Typeset MathML as embedded vector images for WeasyPrint.

        WeasyPrint does not lay out MathML. Render at a reference font size
        and use em dimensions so equations scale with the surrounding text.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        formulas = soup.find_all("math")
        if not formulas:
            return html_content

        size = 16
        for formula in formulas:
            mathml = ElementTree.fromstring(str(formula))
            display = mathml.attrib.setdefault("display", "inline")
            equation = Math(mathml, size=size)
            svg = equation.svgxml()
            encoded = base64.b64encode(ElementTree.tostring(svg)).decode("ascii")
            image = soup.new_tag("img")
            image["src"] = f"data:image/svg+xml;base64,{encoded}"
            image["alt"] = formula.get("alttext") or formula.get_text(" ", strip=True)
            image["class"] = f"pdf-math pdf-math--{'block' if display == 'block' else 'inline'}"
            if formula.get("id"):
                image["id"] = formula["id"]
            width = float(svg.attrib["width"]) / size
            baseline = (equation.getyofst() - equation.margin) / size
            image["style"] = f"width: {width:.6f}em; vertical-align: {baseline:.6f}em;"
            formula.replace_with(image)
        return str(soup)

    def _get_template_context(self, part: JATSClassInterface, front: Front) -> dict[str, Any]:
        """Prepare the context for rendering the PDF template."""
        article_meta = front.to_dict()
        pdf_meta = {}
        css_content = self._get_css()

        if isinstance(part, JATSDocument):
            html_toc, _, _, html_content = self.html_exporter.export_parts(part)
            pdf_meta["is_partial"] = False
        else:
            html_content = self.html_exporter.export_partial(part)
            html_toc = None
            pdf_meta["is_partial"] = True

        pdf_meta["head_generator"] = "DGUV Vorschriften- und Regelwerk PDF"
        pdf_meta["head_author"] = "Deutsche Gesetzliche Unfallversicherung e. V. (DGUV)"
        pdf_meta["head_created"] = front.pub_date_ausgabedatum or front.pub_date_aktualisierte_fassung or "1970-01-01"
        pdf_meta["head_modified"] = front.pub_date_aktualisierte_fassung or front.pub_date_ausgabedatum or "1970-01-01"
        titles = [front.journal_title, front.journal_subtitle, front.article_id, front.title]
        pdf_meta["head_title"] = " - ".join(filter(None, titles)) if any(titles) else "DGUV-Dokument"

        pdf_meta["pub_date_ausgabedatum_german"] = self._to_german_date(front.pub_date_ausgabedatum)
        pdf_meta["pub_date_aktualisierte_fassung_german"] = self._to_german_date(front.pub_date_aktualisierte_fassung)

        pdf_meta["generated_at"] = self._to_german_date(datetime.datetime.now())

        # find impressum in html - should be rendered before the toc
        soup = BeautifulSoup(html_content, "html.parser")
        impressum = soup.find("div", attrs={"data-sec-type": "_4octextparaAnlageImpressum"})
        if impressum:
            html_impressum = str(impressum)
            impressum.decompose()
            html_content = str(soup)
        else:
            html_impressum = None

        return {
            "article_meta": article_meta,
            "pdf_meta": pdf_meta,
            "css_content": css_content,
            "html_toc": html_toc,
            "html_content": html_content,
            "html_impressum": html_impressum,
        }

    def _get_css(self) -> str:
        """Load the CSS for PDF generation."""
        with open(self.STYLE, encoding="utf-8") as css_file:
            return css_file.read()

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
