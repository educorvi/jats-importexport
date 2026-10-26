"""JATS XML exporter implementation.

Serializes domain JATS class models (Article, Front, Body, Back, etc.) back into
valid XML format adhering to JATS schema requirements.
"""

from jats_classes import JATSDocument


class JatsExporter:
    """Exporter that converts a JATSDocument to its JATS XML string representation."""

    def export(self, document: JATSDocument) -> str:
        """Export the JATSDocument to XML string format."""
        return document.to_xml()
