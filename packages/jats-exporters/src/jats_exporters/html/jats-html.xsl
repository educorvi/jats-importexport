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

    <xsl:import href="xsl/utils.xsl"/>
    <xsl:import href="xsl/metadata-toc.xsl"/>
    <xsl:import href="xsl/label-title.xsl"/>
    <xsl:import href="xsl/footnotes.xsl"/>
    <xsl:import href="xsl/dguv-liste-frei.xsl"/>
    <xsl:import href="xsl/elements-block.xsl"/>
    <xsl:import href="xsl/elements-inline.xsl"/>

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


    <xsl:variable name="loose-footnotes" select="//fn[not(ancestor::front|ancestor::table-wrap)]"/>


    <!-- ============================================================= -->
    <!--  TOP LEVEL                                                    -->
    <!-- ============================================================= -->


    <xsl:template match="article">
        <xsl:call-template name="make-article"/>
    </xsl:template>


    <xsl:template name="make-article">
        <div class="article-all row">
            <div class="article-front">
                <xsl:call-template name="metadata-and-toc"/>
            </div>
            <div class="article-content">
                <div class="article-body">
                    <xsl:apply-templates select="body"/>
                </div>
                <xsl:if test="back | $loose-footnotes">
                    <div class="article-back">
                        <xsl:call-template name="make-back"/>
                    </div>
                </xsl:if>
            </div>
        </div>
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
    <!--  SECTIONS                                                     -->
    <!-- ============================================================= -->


    <!--  Template for making sections. -->
    <xsl:template name="make-section">
        <xsl:param name="sec-class"/>
        <xsl:param name="sec-type"/>
        <xsl:param name="generated-title"/>
        <xsl:param name="content">
            <xsl:apply-templates mode="drop-title"/>
        </xsl:param>
        <div class="section {$sec-class}">
            <xsl:if test="$sec-type">
                <xsl:attribute name="data-sec-type">
                    <xsl:value-of select="$sec-type"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:call-template name="named-anchor"/>
            <xsl:call-template name="make-label-title">
                <xsl:with-param name="generated-title" select="$generated-title"/>
            </xsl:call-template>
            <xsl:copy-of select="$content"/>
        </div>
    </xsl:template>


    <!-- ============================================================= -->
    <!--  Matching templates for sections                              -->
    <!-- ============================================================= -->


    <xsl:template match="sec">
        <xsl:call-template name="make-section">
            <xsl:with-param name="sec-class" select="'sec'"/>
            <xsl:with-param name="sec-type" select="@sec-type"/>
        </xsl:call-template>
    </xsl:template>


    <xsl:template match="app">
        <xsl:call-template name="make-section">
            <xsl:with-param name="sec-class" select="'app'"/>
            <xsl:with-param name="sec-type" select="@app-type"/>
        </xsl:call-template>
    </xsl:template>


    <xsl:template match="app-group">
        <xsl:call-template name="make-section">
            <xsl:with-param name="sec-class" select="'app-group'"/>
            <xsl:with-param name="sec-type" select="@content-type"/>
        </xsl:call-template>
    </xsl:template>


    <xsl:template match="glossary">
        <xsl:call-template name="make-section">
            <xsl:with-param name="sec-class" select="'glossary'"/>
            <xsl:with-param name="sec-type" select="@content-type"/>
        </xsl:call-template>
    </xsl:template>


    <xsl:template match="ref-list">
        <xsl:call-template name="make-section">
            <xsl:with-param name="sec-class" select="'ref-list'"/>
            <xsl:with-param name="sec-type" select="@content-type"/>
            <xsl:with-param name="content">
                <xsl:apply-templates select="*[not(self::ref | self::ref-list)]" mode="drop-title"/>
                <xsl:if test="ref">
                    <ul>
                        <xsl:apply-templates select="ref"/>
                    </ul>
                </xsl:if>
                <xsl:apply-templates select="ref-list"/>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>


    <!-- ============================================================= -->
    <!--  Make Back Matter, Footnotes and Matching Templates for Back Sections -->
    <!-- ============================================================= -->


    <xsl:template name="make-back">
        <xsl:apply-templates select="back"/>
        <xsl:if test="$loose-footnotes and not(back)">
            <xsl:call-template name="footnotes"/>
        </xsl:if>
    </xsl:template>


    <xsl:template match="back">
        <xsl:if test="$loose-footnotes">
            <xsl:call-template name="footnotes"/>
        </xsl:if>
        <xsl:apply-templates/>
    </xsl:template>


    <xsl:template name="footnotes">
        <xsl:call-template name="make-section">
            <xsl:with-param name="sec-class" select="'footnotes'"/>
            <xsl:with-param name="generated-title">Anmerkungen</xsl:with-param>
            <xsl:with-param name="content">
                <xsl:apply-templates select="$loose-footnotes" mode="footnote"/>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>


    <xsl:template match="back/glossary">
        <xsl:call-template name="make-section">
            <xsl:with-param name="sec-class" select="'glossary'"/>
            <xsl:with-param name="sec-type" select="@content-type"/>
            <xsl:with-param name="generated-title">Glossar</xsl:with-param>
        </xsl:call-template>
    </xsl:template>


    <xsl:template match="back/ref-list">
        <xsl:call-template name="make-section">
            <xsl:with-param name="sec-class" select="'ref-list'"/>
            <xsl:with-param name="generated-title">Literaturverzeichnis</xsl:with-param>
        </xsl:call-template>
    </xsl:template>

</xsl:stylesheet>
