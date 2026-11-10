<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template name="make-header">
        <xsl:param name="front-node" select="front"/>
        <div class="article-header">
            <!-- Article ID -->
            <xsl:variable name="article-id" select="normalize-space(string($front-node/article-meta/article-id))" />
            <xsl:if test="$article-id">
                <div class="article-id">
                    <xsl:value-of select="$article-id"/>
                </div>
            </xsl:if>
            <!-- Article Title -->
            <xsl:variable name="article-title" select="normalize-space(string($front-node/article-meta/title-group/article-title))" />
            <xsl:if test="$article-title">
                <div class="article-title">
                    <xsl:value-of select="$article-title"/>
                </div>
            </xsl:if>
            <!-- Article Subtitle - only the first subtitle element is considered -->
            <xsl:variable name="article-subtitle" select="normalize-space(string($front-node/article-meta/title-group/subtitle[1]))" />
            <xsl:if test="$article-subtitle">
                <div class="article-subtitle">
                    <xsl:value-of select="$article-subtitle"/>
                </div>
            </xsl:if>
        </div>
    </xsl:template>

</xsl:stylesheet>
