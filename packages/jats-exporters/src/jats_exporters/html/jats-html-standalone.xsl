<?xml version="1.0"?>
<!-- Standalone variant of jats-html.xsl that wraps output in a full HTML document.
     Imports jats-html.xsl and overrides only the root template to add the HTML frame (html/head/body). -->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:import href="jats-html.xsl"/>

    <xsl:template match="/">
        <html>
            <head>
                <meta charset="UTF-8"/>
                <title>
                    <xsl:value-of select="/article/front/article-meta/title-group/article-title[1]"/>
                </title>
            </head>
            <body>
                <xsl:apply-templates/>
            </body>
        </html>
    </xsl:template>

</xsl:stylesheet>
