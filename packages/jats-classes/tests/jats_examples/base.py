_DOC_SKELETON = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Publishing DTD with OASIS Tables with MathML3 v1.1 20151215//EN" "JATS-journalpublishing-oasis-article1-mathml3.dtd"[]>
<article xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="de" article-type="DGUV Vorschriften- und Regelwerk" dtd-version="1.1">
    {article}
</article>"""

_FRONT_SKELETON = """<front>
    {front}
</front>"""

_BODY_SKELETON = """<body>
    {body}
</body>"""

_BACK_SKELETON = """<back>
    {back}
</back>"""

_MINIMAL_FRONT = """<journal-meta>
    <journal-id />
    <issn />
</journal-meta>
<article-meta>
    <title-group>
        <article-title>Minimal Valid JATS Article</article-title>
        <subtitle>Minimal subtitle</subtitle>
    </title-group>
    <pub-date>
        <year>2015</year>
    </pub-date>
    <abstract>
    </abstract>
</article-meta>"""


def get_jats_front(front=_MINIMAL_FRONT):
    return _FRONT_SKELETON.format(front=front)

def get_jats_body(body=""):
    return _BODY_SKELETON.format(body=body)

def get_jats_back(back=""):
    return _BACK_SKELETON.format(back=back)

def get_jats_doc(front=_MINIMAL_FRONT, body="", back=""):
    article = get_jats_front(front) + get_jats_body(body) + (get_jats_back(back) if back else "")
    return _DOC_SKELETON.format(article=article)

MINIMAL_VALID_JATS = get_jats_doc()
VALID_JATS_WITH_BACK = get_jats_doc(back="<sec><title>Back sec</title></sec>")


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
