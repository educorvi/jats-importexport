"""JATS XML exporter implementation.

Serializes domestic JATS class models (Article, Front, Body, Back, etc.) back into
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


def _wrap_article_jats(jats: str) -> str:
    """Wrap inner content in root <article> tag with DTD and namespaces."""
    doctype = (
        '<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Publishing DTD '
        'with OASIS Tables with MathML3 v1.1 20151215//EN" '
        '"JATS-journalpublishing-oasis-article1-mathml3.dtd">'
    )
    article_open = (
        '<article xmlns:mml="http://www.w3.org/1998/Math/MathML" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="de" '
        'article-type="DGUV Vorschrift" dtd-version="0.4">'
    )
    return f"{doctype}\n{article_open}\n\t{jats}\n</article>\n"


def _get_article_jats(article: Article) -> str:
    """Serialize an entire Article structure to JATS XML."""
    content = (
        f"{_get_front_jats(article.front)}"
        f"{_get_body_jats(article.body)}"
        f"{_get_back_jats(article.back)}"
    )
    return _wrap_article_jats(content)


def _get_front_jats(front: Front) -> str:
    """Serialize the Front metadata element to JATS XML."""
    return f"<front>{front.content_raw or ''}</front>"


def _get_body_jats(body: Body) -> str:
    """Serialize the Body element and its inner sections to JATS XML."""
    body_content = "\n".join(map(_get_general_section_jats, body.sections))
    return f"<body>{body_content}</body>"


def _get_back_jats(back: Back) -> str:
    """Serialize the Back element and its appendix groups to JATS XML."""
    back_content = "\n".join(map(_get_appendix_group_jats, back.appendix_groups))
    return f"<back>{back_content}</back>"


def _get_appendix_group_jats(appendix_group: AppendixGroup) -> str:
    """Serialize an AppendixGroup element and its appendices to JATS XML."""
    appendix_content = "\n".join(
        map(_get_general_section_jats, appendix_group.appendixes)
    )
    return f"<appendix-group>{appendix_content}</appendix-group>"


def _get_general_section_jats(section: GenericSection) -> str:
    """Recursively serialize a generic section (Section or Appendix) to JATS XML."""
    if isinstance(section, Section):
        sub_content = "\n".join(map(_get_general_section_jats, section.sections))
    elif isinstance(section, Appendix):
        sub_content = "\n".join(map(_get_general_section_jats, section.sections))
    else:
        sub_content = ""
    sec_type = f' sec-type="{section.sec_type}"' if section.sec_type else ""
    return (
        f"<sec{sec_type}>{section.label_title_raw}\n"
        f"{section.content_raw or ''}\n{sub_content}</sec>"
    )


class JatsExporter(Exporter[str]):
    """Exporter that converts a JATSDocument to its JATS XML string representation."""

    @lru_cache(maxsize=128)
    def export(self, document: JATSDocument) -> str:
        """Export the JATSDocument to XML string format."""
        return _get_article_jats(document.article)

