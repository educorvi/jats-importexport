from __future__ import annotations

import os
from io import BytesIO

import xmlschema
from lxml import etree

from .Article import Article


class JATSDocument:
    article: Article

    def __init__(self, article: Article):
        self.article = article

    @classmethod
    def from_xml(cls, xml_content: str, xsd_path: str | None) -> JATSDocument:
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

    @classmethod
    def from_plone(cls, plone_article: object) -> JATSDocument:
        if getattr(plone_article, "portal_type", None) != "Article":
            raise ValueError("Provided object is not an Article")

        article = Article.from_plone(plone_article)
        return cls(article=article)

    @staticmethod
    def _file_exists(file_path: str) -> bool:
        return os.path.isfile(file_path)

    @staticmethod
    def _validate_xml(xml_content: str, xsd_path: str) -> bool:
        schema = xmlschema.XMLSchema(xsd_path)
        return schema.is_valid(xml_content)
