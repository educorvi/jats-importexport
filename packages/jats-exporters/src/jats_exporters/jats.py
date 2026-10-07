"""JATS XML exporter implementation.

Serializes domain JATS class models (Article, Front, Body, Back, etc.) back into
valid XML format adhering to JATS schema requirements.
"""

from functools import lru_cache

from jats_classes import JATSDocument

from .interface import Exporter


class JatsExporter(Exporter[str]):
    """Exporter that converts a JATSDocument to its JATS XML string representation."""

    @lru_cache(maxsize=128)
    def export(self, document: JATSDocument) -> str:
        """Export the JATSDocument to XML string format."""
        return document.to_xml()
