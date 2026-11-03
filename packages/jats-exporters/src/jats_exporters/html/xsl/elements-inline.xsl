<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                exclude-result-prefixes="xlink">

    <!-- ============================================================= -->
    <!--  INLINE MISCELLANEOUS                                         -->
    <!-- ============================================================= -->
    <!--  Templates strictly for formatting follow; these are templates
          to handle various inline structures -->


    <xsl:template match="break">
        <br class="br"/>
    </xsl:template>


    <xsl:template match="email">
        <a href="mailto:{.}">
            <xsl:apply-templates/>
        </a>
    </xsl:template>


    <xsl:template match="ext-link | uri">
        <a target="xrefwindow" class="jats-ext-link">
            <xsl:attribute name="href">
                <xsl:value-of select="."/>
            </xsl:attribute>
            <!-- if an @href is present, it overrides the href
                 just attached -->
            <xsl:call-template name="assign-href"/>
            <xsl:call-template name="assign-id"/>
            <xsl:apply-templates/>
            <xsl:if test="not(normalize-space(string(.)))">
                <xsl:value-of select="@xlink:href"/>
            </xsl:if>
        </a>
    </xsl:template>


    <!-- inline-graphic is with graphic at the block level elements -->


    <xsl:template match="inline-formula">
        <span class="{local-name()}">
            <xsl:apply-templates/>
        </span>
    </xsl:template>


    <xsl:template match="styled-content">
        <span>
            <xsl:copy-of select="@style"/>
            <xsl:for-each select="@style-type">
                <xsl:attribute name="class">
                    <xsl:value-of select="."/>
                </xsl:attribute>
            </xsl:for-each>
            <xsl:apply-templates/>
        </span>
    </xsl:template>


    <xsl:template match="named-content">
        <span>
            <xsl:for-each select="@content-type">
                <xsl:attribute name="class">
                    <xsl:value-of select="translate(.,' ','-')"/>
                </xsl:attribute>
            </xsl:for-each>
            <xsl:apply-templates/>
        </span>
    </xsl:template>


    <xsl:template match="related-article">
        <span class="generated">[Verwandter Artikel:]</span>
        <xsl:apply-templates/>
    </xsl:template>


    <xsl:template match="related-object">
        <span class="generated">[Verwandter Gegenstand:]</span>
        <xsl:apply-templates/>
    </xsl:template>


    <xsl:template match="xref">
        <a href="#{@rid}">
            <xsl:apply-templates/>
        </a>
    </xsl:template>


    <!-- ============================================================= -->
    <!--  Formatting elements                                          -->
    <!-- ============================================================= -->


    <xsl:template match="bold">
        <b>
            <xsl:apply-templates/>
        </b>
    </xsl:template>


    <xsl:template match="italic">
        <em>
            <xsl:apply-templates/>
        </em>
    </xsl:template>


    <xsl:template match="sc">
        <span style="font-variant: small-caps">
            <xsl:apply-templates/>
        </span>
    </xsl:template>


    <xsl:template match="strike">
        <span style="text-decoration: line-through">
            <xsl:apply-templates/>
        </span>
    </xsl:template>


    <xsl:template match="sub">
        <sub>
            <xsl:apply-templates/>
        </sub>
    </xsl:template>


    <xsl:template match="sup">
        <sup>
            <xsl:apply-templates/>
        </sup>
    </xsl:template>


    <xsl:template match="underline">
        <span style="text-decoration: underline">
            <xsl:apply-templates/>
        </span>
    </xsl:template>

</xsl:stylesheet>
