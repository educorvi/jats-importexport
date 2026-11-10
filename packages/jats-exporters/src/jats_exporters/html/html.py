"""HTML exporter implementations utilizing XSLT stylesheets.

Defines exporters that process a JATSDocument into an HTML structure.
"""

import abc
import os
import re

from bs4 import BeautifulSoup
from jats_classes import JATSClassInterface, JATSDocument
from lxml import etree

from jats_exporters.jats import JatsExporter


class HtmlExporterGeneric(metaclass=abc.ABCMeta):
    """Generic base class for XSLT-based HTML exporters.

    Provides core transformation logic and caching for sub-classes which define
    a specific stylesheet path.
    """

    xsl_doc: etree._ElementTree
    jats_exporter: JatsExporter
    transform: etree.XSLT

    @property
    @abc.abstractmethod
    def XSL_PATH(self) -> str:
        """Get the absolute file path to the XSLT stylesheet used for conversion."""
        raise NotImplementedError("Subclasses must implement XSL_PATH property")

    def __init__(self):
        """Initialize the HTML exporter by loading the XSLT stylesheet and parser."""
        xsl_path = os.path.abspath(self.XSL_PATH)
        self.xsl_doc = etree.parse(xsl_path)
        self.jats_exporter = JatsExporter()
        self.transform = etree.XSLT(self.xsl_doc)

    def _transform(self, xml_doc: str) -> str:
        """Apply XSLT transformation to the JATS XML string and return the HTML."""
        parsed_xml_doc = etree.fromstring(xml_doc)
        return str(self.transform(parsed_xml_doc))

    def _remove_doctype(self, html_content: str) -> str:
        """Remove the <!DOCTYPE html> declaration from the HTML content."""
        return re.sub(r"<!DOCTYPE[^>]*>\s*", "", html_content, flags=re.IGNORECASE)

    def _add_doctype(self, html_content: str) -> str:
        """Add the <!DOCTYPE html> declaration to the HTML content if not already present."""
        html_content = self._remove_doctype(html_content)
        return "<!DOCTYPE html>\n" + html_content

    def transform_xml(self, xml_doc: str) -> str:
        """Apply XSLT transformation to the JATS XML string.
        The XML string does not need to have a single root element.
        The returned HTML string does not include the <!DOCTYPE html> declaration.
        """
        wrapped_xml = f"<root>{xml_doc}</root>"
        html_content = self._transform(wrapped_xml)
        return self._remove_doctype(html_content)

    def export(self, document: JATSDocument) -> str:
        """Export the JATSDocument into an HTML string representation."""
        xml_doc = self.jats_exporter.export(document)
        html_content = self._transform(xml_doc)
        return self._add_doctype(html_content)

    def export_partial(self, part: JATSClassInterface) -> str:
        """Export a partial JATS class instance into an HTML string representation."""
        xml_doc = self.jats_exporter.export_partial(part)
        html_content = self._transform(xml_doc)
        return self._remove_doctype(html_content)


class HtmlExporter(HtmlExporterGeneric):
    """Standard HTML exporter using 'jats-html.xsl'."""

    @property
    def XSL_PATH(self) -> str:
        return os.path.join(os.path.dirname(__file__), "jats-html.xsl")

    def export_parts(self, document: JATSDocument) -> tuple[str, str, str, str]:
        """Export the JATSDocument into its individual parts as HTML strings.
        Returns a tuple containing the toc, header, metadata and content HTML strings.
        """
        xml_doc = self.jats_exporter.export(document)
        html_content = self._transform(xml_doc)
        soup = BeautifulSoup(html_content, "html.parser")
        toc = soup.find_all("nav", class_="article-toc")
        header = soup.find_all("div", class_="article-header")
        metadata = soup.find_all("table", class_="article-metadata")
        content = soup.find_all("div", class_="article-content")
        if (
            toc is None
            or len(toc) == 0
            or header is None
            or len(header) == 0
            or metadata is None
            or len(metadata) == 0
            or content is None
            or len(content) == 0
        ):
            raise ValueError("One or more required HTML parts are missing.")

        return str(toc[0]), str(header[0]), str(metadata[0]), str(content[0])


class HtmlExporterStandalone(HtmlExporterGeneric):
    """Standalone HTML exporter using 'jats-html-standalone.xsl'."""

    @property
    def XSL_PATH(self) -> str:
        return os.path.join(os.path.dirname(__file__), "jats-html-standalone.xsl")
