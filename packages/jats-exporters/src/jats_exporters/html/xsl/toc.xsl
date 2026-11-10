<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template name="make-toc">
        <xsl:param name="front-node" select="front"/>
        <nav class="article-toc">
            <p class="metadata-title">Inhaltsverzeichnis</p>
            <xsl:call-template name="toc-sections">
                <xsl:with-param name="sections"
                                select="//body/sec[title[normalize-space(string(.))] and @sec-type != 'toc'] |
                                    //back/app-group[title[normalize-space(string(.))]] |
                                    //back/sec[title[normalize-space(string(.))] and @sec-type != 'toc'] |
                                    //back/app[title[normalize-space(string(.))]] |
                                    //back/ref-list[title[normalize-space(string(.))]] |
                                    //back/glossary[title[normalize-space(string(.))]]"/>
                <xsl:with-param name="depth" select="0"/>
            </xsl:call-template>
        </nav>
    </xsl:template>


    <xsl:template name="toc-sections">
        <xsl:param name="sections"/>
        <xsl:param name="depth"/>
        <xsl:if test="$sections">
            <ul>
                <xsl:for-each select="$sections">
                    <li>
                        <xsl:variable name="anchor-id">
                            <xsl:choose>
                                <xsl:when test="@id">
                                    <xsl:value-of select="@id"/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:value-of select="generate-id(.)"/>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:variable>
                        <span class="toc-entry">
                            <xsl:attribute name="data-toc-level">
                                <xsl:value-of select="$depth + 1"/>
                            </xsl:attribute>
                            <xsl:if test="label">
                                <span class="toc-label">
                                    <xsl:apply-templates select="label/node()"/>
                                </span>
                                <xsl:text> </xsl:text>
                            </xsl:if>
                            <a href="#{$anchor-id}" class="toc-title">
                                <xsl:apply-templates select="title/node()"/>
                            </a>
                        </span>
                        <xsl:variable name="subsections"
                                      select="sec[title[normalize-space(string(.))] and @sec-type != 'toc'] |
                                            app[title[normalize-space(string(.))]] |
                                            ref-list[title[normalize-space(string(.))]] |
                                            glossary[title[normalize-space(string(.))]]"/>
                        <xsl:if test="$subsections">
                            <xsl:call-template name="toc-sections">
                                <xsl:with-param name="sections" select="$subsections"/>
                                <xsl:with-param name="depth" select="$depth + 1"/>
                            </xsl:call-template>
                        </xsl:if>
                    </li>
                </xsl:for-each>
            </ul>
        </xsl:if>
    </xsl:template>

</xsl:stylesheet>
