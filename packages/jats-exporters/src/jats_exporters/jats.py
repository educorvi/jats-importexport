"""JATS XML exporter implementation.

Serializes domain JATS class models (Article, Front, Body, Back, etc.) back into
valid XML format adhering to JATS schema requirements.
"""

from jats_classes import JATSClassInterface, JATSDocument


class JatsExporter:
    """Exporter that converts a JATSDocument to its JATS XML string representation."""

    def export(self, document: JATSDocument) -> str:
        """Export the JATSDocument to XML string format."""
        return document.to_xml()

    def export_partial(self, part: JATSClassInterface) -> str:
        """Export a partial JATS class instance to XML string format."""
        return part.to_xml()
