<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                exclude-result-prefixes="xlink">

    <!-- ============================================================= -->
    <!--  id mode                                                      -->
    <!-- ============================================================= -->
    <!-- An id can be derived for any element. If an @id is given,
         it is presumed unique and copied. If not, one is generated.   -->


    <!-- returns a unique id for the current element, does not create an attribute or element itself -->
    <xsl:template match="*" mode="id">
        <xsl:value-of select="@id"/>
        <xsl:if test="not(@id)">
            <xsl:value-of select="generate-id(.)"/>
        </xsl:if>
    </xsl:template>


    <!-- assigns a unique id to the current element, creating an @id attribute -->
    <xsl:template name="assign-id">
        <xsl:variable name="id">
            <xsl:apply-templates select="." mode="id"/>
        </xsl:variable>
        <xsl:attribute name="id">
            <xsl:value-of select="$id"/>
        </xsl:attribute>
    </xsl:template>


    <!-- generates an HTML named anchor for the current element -->
    <xsl:template name="named-anchor">
        <!-- generates an HTML named anchor -->
        <xsl:variable name="id">
            <xsl:apply-templates select="." mode="id"/>
        </xsl:variable>
        <a id="{$id}">
            <xsl:comment>named anchor</xsl:comment>
        </a>
    </xsl:template>


    <!-- ============================================================= -->
    <!--  assign-src and assign-href templates                         -->
    <!-- ============================================================= -->


    <xsl:template name="assign-src">
        <xsl:for-each select="@xlink:href">
            <xsl:attribute name="src">
                <xsl:value-of select="."/>
            </xsl:attribute>
        </xsl:for-each>
    </xsl:template>


    <xsl:template name="assign-href">
        <xsl:for-each select="@xlink:href">
            <xsl:attribute name="href">
                <xsl:value-of select="."/>
            </xsl:attribute>
        </xsl:for-each>
    </xsl:template>


    <!-- ============================================================= -->
    <!--  format-date                                                  -->
    <!-- ============================================================= -->
    <!-- Maps a structured date element to a german string with:
             DD Month YYYY (e.g., 28. Dezember 2026)
         Context must be 'date', with content model:
             (((day?, month?) | season)?, year)                        -->


    <xsl:template name="format-date">
        <xsl:for-each select="day">
            <xsl:apply-templates select="." mode="map"/>
            <xsl:text>. </xsl:text>
        </xsl:for-each>
        <xsl:for-each select="month">
            <xsl:apply-templates select="." mode="map"/>
            <xsl:text> </xsl:text>
        </xsl:for-each>
        <xsl:apply-templates select="year" mode="map"/>
    </xsl:template>


    <xsl:template match="day | year" mode="map">
        <xsl:apply-templates/>
    </xsl:template>


    <xsl:template match="month" mode="map">
        <xsl:choose>
            <xsl:when test="number() = 1">Januar</xsl:when>
            <xsl:when test="number() = 2">Februar</xsl:when>
            <xsl:when test="number() = 3">März</xsl:when>
            <xsl:when test="number() = 4">April</xsl:when>
            <xsl:when test="number() = 5">Mai</xsl:when>
            <xsl:when test="number() = 6">Juni</xsl:when>
            <xsl:when test="number() = 7">Juli</xsl:when>
            <xsl:when test="number() = 8">August</xsl:when>
            <xsl:when test="number() = 9">September</xsl:when>
            <xsl:when test="number() = 10">Oktober</xsl:when>
            <xsl:when test="number() = 11">November</xsl:when>
            <xsl:when test="number() = 12">Dezember</xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <!-- ============================================================= -->
    <!--  language-name-de                                             -->
    <!-- ============================================================= -->
    <!-- Maps a language code to its German name.
         The primary subtag is everything before '-', '_' or space.    -->


    <xsl:template name="language-name-de">
        <xsl:param name="lang"/>
        <xsl:variable name="code"
                      select="translate(substring-before(concat($lang, '-'), '-'),
                                        'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                                        'abcdefghijklmnopqrstuvwxyz')"/>
        <xsl:choose>
            <!-- Currently used language codes -->
            <xsl:when test="$code = 'de'">Deutsch</xsl:when>
            <xsl:when test="$code = 'en'">Englisch</xsl:when>
            <xsl:when test="$code = 'uk'">Ukrainisch</xsl:when>
            <xsl:when test="$code = 'ar'">Arabisch</xsl:when>
            <!-- Main european language codes -->
            <xsl:when test="$code = 'bg'">Bulgarisch</xsl:when>
            <xsl:when test="$code = 'cs'">Tschechisch</xsl:when>
            <xsl:when test="$code = 'da'">D&#228;nisch</xsl:when>
            <xsl:when test="$code = 'el'">Griechisch</xsl:when>
            <xsl:when test="$code = 'es'">Spanisch</xsl:when>
            <xsl:when test="$code = 'et'">Estnisch</xsl:when>
            <xsl:when test="$code = 'fi'">Finnisch</xsl:when>
            <xsl:when test="$code = 'fr'">Franz&#246;sisch</xsl:when>
            <xsl:when test="$code = 'ga'">Irisch</xsl:when>
            <xsl:when test="$code = 'hr'">Kroatisch</xsl:when>
            <xsl:when test="$code = 'hu'">Ungarisch</xsl:when>
            <xsl:when test="$code = 'is'">Isländisch</xsl:when>
            <xsl:when test="$code = 'it'">Italienisch</xsl:when>
            <xsl:when test="$code = 'lv'">Lettisch</xsl:when>
            <xsl:when test="$code = 'lt'">Litauisch</xsl:when>
            <xsl:when test="$code = 'mt'">Maltesisch</xsl:when>
            <xsl:when test="$code = 'nl'">Niederl&#228;ndisch</xsl:when>
            <xsl:when test="$code = 'no'">Norwegisch</xsl:when>
            <xsl:when test="$code = 'pl'">Polnisch</xsl:when>
            <xsl:when test="$code = 'pt'">Portugiesisch</xsl:when>
            <xsl:when test="$code = 'ro'">Rumänisch</xsl:when>
            <xsl:when test="$code = 'ru'">Russisch</xsl:when>
            <xsl:when test="$code = 'sk'">Slowakisch</xsl:when>
            <xsl:when test="$code = 'sl'">Slowenisch</xsl:when>
            <xsl:when test="$code = 'sv'">Schwedisch</xsl:when>
            <xsl:when test="$code = 'tr'">T&#252;rkisch</xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$lang"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>
