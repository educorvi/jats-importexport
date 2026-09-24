FRONT_XML = """<front>
    <journal-meta>
        <journal-id>journal-123</journal-id>
        <journal-title-group>
            <journal-title>Journal of Testing</journal-title>
            <journal-subtitle>Reliable XML</journal-subtitle>
        </journal-title-group>
        <issn>1234-5678</issn>
        <publisher>
            <publisher-name>Example Publisher</publisher-name>
            <publisher-loc>
                <institution>Testing Institute</institution>
                <addr-line>Example Street 1</addr-line>
                <postal-code>12345</postal-code>
                <city>Test City</city>
                <phone>+49 123 456</phone>
                <email>mail@example.test</email>
                <uri>https://example.test</uri>
            </publisher-loc>
        </publisher>
    </journal-meta>
    <article-meta>
        <article-id pub-id-type="publisher-id">article-123</article-id>
        <title-group>
            <article-title>Readable <italic>JATS</italic> Front</article-title>
            <subtitle>First subtitle</subtitle>
            <subtitle>Second subtitle</subtitle>
        </title-group>
        <contrib-group>
            <contrib contrib-type="Autor">
                <name><surname>Author</surname></name>
            </contrib>
            <contrib contrib-type="Co-Autor">
                <name><surname>Coauthor</surname></name>
                <aff>Testing Department</aff>
            </contrib>
        </contrib-group>
        <self-uri xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="https://example.test/article-123"/>
        <related-article xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="https://example.test/related" related-article-type="companion">
            <title>Related article</title>
        </related-article>
        <related-article xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="https://example.test/translation" related-article-type="translated-article">
            <title>Translated article</title>
        </related-article>
        <pub-date date-type="Ausgabedatum">
            <day>2</day><month>3</month><year>2024</year>
        </pub-date>
        <pub-date date-type="AktualisierteFassung">
            <year>2025</year>
        </pub-date>
        <history>
            <date date-type="initial-publication"><year>2020</year></date>
            <date date-type="correction"><year>2021</year></date>
            <date date-type="latest-version"><year>2025</year></date>
        </history>
        <permissions>
            <copyright-statement>Copyright Example</copyright-statement>
            <copyright-holder>Example Publisher</copyright-holder>
        </permissions>
        <abstract abstract-type="short">
            <title>Short abstract</title>
            <p>Short <italic>summary</italic>.</p>
        </abstract>
        <abstract abstract-type="summary">
            <title>Summary abstract</title>
            <p>Long summary.</p>
        </abstract>
        <kwd-group kwd-group-type="author-generated">
            <kwd>XML</kwd><kwd>Testing</kwd>
        </kwd-group>
        <custom-meta-group>
            <custom-meta><meta-name>Webcode</meta-name><meta-value>WEB-123</meta-value></custom-meta>
            <custom-meta><meta-name>Überschriften mit Nummerierung</meta-name><meta-value>ja</meta-value></custom-meta>
        </custom-meta-group>
    </article-meta>
</front>"""

FRONT_WITHOUT_TITLE = """<front>
    <journal-meta/>
    <article-meta/>
</front>"""

FRONT_MISSING_JOURNAL_META = """<front>
    <article-meta/>
</front>"""

FRONT_MISSING_ARTICLE_META = """<front>
    <journal-meta/>
</front>"""
