<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                exclude-result-prefixes="xlink">

    <xsl:template name="make-metadata">
        <xsl:param name="front-node" select="front"/>
        <table class="article-metadata">
            <tbody>
                <!-- Journal Title and Subtitle -->
                <xsl:variable name="journal-title" select="normalize-space(string($front-node/journal-meta/journal-title-group/journal-title))" />
                <xsl:variable name="journal-subtitle" select="normalize-space(string($front-node/journal-meta/journal-title-group/journal-subtitle))" />
                <xsl:if test="$journal-title or $journal-subtitle">
                    <tr data-meta-field="journal-title-group">
                        <td>
                            <span><xsl:value-of select="$journal-title"/></span>
                            <xsl:if test="$journal-title and $journal-subtitle">
                                <span> &#x2022; </span>
                            </xsl:if>
                            <span><xsl:value-of select="$journal-subtitle"/></span>
                        </td>
                    </tr>
                </xsl:if>
                <!-- Pub Dates -->
                <xsl:variable name="issue-date" select="$front-node/article-meta/pub-date[@date-type='Ausgabedatum'][1] | $front-node/article-meta/pub-date[not(@date-type) and not(../pub-date[@date-type='Ausgabedatum'])][1]" />
                <xsl:variable name="has-issue-date" select="boolean($issue-date[normalize-space(day) or normalize-space(month) or normalize-space(year)])" />
                <xsl:variable name="revision-date" select="$front-node/article-meta/pub-date[@date-type='AktualisierteFassung'][1]" />
                <xsl:variable name="has-revision-date" select="boolean($revision-date[normalize-space(day) or normalize-space(month) or normalize-space(year)])" />
                <xsl:if test="$has-issue-date or $has-revision-date">
                    <tr data-meta-field="pub-dates">
                        <td>
                            <xsl:if test="$has-issue-date">
                                <span>Vom
                                <xsl:for-each select="$issue-date">
                                    <xsl:call-template name="format-date"/>
                                </xsl:for-each>
                                </span>
                            </xsl:if>
                            <xsl:if test="$has-issue-date and $has-revision-date">
                                <span> &#x2022; </span>
                            </xsl:if>
                            <xsl:if test="$has-revision-date">
                                <span>In der Fassung vom
                                <xsl:for-each select="$revision-date">
                                    <xsl:call-template name="format-date"/>
                                </xsl:for-each>
                                </span>
                            </xsl:if>
                        </td>
                    </tr>
                </xsl:if>
                <!-- Fachbereich -->
                <xsl:variable name="fachbereich" select="$front-node/article-meta/custom-meta-group/custom-meta[meta-name='Fachbereich']/meta-value" />
                <xsl:if test="$fachbereich">
                    <tr data-meta-field="fachbereich">
                        <td>
                            <p class="metadata-title">Fachbereich</p>
                            <xsl:value-of select="$fachbereich"/>
                        </td>
                    </tr>
                </xsl:if>
                <!-- Sachgebiet -->
                <xsl:variable name="sachgebiet" select="$front-node/article-meta/custom-meta-group/custom-meta[meta-name='Sachgebiet']/meta-value" />
                <xsl:if test="$sachgebiet">
                    <tr data-meta-field="sachgebiet">
                        <td>
                            <p class="metadata-title">Sachgebiet</p>
                            <xsl:value-of select="$sachgebiet"/>
                        </td>
                    </tr>
                </xsl:if>
                <!-- Dokument-URI -->
                <xsl:variable name="document-uri" select="$front-node/article-meta/ext-link | $front-node/article-meta/uri | $front-node/article-meta/self-uri" />
                <xsl:if test="$document-uri">
                    <tr data-meta-field="document-uri">
                        <td>
                            <a>
                                <xsl:for-each select="$document-uri[1]">
                                    <xsl:call-template name="assign-href"/>
                                </xsl:for-each>
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
    </xsl:template>

</xsl:stylesheet>
