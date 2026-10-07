"""JATS Document model.

Provides the primary wrapper and parser/validator for whole JATS XML documents.
"""

from __future__ import annotations

import os
from io import BytesIO

import xmlschema
from lxml import etree

from .Article import Article
from .Front import Front


class JATSDocument:
    """Wrapper class representing a complete JATS document.

    Main entry point for loading JATS from XML content or Plone.
    """

    article: Article
    related_articles: list[tuple[str, str, Front]]
    related_articles_translations: list[tuple[str, str, Front]]

    def __init__(
        self,
        article: Article,
        related_articles: list[tuple[str, str, Front]] | None = None,
        related_articles_translations: list[tuple[str, str, Front]] | None = None,
    ):
        """Initialize the document with an Article instance."""
        self.article = article
        self.related_articles = related_articles or []
        self.related_articles_translations = related_articles_translations or []

    def set_related_articles(self, related_articles: list[tuple[str, str, Front]]):
        self.related_articles = related_articles

    def set_related_articles_translations(self, related_articles_translations: list[tuple[str, str, Front]]):
        self.related_articles_translations = related_articles_translations

    @classmethod
    def from_xml(cls, xml_content: str, xsd_path: str | None) -> JATSDocument:
        """Parse XML content into a JATSDocument model, validating against XSD.

        Args:
            xml_content: String containing raw XML text.
            xsd_path: Optional path to an XSD schema for schema validation.

        Returns:
            A JATSDocument instance.
        """
        xml_schema = None
        if xsd_path is not None:
            if not cls._file_exists(xsd_path):
                raise FileNotFoundError(f"XSD file not found: {xsd_path}")
            xml_schema = cls._parse_xml_schema(xsd_path)
        return cls.from_xml_with_parsed_schema(xml_content, xml_schema)

    @classmethod
    def from_xml_with_parsed_schema(cls, xml_content: str, xml_schema: xmlschema.XMLSchema | None) -> JATSDocument:
        """Parse XML content into a JATSDocument model, validating against XSD.

        Args:
            xml_content: String containing raw XML text.
            xml_schema: Optional parsed XMLSchema object for schema validation.

        Returns:
            A JATSDocument instance.
        """
        if xml_schema is not None:
            errors = cls._validate_xml(xml_content, xml_schema)
            if errors:
                details = "\n".join(f"{path or '/'}: {reason}" for path, reason in errors)
                raise ValueError(f"XML is not valid according to the XSD:\n{details}")
        parser = etree.XMLParser(remove_pis=False, remove_comments=False)
        tree = etree.parse(BytesIO(xml_content.encode("utf-8")), parser=parser)
        root = tree.getroot()
        if root.tag != "article":
            raise ValueError(f"Expected root element 'article', got '{root.tag}'")
        article = Article.from_xml_element(root)
        return cls(article=article)

    def to_xml(self) -> str:
        """Serialize the JATSDocument instance back to XML."""
        doctype = (
            '<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Publishing DTD '
            'with OASIS Tables with MathML3 v1.1 20151215//EN" '
            '"JATS-journalpublishing-oasis-article1-mathml3.dtd">'
        )
        return f"{doctype}\n{self.article.to_xml()}\n"

    @staticmethod
    def _file_exists(file_path: str) -> bool:
        """Check if the given path points to an existing file."""
        return os.path.isfile(file_path)

    @staticmethod
    def _parse_xml_schema(xsd_path: str) -> xmlschema.XMLSchema:
        """Parse an XSD schema file and return an XMLSchema object."""
        return xmlschema.XMLSchema(xsd_path)

    @staticmethod
    def _validate_xml(xml_content: str, xml_schema: xmlschema.XMLSchema) -> list[tuple[str, str]]:
        """Validate XML string content against a parsed XMLSchema object.

        Returns a list of validation errors, each as a tuple of (path, reason).
        An empty list indicates the XML is valid.
        """
        return [(error.path or "/", error.reason or "") for error in xml_schema.iter_errors(xml_content)]

    def extract_keywords(self) -> list[str]:
        """Extract keywords from elements with the attribute specific-use="keyword"."""
        return self.article.extract_keywords()

    def extract_and_add_keywords(self) -> None:
        """Extract keywords and add them to the document's keyword set."""
        keywords = self.extract_keywords()
        if keywords:
            old_keywords = self.article.front.subjects or []
            for k in keywords:
                if k not in old_keywords:
                    old_keywords.append(k)
            self.article.front.subjects = old_keywords or None
