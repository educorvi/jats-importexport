import re
from functools import lru_cache
from uuid import uuid4

from jats_classes import JATSDocument
from markdownify import markdownify as md

from .html import HtmlExporter


class MarkdownExporter:
    @lru_cache(maxsize=128)
    def export(self, document: JATSDocument) -> str:
        html = HtmlExporter().export(document)
        # Protect raw MathML from markdownify's tag stripping and text escaping.
        math_blocks = {}
        prefix = uuid4().hex

        def preserve_math(match: re.Match[str]) -> str:
            placeholder = f"{prefix}math{len(math_blocks)}"
            math_blocks[placeholder] = match.group(0)
            return placeholder

        html = re.sub(r"<math\b[^>]*>.*?</math\s*>", preserve_math, html, flags=re.DOTALL | re.IGNORECASE)
        markdown = md(html)
        for placeholder, math in math_blocks.items():
            markdown = markdown.replace(placeholder, math)
        return markdown
