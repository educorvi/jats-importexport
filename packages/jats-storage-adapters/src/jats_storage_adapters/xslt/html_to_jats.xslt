<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xlink="http://www.w3.org/1999/xlink">

    <xsl:output method="xml" encoding="utf-8" indent="yes" omit-xml-declaration="yes"/>

    <xsl:template match="html">
        <xsl:apply-templates select="body/article"/>
    </xsl:template>

    <xsl:template match="article">
        <article>
            <front>
                <xsl:apply-templates select="header"/>
            </front>
            <main>
                <xsl:apply-templates select="section"/>
            </main>
            <back>
                <xsl:apply-templates select="footer"/>
            </back>
        </article>
    </xsl:template>

    <!-- header -->

    <xsl:template match="header">
        <xsl:apply-templates select="h1" mode="header"/>
    </xsl:template>

    <xsl:template match="h1" mode="header">
        <title>
            <xsl:apply-templates/>
        </title>
    </xsl:template>

    <!-- footer -->

    <xsl:template match="footer">
        <xsl:apply-templates select="div" mode="footer"/>
    </xsl:template>

    <xsl:template match="div" mode="footer">
        <section>
            <xsl:apply-templates select="@id"/>
            <xsl:apply-templates/>
        </section>
    </xsl:template>

    <!-- block-level elements -->

    <xsl:template match="section">
        <section>
            <xsl:apply-templates select="@data-section"/>
            <xsl:apply-templates/>
        </section>
    </xsl:template>

    <!-- inline elements -->

    <xsl:template match="span[@itemprop]">
        <named-content content-type="{ @itemprop }">
            <xsl:apply-templates/>
        </named-content>
    </xsl:template>

    <xsl:template match="u">
        <underline>
            <xsl:apply-templates/>
        </underline>
    </xsl:template>

    <!-- TODO the elements above this point dont appear in the richtext html -->

    <!-- headings -->

    <xsl:template match="h1 | h2 | h3 | h4 | h5 | h6">
        <heading level="{local-name()}">
            <xsl:apply-templates/>
        </heading>
    </xsl:template>

    <!-- formats (p / br / blockquote / div / preformatted) -->

    <xsl:template match="p">
        <p>
            <xsl:apply-templates/>
        </p>
    </xsl:template>

    <xsl:template match="br">
        <break/>
    </xsl:template>

    <!-- TODO UI -->
    <xsl:template match="blockquote/p">
        <disp-quote>
            <xsl:apply-templates/>
        </disp-quote>
    </xsl:template>

    <!-- TODO UI -->
    <xsl:template match="div">
        <p>
            <xsl:apply-templates/>
        </p>
    </xsl:template>

    <!-- TODO UI -->
    <xsl:template match="pre">
        <preformat>
            <xsl:apply-templates/>
        </preformat>
    </xsl:template>

    <!-- inline formats -->

    <xsl:template match="b | strong">
        <bold>
            <xsl:apply-templates/>
        </bold>
    </xsl:template>

    <xsl:template match="i | em">
        <italic>
            <xsl:apply-templates/>
        </italic>
    </xsl:template>

    <xsl:template match="span[@style='text-decoration: underline;']">
        <underline>
            <xsl:apply-templates/>
        </underline>
    </xsl:template>

    <xsl:template match="s">
        <strike>
            <xsl:apply-templates/>
        </strike>
    </xsl:template>

    <xsl:template match="sup">
        <sup>
            <xsl:apply-templates/>
        </sup>
    </xsl:template>

    <xsl:template match="sub">
        <sub>
            <xsl:apply-templates/>
        </sub>
    </xsl:template>

    <xsl:template match="code">
        <monospace>
            <xsl:apply-templates/>
        </monospace>
    </xsl:template>

    <!-- TODO -->
    <!-- <p class="text-columns-2">2 Spalten</p>
    <p class="text-columns-3">3 Spalten</p> -->

    <!-- TODO Alignment (start / center / end / justify)-->

    <!-- TODO Other Formats (callout / discreet / highlight-inline / highlight-paragraph) -->

    <!-- Lists -->

    <xsl:template match="ul">
        <list list-type="bullet">
            <xsl:apply-templates/>
        </list>
    </xsl:template>

    <xsl:template match="ol">
        <list list-type="order">
            <xsl:apply-templates/>
        </list>
    </xsl:template>

    <xsl:template match="li">
        <list-item>
            <xsl:choose>
                <xsl:when test="p | ul | ol">
                    <xsl:apply-templates/>
                </xsl:when>
                <xsl:otherwise>
                    <p><xsl:apply-templates/></p>
                </xsl:otherwise>
            </xsl:choose>
        </list-item>
    </xsl:template>

    <!-- Tables -->

    <xsl:template match="table">
        <table-wrap>
            <xsl:apply-templates select="caption"/>
            <table>
                <xsl:apply-templates select="*[not(self::caption)]"/>
            </table>
        </table-wrap>
    </xsl:template>

    <xsl:template match="table/caption">
        <caption>
            <title><xsl:apply-templates/></title>
        </caption>
    </xsl:template>

    <xsl:template match="thead | tbody | tfoot">
        <xsl:element name="{local-name()}">
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="tr">
        <tr>
            <xsl:apply-templates/>
        </tr>
    </xsl:template>

    <xsl:template match="td | th">
        <xsl:element name="{local-name()}">
            <xsl:if test="@colspan">
                <xsl:attribute name="colspan"><xsl:value-of select="@colspan"/></xsl:attribute>
            </xsl:if>
            <xsl:if test="@rowspan">
                <xsl:attribute name="rowspan"><xsl:value-of select="@rowspan"/></xsl:attribute>
            </xsl:if>
            <xsl:if test="@align">
                <xsl:attribute name="align"><xsl:value-of select="@align"/></xsl:attribute>
            </xsl:if>
            <xsl:if test="@valign">
                <xsl:attribute name="valign"><xsl:value-of select="@valign"/></xsl:attribute>
            </xsl:if>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="colgroup">
        <colgroup>
            <xsl:apply-templates/>
        </colgroup>
    </xsl:template>

    <xsl:template match="col">
        <col>
            <xsl:if test="@span">
                <xsl:attribute name="span"><xsl:value-of select="@span"/></xsl:attribute>
            </xsl:if>
            <xsl:if test="@width">
                <xsl:attribute name="width"><xsl:value-of select="@width"/></xsl:attribute>
            </xsl:if>
            <xsl:if test="@style">
                <xsl:attribute name="style"><xsl:value-of select="@style"/></xsl:attribute>
            </xsl:if>
        </col>
    </xsl:template>

    <!-- Links -->

    <xsl:template match="a">
        <ext-link ext-link-type="uri" xlink:href="{@href}">
            <xsl:apply-templates/>
        </ext-link>
    </xsl:template>

    <!-- Images -->

    <!-- A <p> that contains only an <img> should produce <fig>, not <p><fig> -->
    <xsl:template match="p[img]">
        <xsl:apply-templates select="img"/>
    </xsl:template>

    <xsl:template match="img">
        <fig>
            <xsl:if test="@data-captiontext">
                <caption>
                    <title><xsl:value-of select="@data-captiontext"/></title>
                </caption>
            </xsl:if>
            <xsl:if test="@alt">
                <alt-text><xsl:value-of select="@alt"/></alt-text>
            </xsl:if>
            <graphic>
                <xsl:attribute name="xlink:href"><xsl:value-of select="@src"/></xsl:attribute>
                <xsl:if test="@data-picturevariant">
                    <xsl:attribute name="specific-use">
                        <xsl:choose>
                            <xsl:when test="@data-picturevariant='small'">image-size:s</xsl:when>
                            <xsl:when test="@data-picturevariant='medium'">image-size:m</xsl:when>
                            <xsl:when test="@data-picturevariant='large'">image-size:l</xsl:when>
                            <xsl:otherwise>image-size:m</xsl:otherwise>
                        </xsl:choose>
                    </xsl:attribute>
                </xsl:if>
            </graphic>
        </fig>
    </xsl:template>


    <!--
    <xsl:template match="*">
        <xsl:element name="{local-name()}">
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates select="node()"/>
        </xsl:element>
    </xsl:template>
    -->

    <!-- continue through unknown elements -->
    <xsl:template match="*">
        <xsl:apply-templates/>
    </xsl:template>

    <!-- attributes -->
    <xsl:template match="@id">
        <xsl:copy-of select="."/>
    </xsl:template>

    <!-- section ids -->
    <xsl:template match="@data-section">
        <xsl:attribute name="id">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>
</xsl:stylesheet>