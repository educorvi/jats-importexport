from functools import lru_cache

from jats_classes import JATSDocument
from markdownify import markdownify as md

from .html import HtmlExporter
from .interface import Exporter


class MarkdownExporter(Exporter):
    @lru_cache(maxsize=128)
    def export(self, document: JATSDocument) -> str:
        html = HtmlExporter().export(document)
        return md(html)
