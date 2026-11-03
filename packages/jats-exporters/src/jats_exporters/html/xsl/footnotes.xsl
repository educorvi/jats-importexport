<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="fn">
        <!-- Footnotes appearing outside fn-group
             generate cross-references to the footnote,
             which is displayed elsewhere -->
        <xsl:variable name="id">
            <xsl:apply-templates select="." mode="id"/>
        </xsl:variable>
        <a href="#{$id}">
            <xsl:apply-templates select="." mode="label-text"/>
        </a>
    </xsl:template>


    <xsl:template match="fn" mode="footnote">
        <div class="footnote">
            <xsl:call-template name="named-anchor"/>
            <xsl:apply-templates/>
        </div>
    </xsl:template>


    <xsl:template match="fn/p">
        <p>
            <xsl:call-template name="assign-id"/>
            <xsl:if test="not(preceding-sibling::p)">
                <!-- drop an inline label text into the first p -->
                <xsl:apply-templates select="parent::fn" mode="label-text"/>
                <xsl:text> </xsl:text>
            </xsl:if>
            <xsl:apply-templates/>
        </p>
    </xsl:template>


    <xsl:template match="fn" mode="label-text">
        <xsl:choose>
            <xsl:when test="not(label or @symbol)">
                <span class="generated">
                    <xsl:text>[</xsl:text>
                    <xsl:number level="any" count="fn[not(ancestor::front)]"
                                from="article"/>
                    <xsl:text>]</xsl:text>
                </span>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="@symbol"/>
                <xsl:value-of
                    select="translate(normalize-space(string(label)), ' &#xA;&#x9;', '&#xA0;&#xA0;&#xA0;')"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>
