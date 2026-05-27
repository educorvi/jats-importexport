<?xml version="1.0"?>
<!-- Standalone variant of jats-html.xsl that wraps output in a full HTML document.
     Imports jats-html.xsl and overrides only the root template to add the HTML
     frame (html/head/body) that is commented out in the base stylesheet. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                xmlns:mml="http://www.w3.org/1998/Math/MathML"
                exclude-result-prefixes="xlink mml">

    <xsl:import href="jats-html.xsl"/>

    <xsl:template match="/">
        <html>
            <!-- HTML header -->
            <xsl:call-template name="make-html-header"/>
            <body>
                <xsl:apply-templates/>
            </body>
        </html>
    </xsl:template>

</xsl:stylesheet>
