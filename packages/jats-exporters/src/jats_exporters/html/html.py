"""HTML exporter implementations utilizing XSLT stylesheets.

Defines exporters that process a JATSDocument into an HTML structure.
"""

import abc
import os
import re
from functools import lru_cache
from urllib.parse import unquote

from jats_classes import JATSDocument
from lxml import etree

from jats_exporters.interface import Exporter
from jats_exporters.jats import JatsExporter


class HtmlExporterGeneric(Exporter[str], metaclass=abc.ABCMeta):
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

    def _replace_related_article_links(self, html: str, doc: JATSDocument) -> str:
        # get all hrefs
        hrefs = re.findall(r'href="([^"]+)"', html)
        for href in hrefs:
            unquoted_href = unquote(href)
            for related_article in doc.related_articles:
                if unquoted_href == related_article[2].article_id:
                    new_href = related_article[1]
                    html = html.replace(f'href="{href}"', f'href="{new_href}"')
                    break
        return html

    @lru_cache(maxsize=128)
    def _transform(self, xml_doc: str, doc: JATSDocument) -> str:
        """Apply XSLT transformation to the JATS XML string and return the HTML."""
        parsed_xml_doc = etree.fromstring(xml_doc)
        html = str(self.transform(parsed_xml_doc))
        html = self._replace_related_article_links(html, doc)
        return html

    @lru_cache(maxsize=128)
    def transform_xml(self, xml_doc: str) -> str:
        """Apply XSLT transformation to the JATS XML string.
        The XML string does not need to have a single root element.
        The returned HTML string does not include the <!DOCTYPE html> declaration.
        """
        wrapped_xml = f"<root>{xml_doc}</root>"
        html_content = self._transform(wrapped_xml)
        return re.sub(r"<!DOCTYPE[^>]*>\s*", "", html_content, flags=re.IGNORECASE)

    @lru_cache(maxsize=128)
    def export(self, document: JATSDocument) -> str:
        """Export the JATSDocument into an HTML string representation."""
        return self._transform(self.jats_exporter.export(document), doc=document)


class HtmlExporter(HtmlExporterGeneric):
    """Standard HTML exporter using 'jats-html.xsl'."""

    XSL_PATH = os.path.join(os.path.dirname(__file__), "jats-html.xsl")


class HtmlExporterStandalone(HtmlExporterGeneric):
    """Standalone HTML exporter using 'jats-html-standalone.xsl'."""

    XSL_PATH = os.path.join(os.path.dirname(__file__), "jats-html-standalone.xsl")
