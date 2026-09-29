DOC_INVALID_ROOT = """<not-article>
    <front></front>
    <body></body>
    <back></back>
</not-article>"""

DOC_MISSING_BODY = """<article>
    <front></front>
</article>"""

DOC_MISSING_FRONT = """<article>
    <body></body>
</article>"""

DOC_EMPTY_FRONT = """<article>
    <front></front>
    <body></body>
    <back></back>
</article>"""

INVALID_STRUCTURE_LIST = [
    DOC_INVALID_ROOT,
    DOC_MISSING_BODY,
    DOC_MISSING_FRONT,
    DOC_EMPTY_FRONT,
]
