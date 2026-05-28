"""JATS Document model.

Provides the primary wrapper and parser/validator for whole JATS XML documents.
"""

from __future__ import annotations

import os
from io import BytesIO

import xmlschema
from lxml import etree

from .Article import Article


class JATSDocument:
    """Wrapper class representing a complete JATS document.

    Main entry point for loading JATS from XML content or Plone.
    """

    article: Article

    def __init__(self, article: Article):
        """Initialize the document with an Article instance."""
        self.article = article

    @classmethod
    def from_xml(cls, xml_content: str, xsd_path: str | None) -> JATSDocument:
        """Parse XML content into a JATSDocument model, validating against XSD.

        Args:
            xml_content: String containing raw XML text.
            xsd_path: Optional path to an XSD schema for schema validation.

        Returns:
            A JATSDocument instance.
        """
        if xsd_path is not None:
            if not cls._file_exists(xsd_path):
                raise FileNotFoundError(f"XSD file not found: {xsd_path}")
            if not cls._validate_xml(xml_content, xsd_path):
                raise ValueError("XML is not valid according to the XSD:")
        parser = etree.XMLParser(remove_pis=False, remove_comments=False)
        tree = etree.parse(BytesIO(xml_content.encode("utf-8")), parser=parser)
        root = tree.getroot()
        if root.tag != "article":
            raise ValueError(f"Expected root element 'article', got '{root.tag}'")
        article = Article.from_xml_element(root)
        return cls(article=article)


    @staticmethod
    def _file_exists(file_path: str) -> bool:
        """Check if the given path points to an existing file."""
        return os.path.isfile(file_path)

    @staticmethod
    def _validate_xml(xml_content: str, xsd_path: str) -> bool:
        """Validate XML string content against an XSD schema file."""
        schema = xmlschema.XMLSchema(xsd_path)
        return schema.is_valid(xml_content)
