JATS_INVALID_ROOT = """<not-article>
    <front></front>
    <body></body>
    <back></back>
</not-article>"""

JATS_MISSING_BODY = """<article>
    <front></front>
</article>"""

JATS_MISSING_FRONT = """<article>
    <body></body>
</article>"""

JATS_EMPTY_FRONT = """<article>
    <front></front>
    <body></body>
    <back></back>
</article>"""

INVALID_STRUCTURE_LIST = [
    JATS_INVALID_ROOT,
    JATS_MISSING_BODY,
    JATS_MISSING_FRONT,
    JATS_EMPTY_FRONT,
]
