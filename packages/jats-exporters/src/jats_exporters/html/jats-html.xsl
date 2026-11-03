<?xml version="1.0"?>
<!-- ============================================================= -->
<!--  MODULE:    HTML Preview of NISO JATS Publishing 1.0 XML      -->
<!--  DATE:      May-June 2012                                     -->
<!--                                                               -->
<!-- ============================================================= -->

<!-- ============================================================= -->
<!--  SYSTEM:    NCBI Archiving and Interchange Journal Articles   -->
<!--                                                               -->
<!--  PURPOSE:   Provide an HTML preview of a journal article,     -->
<!--             in a form suitable for reading.                   -->
<!--                                                               -->
<!--  PROCESSOR DEPENDENCIES:                                      -->
<!--             None: standard XSLT 1.0                           -->
<!--             Tested using Saxon 6.5, Tranformiix (Firefox),    -->
<!--               Saxon 9.4.0.3                                   -->
<!--                                                               -->
<!--  COMPONENTS REQUIRED:                                         -->
<!--             1) This stylesheet                                -->
<!--             2) CSS styles defined in jats-preview.css         -->
<!--                (to be placed with the results)                -->
<!--                                                               -->
<!--  INPUT:     An XML document valid to (any of) the             -->
<!--             NISO JATS 1.0, NLM/NCBI Journal Publishing 3.0,   -->
<!--             or NLM/NCBI Journal Publishing 2.3 DTDs.          -->
<!--             (May also work with older variants,               -->
<!--             and note further assumptions and limitations      -->
<!--             below.)                                           -->
<!--                                                               -->
<!--  OUTPUT:    HTML (XHTML if a postprocessor is used)           -->
<!--                                                               -->
<!--  CREATED FOR:                                                 -->
<!--             Digital Archive of Journal Articles               -->
<!--             National Center for Biotechnology Information (NCBI)     -->
<!--             National Library of Medicine (NLM)                -->
<!--                                                               -->
<!--  CREATED BY:                                                  -->
<!--             Wendell Piez (based on HTML design by             -->
<!--             Kate Hamilton and Debbie Lapeyre, 2004),          -->
<!--             Mulberry Technologies, Inc.                       -->
<!--                                                               -->
<!-- ============================================================= -->

<!-- ============================================================= -->
<!--
  This work is in the public domain and may be reproduced, published or
  otherwise used without the permission of the National Library of Medicine (NLM).

  We request only that the NLM is cited as the source of the work.

  Although all reasonable efforts have been taken to ensure the accuracy and
  reliability of the software and data, the NLM and the U.S. Government  do
  not and cannot warrant the performance or results that may be obtained  by
  using this software or data. The NLM and the U.S. Government disclaim all
  warranties, express or implied, including warranties of performance,
  merchantability or fitness for any particular purpose.
-->
<!-- ============================================================= -->

<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                xmlns:mml="http://www.w3.org/1998/Math/MathML"
                exclude-result-prefixes="xlink mml">

    <xsl:output method="html"
                doctype-public="-//W3C//DTD HTML 4.01 Transitional//EN"
                doctype-system="http://www.w3.org/TR/html4/loose.dtd"
                encoding="UTF-8"/>

    <xsl:strip-space elements="*"/>

    <!-- Space is preserved in all elements allowing #PCDATA -->
    <xsl:preserve-space
            elements="addr-line aff alt-text article-id article-title attrib bold
              comment contrib-id copyright-holder copyright-statement copyright-year
              day def-head disp-formula email ext-link fax fpage given-names
              inline-formula institution issn issue italic journal-id journal-subtitle journal-title
              kwd label lpage meta-name meta-value mixed-citation month named-content object-id
              p person-group phone prefix preformat publisher-loc publisher-name
              related-article related-object role sc self-uri source strike styled-content
              sub subject subtitle sup surname td term term-head th title trans-title
              underline uri volume xref year
              mml:annotation mml:ci mml:cn mml:csymbol mml:mi mml:mn mml:mo mml:ms mml:mtext"/>


    <!-- ============================================================= -->
    <!--  TOP LEVEL                                                    -->
    <!-- ============================================================= -->


    <xsl:template match="article">
        <xsl:call-template name="make-article"/>
    </xsl:template>


    <xsl:template name="make-article">
        <xsl:variable name="this-article">
            <xsl:apply-templates select="." mode="id"/>
        </xsl:variable>
        <div id="article-all" class="row">
            <div id="article-front" class="front col-3">
                <xsl:apply-templates select="front | front-stub"/>
            </div>
            <div id="article-content" class="content col-9">
                <!-- body -->
                <xsl:for-each select="body">
                    <div id="article-body" class="body">
                        <xsl:apply-templates/>
                    </div>
                </xsl:for-each>
                <!-- appendix-->
                <xsl:if test="back | $loose-footnotes">
                    <!-- $loose-footnotes is defined below as any footnotes outside front matter or fn-group -->
                    <div id="article-back" class="back">
                        <xsl:call-template name="make-back"/>
                    </div>
                </xsl:if>
            </div>
        </div>
    </xsl:template>


    <xsl:template match="front | front-stub">
        <xsl:call-template name="metadata-and-toc"/>
    </xsl:template>


    <!-- ============================================================= -->
    <!--  HTML / EasySection spefific (no valid JATS)                  -->
    <!-- ============================================================= -->


    <xsl:template match="heading">
        <xsl:variable name="tag">
            <xsl:choose>
                <xsl:when test="@level = 'h1' or @level = 'h2' or @level = 'h3' or
                                @level = 'h4' or @level = 'h5' or @level = 'h6'">
                    <xsl:value-of select="@level"/>
                </xsl:when>
                <xsl:otherwise>h2</xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:element name="{$tag}">
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>


    <!-- ============================================================= -->
    <!--  REGULAR (DEFAULT) MODE                                       -->
    <!-- ============================================================= -->


    <xsl:template match="sec">
        <xsl:variable name="level" select="count(ancestor::sec | ancestor::app-group | ancestor::app) + 2"/>
        <xsl:variable name="heading-tag">
            <xsl:choose>
                <xsl:when test="$level &lt;= 6">
                    <xsl:value-of select="concat('h', $level)"/>
                </xsl:when>
                <xsl:otherwise>h6</xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <div class="section" data-sec-type="{@sec-type}">
            <xsl:call-template name="named-anchor"/>
            <xsl:if test="label or title">
                <xsl:element name="{$heading-tag}">
                    <xsl:attribute name="class">title</xsl:attribute>
                    <xsl:if test="label">
                        <span class="label">
                            <xsl:apply-templates select="label/node()"/>
                        </span>
                        <xsl:text> </xsl:text>
                    </xsl:if>
                    <xsl:apply-templates select="title/node()"/>
                    <xsl:if test="processing-instruction('section-edit-link')">
                        <a aria-label="Bearbeiten" class="section-edit-link" href="{normalize-space(processing-instruction('section-edit-link'))}">
                            <i class="bi bi-pen-fill"></i>
                        </a>
                    </xsl:if>
                </xsl:element>
            </xsl:if>
            <xsl:apply-templates mode="drop-title"/>
        </div>
    </xsl:template>


    <xsl:template match="*" mode="drop-title">
        <xsl:apply-templates select="."/>
    </xsl:template>


    <xsl:template match="title | label" mode="drop-title"/>

    <xsl:template match="processing-instruction()" mode="drop-title">
        <xsl:apply-templates select="."/>
    </xsl:template>


    <xsl:template match="app">
        <div class="section app">
            <xsl:call-template name="named-anchor"/>
            <!-- <xsl:apply-templates select="." mode="label"/> -->
            <xsl:if test="label or title">
                <h3>
                    <xsl:attribute name="class">title</xsl:attribute>
                    <xsl:if test="label">
                        <span class="label">
                            <xsl:apply-templates select="label/node()"/>
                        </span>
                        <xsl:text> </xsl:text>
                    </xsl:if>
                    <xsl:apply-templates select="title/node()"/>
                    <xsl:if test="processing-instruction('section-edit-link')">
                        <a aria-label="Bearbeiten" class="section-edit-link" href="{normalize-space(processing-instruction('section-edit-link'))}">
                            <i class="bi bi-pen-fill"></i>
                        </a>
                    </xsl:if>
                </h3>
            </xsl:if>
            <xsl:apply-templates mode="drop-title"/>
        </div>
    </xsl:template>


    <xsl:template match="ref-list" name="ref-list">
        <div class="section ref-list">
            <xsl:call-template name="named-anchor"/>
            <xsl:if test="label or title">
                <h3 class="title">
                    <xsl:if test="label">
                        <span class="label">
                            <xsl:apply-templates select="label/node()"/>
                        </span>
                        <xsl:text> </xsl:text>
                    </xsl:if>
                    <xsl:apply-templates select="title/node()"/>
                </h3>
            </xsl:if>
            <xsl:apply-templates select="*[not(self::ref | self::ref-list | self::label | self::title)]"/>
            <xsl:if test="ref">
                <ul>
                    <xsl:apply-templates select="ref"/>
                </ul>
            </xsl:if>
            <xsl:apply-templates select="ref-list"/>
        </div>
    </xsl:template>


    <!-- ============================================================= -->
    <!--  Titles                                                       -->
    <!-- ============================================================= -->


    <xsl:template name="main-title"
                  match="abstract/title | body/*/title |
           back/title | back[not(title)]/*/title">
        <xsl:param name="contents">
            <xsl:apply-templates/>
        </xsl:param>
        <xsl:if test="normalize-space(string($contents))">
            <!-- coding defensively since empty titles make glitchy HTML -->
            <h2 class="main-title">
                <xsl:copy-of select="$contents"/>
            </h2>
        </xsl:if>
    </xsl:template>


    <xsl:template name="section-title"
                  match="abstract/*/title | body/*/*/title |
		       back[title]/*/title | back[not(title)]/*/*/title">
        <xsl:param name="contents">
            <xsl:apply-templates/>
        </xsl:param>
        <xsl:if test="normalize-space(string($contents))">
            <!-- coding defensively since empty titles make glitchy HTML -->
            <h3 class="section-title">
                <xsl:copy-of select="$contents"/>
            </h3>
        </xsl:if>
    </xsl:template>


    <xsl:template name="subsection-title"
                  match="abstract/*/*/title | body/*/*/*/title |
		       back[title]/*/*/title | back[not(title)]/*/*/*/title">
        <xsl:param name="contents">
            <xsl:apply-templates/>
        </xsl:param>
        <xsl:if test="normalize-space(string($contents))">
            <!-- coding defensively since empty titles make glitchy HTML -->
            <h4 class="subsection-title">
                <xsl:copy-of select="$contents"/>
            </h4>
        </xsl:if>
    </xsl:template>


    <xsl:template match="glossary/title" priority="3">
        <xsl:if test="normalize-space(string(.))">
            <xsl:variable name="level"
                          select="count(ancestor::sec | ancestor::app-group |
                                        ancestor::app | ancestor::glossary) + 1 +
                                  count(ancestor::back[title])"/>
            <xsl:variable name="heading-tag">
                <xsl:choose>
                    <xsl:when test="$level &lt;= 6">
                        <xsl:value-of select="concat('h', $level)"/>
                    </xsl:when>
                    <xsl:otherwise>h6</xsl:otherwise>
                </xsl:choose>
            </xsl:variable>
            <xsl:element name="{$heading-tag}">
                <xsl:attribute name="class">title</xsl:attribute>
                <xsl:if test="../label">
                    <span class="label">
                        <xsl:apply-templates select="../label/node()"/>
                    </span>
                    <xsl:text> </xsl:text>
                </xsl:if>
                <xsl:apply-templates/>
                <xsl:if test="../processing-instruction('section-edit-link')">
                    <a aria-label="Bearbeiten" class="section-edit-link" href="{normalize-space(../processing-instruction('section-edit-link'))}">
                        <i class="bi bi-pen-fill"></i>
                    </a>
                </xsl:if>
            </xsl:element>
        </xsl:if>
    </xsl:template>


    <xsl:template name="block-title" priority="2"
                  match="list/title | def-list/title | boxed-text/title">
        <xsl:param name="contents">
            <xsl:apply-templates/>
        </xsl:param>
        <xsl:if test="normalize-space(string($contents))">
            <!-- coding defensively since empty titles make glitchy HTML -->
            <h4 class="block-title">
                <xsl:copy-of select="$contents"/>
            </h4>
        </xsl:if>
    </xsl:template>


    <!-- default: any other titles found -->
    <xsl:template match="title">
        <xsl:if test="normalize-space(string(.))">
            <h3 class="title">
                <xsl:apply-templates/>
            </h3>
        </xsl:if>
    </xsl:template>


    <xsl:template match="subtitle">
        <xsl:if test="normalize-space(string(.))">
            <h5 class="subtitle">
                <xsl:apply-templates/>
            </h5>
        </xsl:if>
    </xsl:template>


    <!-- ============================================================= -->
    <!--  Figures, lists and block-level objectS                       -->
    <!-- ============================================================= -->


    <xsl:template match="fig-group">
        <div class="{local-name()}">
            <xsl:apply-templates/>
        </div>
    </xsl:template>

    <xsl:template match="attrib">
        <p class="attrib">
            <xsl:apply-templates/>
        </p>
    </xsl:template>


    <xsl:template match="boxed-text | fig | table-wrap">
        <xsl:variable name="gi" select="local-name(.)"/>
        <div class="{$gi} panel">
            <xsl:if test="not(@position != 'float')">
                <!-- the test respects @position='float' as the default -->
                <xsl:attribute name="style">display: float; clear: both</xsl:attribute>
            </xsl:if>
            <xsl:call-template name="named-anchor"/>
            <xsl:choose>
                <xsl:when test="self::fig and graphic">
                    <xsl:apply-templates select="graphic"/>
                    <xsl:if test="label or caption">
                        <div class="caption">
                            <xsl:variable name="label-text" select="normalize-space(string(label))"/>
                            <xsl:if test="$label-text">
                                <span class="label">
                                    <xsl:copy-of select="$label-text"/>
                                </span>
                            </xsl:if>
                            <xsl:if test="caption/title">
                                <span class="title">
                                    <xsl:apply-templates select="caption/title/node()"/>
                                </span>
                            </xsl:if>
                            <xsl:if test="caption/p">
                                <span class="caption-text">
                                    <xsl:apply-templates select="caption/p/node()"/>
                                </span>
                            </xsl:if>
                        </div>
                    </xsl:if>
                    <xsl:apply-templates
                        select="*[not(self::graphic or self::label or self::caption or self::alt-text)]"/>
                </xsl:when>
                <xsl:when test="self::table-wrap">
                    <xsl:if test="label or caption">
                        <div class="caption">
                            <xsl:variable name="label-text" select="normalize-space(string(label))" />
                            <xsl:if test="$label-text">
                                <span class="label">
                                    <xsl:copy-of select="$label-text"/>
                                </span>
                            </xsl:if>
                            <xsl:if test="caption/title">
                                <span class="title">
                                    <xsl:apply-templates select="caption/title/node()"/>
                                </span>
                            </xsl:if>
                            <xsl:if test="caption/p">
                                <span class="caption-text">
                                    <xsl:apply-templates select="caption/p/node()"/>
                                </span>
                            </xsl:if>
                        </div>
                    </xsl:if>
                    <div class="table-responsive">
                        <xsl:apply-templates select="*[not(self::label or self::caption)]"/>
                    </div>
                    <xsl:apply-templates mode="footnote" select="self::table-wrap//fn"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:if test="label or caption">
                        <div class="caption">
                            <xsl:variable name="label-text" select="normalize-space(string(label))" />
                            <xsl:if test="$label-text">
                                <span class="label">
                                    <xsl:copy-of select="$label-text"/>
                                    <xsl:text> </xsl:text>
                                </span>
                            </xsl:if>
                            <xsl:if test="caption/title">
                                <span class="title">
                                    <xsl:apply-templates select="caption/title/node()"/>
                                </span>
                            </xsl:if>
                            <xsl:if test="caption/p">
                                <span class="caption-text">
                                    <xsl:apply-templates select="caption/p/node()"/>
                                </span>
                            </xsl:if>
                        </div>
                    </xsl:if>
                    <xsl:apply-templates select="*[not(self::label or self::caption)]"/>
                </xsl:otherwise>
            </xsl:choose>
        </div>
    </xsl:template>


    <xsl:template match="caption">
        <div class="caption">
            <xsl:apply-templates/>
        </div>
    </xsl:template>


    <xsl:template match="disp-formula">
        <div class="{local-name()} panel">
            <xsl:call-template name="named-anchor"/>
            <xsl:apply-templates/>
        </div>
    </xsl:template>


    <xsl:template match="glossary">
        <div class="glossary">
            <xsl:call-template name="named-anchor"/>
            <xsl:apply-templates select="title"/>
            <xsl:if test="not(title)">
                <xsl:apply-templates select="label"/>
            </xsl:if>
            <xsl:if test="not(normalize-space(string(title)))">
                <xsl:call-template name="block-title">
                    <xsl:with-param name="contents">
                        <span class="generated">Glossar</span>
                    </xsl:with-param>
                </xsl:call-template>
            </xsl:if>
            <xsl:apply-templates select="*[not(self::label|self::title)]"/>
        </div>
    </xsl:template>


    <xsl:template match="graphic | inline-graphic">
        <xsl:apply-templates/>
        <img>
            <xsl:attribute name="alt">
                <xsl:choose>
                    <xsl:when test="alt-text">
                        <xsl:value-of select="normalize-space(string(alt-text[1]))"/>
                    </xsl:when>
                    <xsl:when test="ancestor::fig/alt-text">
                        <xsl:value-of select="normalize-space(string((ancestor::fig/alt-text)[1]))"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="@xlink:href"/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:attribute>
            <xsl:if test="@specific-use">
                <xsl:choose>
                    <xsl:when test="@specific-use='image-size:icon'">
                        <xsl:attribute name="class">image-size-icon</xsl:attribute>
                    </xsl:when>
                    <xsl:when test="@specific-use='image-size:s'">
                        <xsl:attribute name="class">image-size-small</xsl:attribute>
                    </xsl:when>
                    <xsl:when test="@specific-use='image-size:m'">
                        <xsl:attribute name="class">image-size-medium</xsl:attribute>
                    </xsl:when>
                    <xsl:when test="@specific-use='image-size:l'">
                        <xsl:attribute name="class">image-size-large</xsl:attribute>
                    </xsl:when>
                </xsl:choose>
            </xsl:if>
            <xsl:call-template name="assign-src"/>
        </img>
    </xsl:template>


    <xsl:template match="alt-text">
        <!-- handled with graphic or inline-graphic -->
    </xsl:template>


    <xsl:template match="list">
        <div class="list">
            <xsl:call-template name="named-anchor"/>
            <xsl:apply-templates select="label | title"/>
            <xsl:apply-templates select="." mode="list"/>
        </div>
    </xsl:template>


    <xsl:template priority="2" mode="list"
                  match="list[@list-type='simple' or list-item/label]">
        <ul style="list-style-type: none">
            <xsl:apply-templates select="list-item"/>
        </ul>
    </xsl:template>


    <xsl:template match="list[@list-type='bullet' or not(@list-type)]" mode="list">
        <ul>
            <xsl:apply-templates select="list-item"/>
        </ul>
    </xsl:template>


    <xsl:template match="list" mode="list">
        <xsl:variable name="style">
            <xsl:choose>
                <xsl:when test="@list-type='alpha-lower'">lower-alpha</xsl:when>
                <xsl:when test="@list-type='alpha-upper'">upper-alpha</xsl:when>
                <xsl:when test="@list-type='roman-lower'">lower-roman</xsl:when>
                <xsl:when test="@list-type='roman-upper'">upper-roman</xsl:when>
                <xsl:otherwise>decimal</xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <ol style="list-style-type: {$style}">
            <xsl:apply-templates select="list-item"/>
        </ol>
    </xsl:template>


    <xsl:template match="list-item">
        <li>
            <xsl:apply-templates/>
        </li>
    </xsl:template>


    <xsl:template match="list-item/label">
        <!-- if the next sibling is a p, the label will be called as
             a run-in -->
        <xsl:if test="following-sibling::*[1][not(self::p)]">
            <xsl:call-template name="label"/>
        </xsl:if>
    </xsl:template>


    <xsl:template match="media">
        <a>
            <xsl:call-template name="assign-id"/>
            <xsl:call-template name="assign-href"/>
            <xsl:apply-templates/>
        </a>
    </xsl:template>


    <xsl:template match="p">
        <p>
            <xsl:if test="not(preceding-sibling::*)">
                <xsl:attribute name="class">first</xsl:attribute>
            </xsl:if>
            <xsl:call-template name="assign-id"/>
            <xsl:apply-templates/>
        </p>
    </xsl:template>


    <xsl:template match="list-item/p[not(preceding-sibling::*[not(self::label)])]">
        <p>
            <xsl:call-template name="assign-id"/>
            <xsl:for-each select="preceding-sibling::label">
                <span class="label">
                    <xsl:apply-templates/>
                </span>
                <xsl:text> </xsl:text>
            </xsl:for-each>
            <xsl:apply-templates/>
        </p>
    </xsl:template>


    <xsl:template match="permissions">
        <xsl:if test="normalize-space(string(copyright-statement)) or descendant-or-self::*/@*[normalize-space(.)]">
            <div class="permissions">
                <xsl:apply-templates select="copyright-statement"/>
            </div>
        </xsl:if>
    </xsl:template>


    <xsl:template match="copyright-statement">
        <p class="copyright">
            <xsl:apply-templates></xsl:apply-templates>
        </p>
    </xsl:template>


    <xsl:template match="def-list">
        <div class="def-list">
            <xsl:call-template name="named-anchor"/>
            <xsl:apply-templates select="label | title"/>
            <div class="def-list">
                <xsl:if test="term-head|def-head">
                    <div class="row">
                        <div class="col def-list-head">
                            <xsl:apply-templates select="term-head"/>
                        </div>
                        <div class="col def-list-head">
                            <xsl:apply-templates select="def-head"/>
                        </div>
                    </div>
                </xsl:if>
                <xsl:apply-templates select="def-item"/>
            </div>
            <xsl:apply-templates select="def-list"/>
        </div>
    </xsl:template>


    <xsl:template match="def-item">
        <div class="row def-item">
            <xsl:call-template name="assign-id"/>
            <xsl:apply-templates/>
        </div>
    </xsl:template>


    <xsl:template match="term">
        <div class="col def-term">
            <xsl:call-template name="assign-id"/>
            <p>
                <xsl:apply-templates/>
            </p>
        </div>
    </xsl:template>


    <xsl:template match="def">
        <div class="col def-def">
            <xsl:call-template name="assign-id"/>
            <xsl:apply-templates/>
        </div>
    </xsl:template>


    <xsl:template match="disp-quote">
        <div class="blockquote">
            <xsl:call-template name="named-anchor"/>
            <xsl:apply-templates/>
        </div>
    </xsl:template>


    <xsl:template match="ref">
        <li>
            <xsl:variable name="ref-label" select="normalize-space(string(label))" />
            <xsl:if test="$ref-label">
                <span>
                    <xsl:copy-of select="$ref-label"/>
                    <xsl:text> </xsl:text>
                </span>
            </xsl:if>
            <xsl:apply-templates/>
        </li>
    </xsl:template>


    <xsl:template match="ref/*" priority="0">
        <!-- should match mixed-citation; label should be matched below -->
        <p class="citation">
            <xsl:call-template name="named-anchor"/>
            <xsl:apply-templates/>
        </p>
    </xsl:template>


    <xsl:template match="mml:*">
        <!-- HTML requires unprefixed MathML element names. -->
        <xsl:element name="{local-name()}" namespace="http://www.w3.org/1998/Math/MathML">
            <xsl:copy-of select="@*"/>
            <xsl:if test="self::mml:math">
                <xsl:attribute name="class">
                    <xsl:value-of select="normalize-space(concat(@class, ' nexus-exclude'))"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>


    <xsl:template match="mixed-citation/label">
        <!-- these labels appear in line -->
        <span class="generated">[</span>
        <xsl:apply-templates/>
        <span class="generated">]</span>
    </xsl:template>


    <xsl:template match="app/label | boxed-text/label |
    disp-formula/label | fig/label | fn/label | ref/label | table-wrap/label"
                  priority="2">
        <!-- suppressed, since acquired by their parents in mode="label" -->
    </xsl:template>


    <xsl:template match="p/label">
        <span class="label">
            <xsl:apply-templates/>
        </span>
    </xsl:template>

    <xsl:template match="label" name="label">
        <!-- other labels are displayed as blocks -->
        <h5 class="label">
            <xsl:apply-templates/>
        </h5>
    </xsl:template>


    <!-- ============================================================= -->
    <!--  TABLES                                                       -->
    <!-- ============================================================= -->
    <!--  Tables are already in XHTML, and can simply be copied
          through                                                      -->


    <xsl:template match="table">
        <xsl:copy>
            <xsl:apply-templates select="@*" mode="table-copy"/>
            <xsl:attribute name="class">
                <xsl:choose>
                    <xsl:when test="@class">table table-bordered
                        <xsl:value-of select="@class"/>
                    </xsl:when>
                    <xsl:otherwise>table table-bordered</xsl:otherwise>
                </xsl:choose>
            </xsl:attribute>
            <xsl:call-template name="named-anchor"/>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="thead | tbody | tfoot | col | colgroup | tr">
        <xsl:copy>
            <xsl:apply-templates select="@*" mode="table-copy"/>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="th | td">
        <xsl:copy>
            <xsl:apply-templates select="@*" mode="table-copy"/>
            <xsl:call-template name="named-anchor"/>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>


    <xsl:template match="@*" mode="table-copy">
        <xsl:copy-of select="."/>
    </xsl:template>


    <xsl:template match="@content-type" mode="table-copy"/>


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


    <!-- inline-graphic is handled above, with graphic -->


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


    <!-- ============================================================= -->
    <!--  BACK MATTER                                                  -->
    <!-- ============================================================= -->


    <xsl:variable name="loose-footnotes"
                  select="//fn[not(ancestor::front|ancestor::table-wrap)]"/>


    <xsl:template name="make-back">
        <xsl:apply-templates select="back"/>
        <xsl:if test="$loose-footnotes and not(back)">
            <!-- autogenerating a section for footnotes only if there is no
                 back element, and if footnotes exist for it -->
            <xsl:call-template name="footnotes"/>
        </xsl:if>
    </xsl:template>

    <xsl:template match="back">
        <!-- content model for back:
              (label?, title*,
              (app-group | glossary | ref-list)*) -->
        <xsl:if test="$loose-footnotes">
            <xsl:call-template name="footnotes"/>
        </xsl:if>
        <xsl:apply-templates/>
    </xsl:template>


    <xsl:template name="footnotes">
        <xsl:call-template name="backmatter-section">
            <xsl:with-param name="generated-title">Anmerkungen</xsl:with-param>
            <xsl:with-param name="contents">
                <xsl:apply-templates select="$loose-footnotes" mode="footnote"/>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>


    <xsl:template match="app-group">
        <xsl:call-template name="backmatter-section">
            <xsl:with-param name="generated-title">Anhänge</xsl:with-param>
            <xsl:with-param name="is-app-group" select="true()"/>
        </xsl:call-template>
    </xsl:template>


    <xsl:template match="back/glossary">
        <xsl:call-template name="backmatter-section">
            <xsl:with-param name="generated-title">Glossar</xsl:with-param>
            <xsl:with-param name="is-glossary" select="true()"/>
        </xsl:call-template>
    </xsl:template>


    <xsl:template match="back/ref-list">
        <xsl:call-template name="backmatter-section">
            <xsl:with-param name="generated-title">Literaturverzeichnis</xsl:with-param>
            <xsl:with-param name="contents">
                <xsl:call-template name="ref-list"/>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>


    <xsl:template name="backmatter-section">
        <xsl:param name="generated-title"/>
        <xsl:param name="is-app-group" select="false()"/>
        <xsl:param name="is-glossary" select="false()"/>
        <xsl:param name="contents">
            <xsl:if test="($is-app-group or $is-glossary) and title">
                <xsl:apply-templates mode="drop-title"/>
            </xsl:if>
            <xsl:if test="not($is-app-group or $is-glossary) or not(title)">
                <xsl:apply-templates/>
            </xsl:if>
        </xsl:param>
        <div class="section">
            <xsl:call-template name="named-anchor"/>
            <xsl:if test="$is-app-group and title">
                <h2 class="title">
                    <xsl:if test="label">
                        <span class="label">
                            <xsl:apply-templates select="label/node()"/>
                        </span>
                        <xsl:text> </xsl:text>
                    </xsl:if>
                    <xsl:apply-templates select="title/node()"/>
                    <xsl:if test="processing-instruction('section-edit-link')">
                        <a aria-label="Bearbeiten" class="section-edit-link" href="{normalize-space(processing-instruction('section-edit-link'))}">
                            <i class="bi bi-pen-fill"></i>
                        </a>
                    </xsl:if>
                </h2>
            </xsl:if>
            <xsl:if test="$is-glossary and title">
                <xsl:apply-templates select="title"/>
            </xsl:if>
            <xsl:if test="not(title) and $generated-title">
                <xsl:choose>
                    <!-- The level of title depends on whether the back matter itself
                         has a title -->
                    <xsl:when test="ancestor::back/title">
                        <xsl:call-template name="section-title">
                            <xsl:with-param name="contents" select="$generated-title"/>
                        </xsl:call-template>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:call-template name="main-title">
                            <xsl:with-param name="contents" select="$generated-title"/>
                        </xsl:call-template>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:if>
            <xsl:copy-of select="$contents"/>
        </div>
    </xsl:template>


    <!-- ============================================================= -->
    <!--  FOOTNOTES                                                    -->
    <!-- ============================================================= -->

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


    <!-- ============================================================= -->
    <!--  UTILITY TEMPLATES                                           -->
    <!-- ============================================================= -->


    <xsl:template name="assign-id">
        <xsl:variable name="id">
            <xsl:apply-templates select="." mode="id"/>
        </xsl:variable>
        <xsl:attribute name="id">
            <xsl:value-of select="$id"/>
        </xsl:attribute>
    </xsl:template>


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


    <xsl:template name="named-anchor">
        <!-- generates an HTML named anchor -->
        <xsl:variable name="id">
            <xsl:choose>
                <xsl:when test="@id">
                    <!-- if we have an @id, we use it -->
                    <xsl:value-of select="@id"/>
                </xsl:when>
                <xsl:otherwise>
                    <!-- otherwise we simply generate an ID -->
                    <xsl:value-of select="generate-id(.)"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <a id="{$id}">
            <xsl:comment>named anchor</xsl:comment>
        </a>
    </xsl:template>


    <!-- ============================================================= -->
    <!--  id mode                                                      -->
    <!-- ============================================================= -->
    <!-- An id can be derived for any element. If an @id is given,
         it is presumed unique and copied. If not, one is generated.   -->

    <xsl:template match="*" mode="id">
        <xsl:value-of select="@id"/>
        <xsl:if test="not(@id)">
            <xsl:value-of select="generate-id(.)"/>
        </xsl:if>
    </xsl:template>


    <xsl:template match="article" mode="id">
        <xsl:value-of select="@id"/>
        <xsl:if test="not(@id)">
            <xsl:value-of select="local-name()"/>
            <xsl:number from="article" level="multiple"
                        count="article" format="1-1"/>
        </xsl:if>
    </xsl:template>


    <!-- ============================================================= -->
    <!--  "format-date"                                                -->
    <!-- ============================================================= -->
    <!-- Maps a structured date element to a string -->

    <xsl:template name="format-date">
        <!-- formats date in DD Month YYYY format -->
        <!-- context must be 'date', with content model:
             (((day?, month?) | season)?, year) -->
        <xsl:for-each select="day">
            <xsl:apply-templates select="." mode="map"/>
            <xsl:text>. </xsl:text>
        </xsl:for-each>
        <xsl:for-each select="month|season">
            <xsl:apply-templates select="." mode="map"/>
            <xsl:text> </xsl:text>
        </xsl:for-each>
        <xsl:apply-templates select="year" mode="map"/>
    </xsl:template>


    <xsl:template match="day | season | year" mode="map">
        <xsl:apply-templates/>
    </xsl:template>


    <!-- ============================================================= -->
    <!--  "language-name-de" maps a language code to a German name     -->
    <!-- ============================================================= -->

    <xsl:template name="language-name-de">
        <xsl:param name="lang"/>
        <!-- the primary subtag is everything before '-', '_' or space -->
        <xsl:variable name="code"
                      select="translate(substring-before(concat($lang, '-'), '-'),
                                        'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                                        'abcdefghijklmnopqrstuvwxyz')"/>
        <xsl:choose>
            <xsl:when test="$code = 'de'">Deutsch</xsl:when>
            <xsl:when test="$code = 'en'">Englisch</xsl:when>
            <xsl:when test="$code = 'fr'">Franz&#246;sisch</xsl:when>
            <xsl:when test="$code = 'es'">Spanisch</xsl:when>
            <xsl:when test="$code = 'it'">Italienisch</xsl:when>
            <xsl:when test="$code = 'nl'">Niederl&#228;ndisch</xsl:when>
            <xsl:when test="$code = 'pl'">Polnisch</xsl:when>
            <xsl:when test="$code = 'cs'">Tschechisch</xsl:when>
            <xsl:when test="$code = 'da'">D&#228;nisch</xsl:when>
            <xsl:when test="$code = 'sv'">Schwedisch</xsl:when>
            <xsl:when test="$code = 'no'">Norwegisch</xsl:when>
            <xsl:when test="$code = 'fi'">Finnisch</xsl:when>
            <xsl:when test="$code = 'tr'">T&#252;rkisch</xsl:when>
            <xsl:when test="$code = 'ru'">Russisch</xsl:when>
            <xsl:when test="$code = 'uk'">Ukrainisch</xsl:when>
            <xsl:when test="$code = 'zh'">Chinesisch</xsl:when>
            <xsl:when test="$code = 'ja'">Japanisch</xsl:when>
            <xsl:when test="$code = 'ar'">Arabisch</xsl:when>
            <xsl:when test="$code = 'pt'">Portugiesisch</xsl:when>
            <xsl:otherwise>
                <!-- fall back to the raw code when unknown -->
                <xsl:value-of select="$lang"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <xsl:template match="month" mode="map">
        <!-- maps numeric values to German months -->
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
    <!--  DGUV Freie Listen                                            -->
    <!-- ============================================================= -->

    <xsl:template match="p[@content-type='_4octextpara_ListeFrei']">
        <xsl:variable name="level">
            <xsl:call-template name="free-list-level">
                <xsl:with-param name="node" select="."/>
            </xsl:call-template>
        </xsl:variable>

        <xsl:variable name="type">
            <xsl:call-template name="free-list-type">
                <xsl:with-param name="node" select="."/>
            </xsl:call-template>
        </xsl:variable>

        <xsl:variable name="label">
            <xsl:call-template name="free-list-label">
                <xsl:with-param name="node" select="."/>
            </xsl:call-template>
        </xsl:variable>

        <xsl:choose>
            <xsl:when test="count(*) = 1 and count(list) = 1">
                <div class="list" data-list-level="{$level}">
                    <xsl:call-template name="named-anchor"/>
                    <xsl:apply-templates select="label | title"/>
                    <xsl:apply-templates select="." mode="list"/>
                </div>
            </xsl:when>
            <xsl:otherwise>
                <div class="freie-liste" data-list-type="{$type}" data-list-level="{$level}">
                    <p>
                        <xsl:call-template name="assign-id"/>
                        <xsl:if test="normalize-space(string($label))">
                            <span class="list-label">
                                <xsl:copy-of select="$label"/>
                            </span>
                        </xsl:if>
                        <span class="list-item">
                            <xsl:apply-templates select="node()[not(self::named-content[@specific-use='_4octextinline_ListenpunktFrei'])]"/>
                        </span>
                    </p>
                </div>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template name="free-list-level">
        <xsl:param name="node"/>
        <xsl:variable name="pi"
            select="$node/processing-instruction('dguv') [contains(normalize-space(.), 'ListeFrei level=')][1]"/>
        <xsl:choose>
            <xsl:when test="contains(normalize-space($pi), 'level=1')">
                <xsl:text>1</xsl:text>
            </xsl:when>
            <xsl:when test="contains(normalize-space($pi), 'level=2')">
                <xsl:text>2</xsl:text>
            </xsl:when>
            <xsl:when test="contains(normalize-space($pi), 'level=3')">
                <xsl:text>3</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>1</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template name="free-list-type">
        <xsl:param name="node"/>
        <xsl:variable name="marker"
            select="$node/named-content[@specific-use='_4octextinline_ListenpunktFrei'][1]"/>
        <xsl:if test="$marker">
            <xsl:text>ordered</xsl:text>
        </xsl:if>
        <xsl:if test="not($marker)">
            <xsl:text>unordered</xsl:text>
        </xsl:if>
    </xsl:template>

    <xsl:template name="free-list-label">
        <xsl:param name="node"/>
        <xsl:variable name="marker"
            select="$node/named-content[@specific-use='_4octextinline_ListenpunktFrei'][1]"/>
        <xsl:if test="$marker">
            <xsl:apply-templates select="$marker/node()"/>
        </xsl:if>
    </xsl:template>


    <!-- ============================================================= -->
    <!--  DGUV processing instructions                                 -->
    <!-- ============================================================= -->

    <!-- <?dguv toc?> — inserts a table of contents linking to all
         section headings (sec elements with a non-empty title) in the document. -->
        <xsl:template match="processing-instruction('dguv')[normalize-space(.) = 'toc']">
            <xsl:call-template name="metadata-and-toc">
                <xsl:with-param name="front-node" select="//front"/>
            </xsl:call-template>
        </xsl:template>

    <xsl:template name="metadata-and-toc">
        <xsl:param name="front-node" select="."/>
        <div class="metadata-and-toc">
            <div class="metadata-small">
                <table>
                    <!-- Journal Title -->
                    <xsl:variable name="journal-title" select="$front-node/journal-meta/journal-title-group/journal-title" />
                    <xsl:if test="normalize-space(string($journal-title))">
                        <tr data-meta-field="journal-title">
                            <td>
                                <xsl:apply-templates select="$journal-title"/>
                            </td>
                        </tr>
                    </xsl:if>
                    <!-- Journal Subtitle -->
                    <xsl:variable name="journal-subtitle" select="$front-node/journal-meta/journal-title-group/journal-subtitle" />
                    <xsl:if test="normalize-space(string($journal-subtitle))">
                        <tr data-meta-field="journal-subtitle">
                            <td>
                                <xsl:apply-templates select="$journal-subtitle"/>
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
                                <xsl:for-each select="($front-node/article-meta/ext-link | $front-node/article-meta/uri | $front-node/article-meta/self-uri)[1]">
                                    <a href="{@xlink:href}">Publikation</a>
                                </xsl:for-each>
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
                                                            <xsl:with-param name="lang"
                                                                            select="@xml:lang"/>
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
                </table>
            </div>
            <nav class="jats-html-export-toc">
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


    <!-- ============================================================= -->
    <!--  End stylesheet                                               -->
    <!-- ============================================================= -->

</xsl:stylesheet>
