from jats_classes import JATSDocument, Section, Appendix, AppendixGroup, Front, Body, Back, Article, RefList, Glossary

def test_jats_constructors():
    section = Section(sec_type=None, label_title_raw="", content_raw="", sections=[])
    appendix = Appendix(sec_type=None, label_title_raw="", content_raw="", sections=[section])
    appendix_group = AppendixGroup(sec_type=None, label_title_raw="", content_raw="", sections=[appendix])
    front = Front(
                xml_lang="de",
                journal_id=None,
                journal_title=None,
                journal_subtitle=None,
                issn=None,
                publisher_name=None,
                publisher_institution=None,
                publisher_addr_line=None,
                publisher_postal_code=None,
                publisher_city=None,
                publisher_phone=None,
                publisher_email=None,
                publisher_uri=None,
                article_id=None,
                title=None,
                article_subtitle=[],
                author_surname=None,
                co_author_surname=None,
                co_author_aff=None,
                self_uri=None,
                article_categories=None,
                related_articles_translations_map=None,
                related_articles_map=None,
                pub_date_ausgabedatum=None,
                pub_date_aktualisierte_fassung=None,
                history_initial_publication=None,
                history_correction=None,
                history_latest_version=None,
                copyright_statement=None,
                copyright_holder=None,
                abstract_short_title=None,
                abstract_short=None,
                abstract_summary_title=None,
                abstract_summary=None,
                subjects=[],
                beschreibender_typ=None,
                bisherige_bestellnummer=None,
                webcode=None,
                organisationseinheit=None,
                fachbereich=None,
                sachgebiet=None,
                veroeffentlichungsstatus=None,
                bildnachweis=None,
                ueberschriften_mit_nummerierung=False,
            )
    body = Body(sections=[section])
    back = Back(sections=[appendix_group])
    article = Article(front=front, body=body, back=back)
    doc = JATSDocument(article=article)
    ref_list = RefList(label_title_raw="", content_raw="")
    glossary = Glossary(label_title_raw="", content_raw="")