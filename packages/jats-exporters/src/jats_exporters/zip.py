"""ZIP exporter for JATS documents and their referenced media."""

import io
import zipfile

from jats_classes import JATSDocument

from .html import HtmlExporterStandalone
from .jats import JatsExporter
from .markdown import MarkdownExporter
from .pdf import PdfExporter


class ZipExporter:
    """Export a JATS document, its other formats, and its referenced media."""

    def __init__(self):
        self.jats_exporter = JatsExporter()
        self.html_exporter = HtmlExporterStandalone()
        self.markdown_exporter = MarkdownExporter()
        self.pdf_exporter = PdfExporter()

    def export(
        self,
        document: JATSDocument,
        document_for_pdf: JATSDocument,
        media: dict[str, tuple[str, tuple[bytes, str] | None]],
    ) -> tuple[bytes, str]:
        """Return a ZIP archive and its suggested filename."""
        base_name = self._get_base_name(document)
        jats_content = self.jats_exporter.export(document)
        html_content = self.html_exporter.export(document)
        markdown_content = self.markdown_exporter.export(document)
        pdf_content, _ = self.pdf_exporter.export(document_for_pdf)

        archive = io.BytesIO()
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f"{base_name}.xml", jats_content.encode("utf-8"))
            zip_file.writestr(f"{base_name}.html", html_content.encode("utf-8"))
            zip_file.writestr(f"{base_name}.md", markdown_content.encode("utf-8"))
            zip_file.writestr(f"{base_name}.pdf", pdf_content)
            for filename, media_content in media.values():
                if media_content is not None:
                    content, _ = media_content
                    zip_file.writestr(filename, content)

        return archive.getvalue(), f"{base_name}.zip"

    @staticmethod
    def _get_base_name(document: JATSDocument) -> str:
        name = document.article.front.article_id or document.article.front.title or ""
        base_name = "".join(character if character.isalnum() else "_" for character in name)
        return base_name or "Dokument"
