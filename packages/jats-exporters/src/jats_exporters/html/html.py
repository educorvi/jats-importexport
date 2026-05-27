import os
from functools import lru_cache

from jats_classes import JATSDocument
from lxml import etree

from jats_exporters.interface import Exporter
from jats_exporters.jats import JatsExporter

XSL_PATH = os.path.join(os.path.dirname(__file__), "jats-html.xsl")


class HtmlExporter(Exporter[str]):
    xsl_doc: etree._ElementTree
    jats_exporter: JatsExporter
    transform: etree.XSLT

    def __init__(self):
        xsl_path = os.path.abspath(XSL_PATH)
        self.xsl_doc = etree.parse(xsl_path)
        self.jats_exporter = JatsExporter()
        self.transform = etree.XSLT(self.xsl_doc)

    @lru_cache(maxsize=128)
    def _transform(self, xml_doc: str) -> str:
        parsed_xml_doc = etree.fromstring(xml_doc)
        return str(self.transform(parsed_xml_doc))

    @lru_cache(maxsize=128)
    def export(self, document: JATSDocument) -> str:
        return self._transform(self.jats_exporter.export(document))
