"""JATS XML exporter implementation.

Serializes domain JATS class models (Article, Front, Body, Back, etc.) back into
valid XML format adhering to JATS schema requirements.
"""

from functools import lru_cache

from jats_classes import (
    Appendix,
    AppendixGroup,
    Article,
    Back,
    Body,
    Front,
    GenericSection,
    JATSDocument,
    Section,
)

from .interface import Exporter


def _wrap_article_jats(jats: str, xml_lang: str) -> str:
    """Wrap inner content in root <article> tag with DTD and namespaces."""
    doctype = (
        '<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Publishing DTD '
        'with OASIS Tables with MathML3 v1.1 20151215//EN" '
        '"JATS-journalpublishing-oasis-article1-mathml3.dtd">'
    )
    article_open = (
        '<article xmlns:mml="http://www.w3.org/1998/Math/MathML" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="{xml_lang}" '
        'article-type="DGUV Vorschrift" dtd-version="0.4">'
    )
    return f"{doctype}\n{article_open}\n\t{jats}\n</article>\n"


def _get_article_jats(article: Article) -> str:
    """Serialize an entire Article structure to JATS XML."""
    xml_lang = article.front.xml_lang or "de"
    content = f"{_get_front_jats(article.front)}{_get_body_jats(article.body)}{_get_back_jats(article.back)}"
    return _wrap_article_jats(content, xml_lang)


def _get_front_jats(front: Front) -> str:
    """Serialize the Front metadata element to JATS XML."""
    return front.to_xml()


def _get_body_jats(body: Body) -> str:
    """Serialize the Body element and its inner sections to JATS XML."""
    body_content = "\n".join(map(_get_general_section_jats, body.sections))
    return f"<body>{body_content}</body>"


def _get_back_jats(back: Back | None) -> str:
    """Serialize the Back element and its appendix groups to JATS XML."""
    if back is None:
        return ""
    back_content = "\n".join(map(_get_general_section_jats, back.appendix_groups))
    return f"<back>{back_content}</back>"


def _get_general_section_jats(section: GenericSection) -> str:
    """Recursively serialize a generic section (Section, Appendix or AppendixGroup) to JATS XML."""
    if isinstance(section, Section):
        sub_content = "\n".join(map(_get_general_section_jats, section.sections))
        tag_name = "sec"
        sec_type_attr_name = "sec-type"
    elif isinstance(section, Appendix):
        sub_content = "\n".join(map(_get_general_section_jats, section.sections))
        tag_name = "app"
        sec_type_attr_name = "app-type"
    elif isinstance(section, AppendixGroup):
        sub_content = "\n".join(map(_get_general_section_jats, section.appendixes))
        tag_name = "app-group"
        sec_type_attr_name = "content-type"
    else:
        raise ValueError(f"Unsupported section type: {type(section)}")

    sec_type = f' {sec_type_attr_name}="{section.sec_type}"' if section.sec_type else ""
    return f"<{tag_name}{sec_type}>{section.label_title_raw}\n{section.content_raw or ''}\n{sub_content}</{tag_name}>"


class JatsExporter(Exporter[str]):
    """Exporter that converts a JATSDocument to its JATS XML string representation."""

    @lru_cache(maxsize=128)
    def export(self, document: JATSDocument) -> str:
        """Export the JATSDocument to XML string format."""
        return _get_article_jats(document.article)
