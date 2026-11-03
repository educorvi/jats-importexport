<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                exclude-result-prefixes="xlink">


    <xsl:template name="metadata-and-toc">
        <xsl:param name="front-node" select="front"/>
        <div class="metadata-and-toc">
            <div class="metadata-small">
                <table>
                    <tbody>
                        <!-- Journal Title -->
                        <xsl:variable name="journal-title" select="normalize-space(string($front-node/journal-meta/journal-title-group/journal-title))" />
                        <xsl:if test="$journal-title">
                            <tr data-meta-field="journal-title">
                                <td>
                                    <xsl:value-of select="$journal-title"/>
                                </td>
                            </tr>
                        </xsl:if>
                        <!-- Journal Subtitle -->
                        <xsl:variable name="journal-subtitle" select="normalize-space(string($front-node/journal-meta/journal-title-group/journal-subtitle))" />
                        <xsl:if test="$journal-subtitle">
                            <tr data-meta-field="journal-subtitle">
                                <td>
                                    <xsl:value-of select="$journal-subtitle"/>
                                </td>
                            </tr>
                        </xsl:if>
                        <!-- Vom -->
                        <xsl:variable name="issue-date" select="$front-node/article-meta/pub-date[@date-type='Ausgabedatum'][1] | $front-node/article-meta/pub-date[not(@date-type) and not(../pub-date[@date-type='Ausgabedatum'])][1]" />
                        <xsl:if test="$issue-date[normalize-space(day) or normalize-space(month) or normalize-space(year)]">
                            <tr data-meta-field="issue-date">
                                <td>
                                    Vom
                                    <xsl:for-each select="$issue-date">
                                        <xsl:call-template name="format-date"/>
                                    </xsl:for-each>
                                </td>
                            </tr>
                        </xsl:if>
                        <!-- In der Fassung vom -->
                        <xsl:variable name="revision-date" select="$front-node/article-meta/pub-date[@date-type='AktualisierteFassung'][1]" />
                        <xsl:if test="$revision-date[normalize-space(day) or normalize-space(month) or normalize-space(year)]">
                            <tr data-meta-field="revision-date">
                                <td>
                                    In der Fassung vom
                                    <xsl:for-each select="$revision-date">
                                        <xsl:call-template name="format-date"/>
                                    </xsl:for-each>
                                </td>
                            </tr>
                        </xsl:if>
                        <!-- Dokument-URI -->
                        <xsl:variable name="document-uri" select="$front-node/article-meta/ext-link | $front-node/article-meta/uri | $front-node/article-meta/self-uri" />
                        <xsl:if test="$document-uri">
                            <tr data-meta-field="document-uri">
                                <td>
                                    <a href="{@xlink:href}">
                                        <xsl:call-template name="assign-href" select="$document-uri[1]"/>
                                        Publikation
                                    </a>
                                </td>
                            </tr>
                        </xsl:if>
                        <!-- Related articles -->
                        <xsl:variable name="related-articles"
                                    select="$front-node/article-meta/related-article[normalize-space(string(@xlink:href))][@related-article-type='companion']" />
                        <xsl:if test="$related-articles">
                            <tr data-meta-field="related-articles">
                                <td>
                                    <p class="metadata-title">Verwandte Artikel</p>
                                    <ul>
                                        <xsl:for-each select="$related-articles">
                                            <li>
                                                <a>
                                                    <xsl:call-template name="assign-href"/>
                                                    <xsl:choose>
                                                        <xsl:when test="normalize-space(string(.))">
                                                            <xsl:apply-templates/>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                            <xsl:value-of select="@xlink:href"/>
                                                        </xsl:otherwise>
                                                    </xsl:choose>
                                                </a>
                                            </li>
                                        </xsl:for-each>
                                    </ul>
                                </td>
                            </tr>
                        </xsl:if>
                        <!-- Translations -->
                        <xsl:variable name="related-articles-translations"
                                    select="$front-node/article-meta/related-article[normalize-space(string(@xlink:href))][@related-article-type='translated-article']" />
                        <xsl:if test="$related-articles-translations">
                            <tr data-meta-field="related-articles">
                                <td>
                                    <p class="metadata-title">Sprachvarianten</p>
                                    <ul>
                                        <xsl:for-each select="$related-articles-translations">
                                            <li>
                                                <a>
                                                    <xsl:call-template name="assign-href"/>
                                                    <xsl:choose>
                                                        <xsl:when test="normalize-space(string(@xml:lang))">
                                                            <xsl:call-template name="language-name-de">
                                                                <xsl:with-param name="lang" select="@xml:lang"/>
                                                            </xsl:call-template>
                                                        </xsl:when>
                                                        <xsl:when test="normalize-space(string(.))">
                                                            <xsl:apply-templates/>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                            <xsl:value-of select="@xlink:href"/>
                                                        </xsl:otherwise>
                                                    </xsl:choose>
                                                </a>
                                            </li>
                                        </xsl:for-each>
                                    </ul>
                                </td>
                            </tr>
                        </xsl:if>
                    </tbody>
                </table>
            </div>
            <nav class="toc">
                <p class="toc-meta-title">Inhaltsverzeichnis</p>
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
        </div>
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
