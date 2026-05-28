"""HTML exporter implementations utilizing XSLT stylesheets.

Defines exporters that process a JATSDocument into an HTML structure.
"""

import abc
import os
from functools import lru_cache

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

    @lru_cache(maxsize=128)
    def _transform(self, xml_doc: str) -> str:
        """Apply XSLT transformation to the JATS XML string and return the HTML."""
        parsed_xml_doc = etree.fromstring(xml_doc)
        return str(self.transform(parsed_xml_doc))

    @lru_cache(maxsize=128)
    def export(self, document: JATSDocument) -> str:
        """Export the JATSDocument into an HTML string representation."""
        return self._transform(self.jats_exporter.export(document))


class HtmlExporter(HtmlExporterGeneric):
    """Standard HTML exporter using 'jats-html.xsl'."""

    XSL_PATH = os.path.join(os.path.dirname(__file__), "jats-html.xsl")


class HtmlExporterStandalone(HtmlExporterGeneric):
    """Standalone HTML exporter using 'jats-html-standalone.xsl'."""

    XSL_PATH = os.path.join(os.path.dirname(__file__), "jats-html-standalone.xsl")

