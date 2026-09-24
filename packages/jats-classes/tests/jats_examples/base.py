JATS_DOC_SKELETON = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Publishing DTD with OASIS Tables with MathML3 v1.1 20151215//EN" "JATS-journalpublishing-oasis-article1-mathml3.dtd"[]>
<article xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="de" article-type="DGUV Vorschriften- und Regelwerk" dtd-version="1.1">
    {article}
</article>
"""

JATS_FRONT_SKELETON = """<front>
    <journal-meta>
        {journal_meta}
    </journal-meta>
    <article-meta>
        {article_meta}
    </article-meta>
</front>
"""

JATS_BODY_SKELETON = """<body>
    {body}
</body>
"""

JATS_BACK_SKELETON = """<back>
    {back}
</back>
"""

JATS_MINIMAL_JOURNAL_META = """<journal-id />
<issn />
"""

JATS_MINIMAL_ARTICLE_META = """<title-group>
    <article-title>Minimal Valid JATS Article</article-title>
    <subtitle>Minimal subtitle</subtitle>
</title-group>
<pub-date>
    <year>2015</year>
</pub-date>
<abstract>
</abstract>
"""

def get_jats_front(journal_meta=JATS_MINIMAL_JOURNAL_META, article_meta=JATS_MINIMAL_ARTICLE_META):
    return JATS_FRONT_SKELETON.format(
        journal_meta=journal_meta,
        article_meta=article_meta
    )

def get_jats_body(body=""):
    return JATS_BODY_SKELETON.format(
        body=body
    )

def get_jats_back(back=""):
    return JATS_BACK_SKELETON.format(
        back=back
    )

def get_jats_doc(journal_meta=JATS_MINIMAL_JOURNAL_META, article_meta=JATS_MINIMAL_ARTICLE_META, body="", back=""):
    article = get_jats_front(journal_meta, article_meta) + get_jats_body(body) + (get_jats_back(back) if back else "")
    return JATS_DOC_SKELETON.format(
        article=article
    )

MINIMAL_VALID_JATS = get_jats_doc()
VALID_JATS_WITH_BACK = get_jats_doc(back="<sec><title>Back sec</title></sec>")
