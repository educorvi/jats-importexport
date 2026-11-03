<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                xmlns:mml="http://www.w3.org/1998/Math/MathML"
                exclude-result-prefixes="xlink mml">

    <!-- ============================================================= -->
    <!--  BLOCK-LEVEL OBJECTS                                          -->
    <!-- ============================================================= -->


    <!-- ============================================================= -->
    <!--  figures, boxes, table wrappers, etc.                         -->
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
                    <xsl:call-template name="make-caption"/>
                    <xsl:apply-templates select="*[not(self::graphic or self::alt-text)]" mode="drop-title"/>
                </xsl:when>
                <xsl:when test="self::table-wrap">
                    <xsl:call-template name="make-caption"/>
                    <div class="table-responsive">
                        <xsl:apply-templates mode="drop-title"/>
                    </div>
                    <xsl:apply-templates mode="footnote" select="self::table-wrap//fn"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:call-template name="make-caption"/>
                    <xsl:apply-templates mode="drop-title"/>
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


    <!-- ============================================================= -->
    <!--  Tables                                                       -->
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
    <!--  Lists                                                        -->
    <!-- ============================================================= -->


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


    <!-- ============================================================= -->
    <!--  Other                                                        -->
    <!-- ============================================================= -->


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
            <xsl:apply-templates mode="drop-title"/>
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

</xsl:stylesheet>
