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


    <xsl:template match="sec-meta" />


    <xsl:template match="fig-group">
        <div class="{local-name()}">
            <xsl:apply-templates/>
        </div>
    </xsl:template>


    <xsl:template match="boxed-text | fig | table-wrap">
        <xsl:variable name="gi" select="local-name(.)"/>
        <xsl:variable name="content-type" select="@content-type"/>
        <div>
            <xsl:if test="(self::fig or self::table-wrap) and (label or caption)">
                <xsl:attribute name="role">figure</xsl:attribute>
                <xsl:attribute name="aria-labelledby">
                    <xsl:value-of select="concat(generate-id(), '-caption')"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:attribute name="class">
                <xsl:value-of select="$gi"/>
                <xsl:text> panel</xsl:text>
                <xsl:if test="self::boxed-text and caption/title/*[(self::graphic or self::inline-graphic) and @specific-use='image-size:icon']">
                    <xsl:text> boxed-text--has-icon</xsl:text>
                </xsl:if>
            </xsl:attribute>
            <xsl:if test="$content-type">
                <xsl:attribute name="data-content-type">
                    <xsl:value-of select="$content-type"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:call-template name="named-anchor"/>
            <xsl:choose>
                <xsl:when test="self::fig">
                    <xsl:apply-templates select="graphic"/>
                    <xsl:call-template name="make-caption"/>
                    <xsl:apply-templates select="*[not(self::graphic or self::alt-text)]" mode="drop-title"/>
                </xsl:when>
                <xsl:when test="self::table-wrap">
                    <xsl:call-template name="make-caption"/>
                    <div class="table-responsive" tabindex="0">
                        <xsl:apply-templates mode="drop-title"/>
                    </div>
                    <xsl:apply-templates mode="footnote" select="self::table-wrap//fn"/>
                </xsl:when>
                <xsl:when test="self::boxed-text">
                    <xsl:call-template name="make-caption"/>
                    <div class="boxed-text-content">
                        <xsl:apply-templates mode="drop-title"/>
                    </div>
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
        <xsl:variable name="tag">
            <xsl:choose>
                <xsl:when test="*[self::fig or self::disp-formula or self::list or self::table-wrap or self::boxed-text]">div</xsl:when>
                <xsl:otherwise>p</xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:element name="{$tag}">
            <xsl:variable name="content-type" select="@content-type"/>
            <xsl:if test="$content-type">
                <xsl:attribute name="data-content-type">
                    <xsl:value-of select="$content-type"/>
                </xsl:attribute>
                <xsl:if test="$content-type='_1UnterUeberschrift'">
                    <xsl:variable name="heading-level">
                        <xsl:call-template name="get-heading-level"/>
                    </xsl:variable>
                    <xsl:attribute name="role">heading</xsl:attribute>
                    <xsl:attribute name="aria-level">
                        <xsl:value-of select="$heading-level"/>
                    </xsl:attribute>
                </xsl:if>
            </xsl:if>
            <xsl:call-template name="assign-id"/>
            <xsl:choose>
                <xsl:when test="$tag = 'div'">
                    <xsl:attribute name="class">div-p</xsl:attribute>
                    <xsl:call-template name="mixed-content"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:apply-templates/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:element>
    </xsl:template>

    <xsl:template name="mixed-content">
        <xsl:param name="nodes" select="node()"/>
        <xsl:for-each select="$nodes">
            <xsl:choose>
                <xsl:when test="self::*[self::fig or self::disp-formula or self::list or self::table-wrap or self::boxed-text]">
                    <xsl:apply-templates select="."/>
                </xsl:when>
                <!-- start of an inline run: previous node is a block or none -->
                <xsl:when test="not(preceding-sibling::node()[1][not(self::*[self::named-content[@specific-use='_4octextinline_ListenpunktFrei'] or self::fig or self::disp-formula or self::list or self::table-wrap or self::boxed-text])])
                                and (normalize-space(.)
                                    or self::*[not(self::named-content[@specific-use='_4octextinline_ListenpunktFrei'] or self::fig or self::disp-formula or self::list or self::table-wrap or self::boxed-text)]
                                    or following-sibling::node()[1][self::*[not(self::named-content[@specific-use='_4octextinline_ListenpunktFrei'] or self::fig or self::disp-formula or self::list or self::table-wrap or self::boxed-text)]])">
                    <p>
                        <xsl:call-template name="inline-run">
                            <xsl:with-param name="node" select="."/>
                        </xsl:call-template>
                    </p>
                </xsl:when>
            </xsl:choose>
        </xsl:for-each>
    </xsl:template>

    <!-- Emits the node, then every directly following inline sibling -->
    <xsl:template name="inline-run">
        <xsl:param name="node"/>
        <xsl:apply-templates select="$node"/>
        <xsl:for-each select="$node/following-sibling::node()[1][not(self::*[self::named-content[@specific-use='_4octextinline_ListenpunktFrei'] or self::fig or self::disp-formula or self::list or self::table-wrap or self::boxed-text])]">
            <xsl:call-template name="inline-run">
                <xsl:with-param name="node" select="."/>
            </xsl:call-template>
        </xsl:for-each>
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


    <xsl:template match="abstract">
        <div class="abstract">
            <xsl:apply-templates/>
        </div>
    </xsl:template>


    <xsl:template match="table">
        <xsl:copy>
            <xsl:apply-templates select="@*" mode="table-copy"/>
            <xsl-if test="not(@id)">
                <xsl:call-template name="assign-id"/>
            </xsl-if>
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
        <xsl:call-template name="named-anchor"/>
        <xsl:apply-templates select="label | title"/>
        <xsl:apply-templates select="." mode="list"/>
    </xsl:template>


    <xsl:template match="list[@list-type='bullet' or not(@list-type)]" mode="list">
        <ul role="list" class="list">
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
                <xsl:when test="@list-type='simple'">none</xsl:when>
                <xsl:otherwise>decimal</xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <ol style="list-style-type: {$style}" role="list" class="list">
            <xsl:apply-templates select="list-item"/>
        </ol>
    </xsl:template>


    <xsl:template match="list-item">
        <li>
            <xsl:apply-templates/>
        </li>
    </xsl:template>


    <!-- ============================================================= -->
    <!--  Other                                                        -->
    <!-- ============================================================= -->


    <xsl:template match="def-list">
        <div class="def-list">
            <xsl:call-template name="named-anchor"/>
            <xsl:call-template name="make-label-title"/>
            <dl>
                <xsl:if test="term-head|def-head">
                    <div class="def-item">
                        <xsl:apply-templates select="term-head"/>
                        <xsl:apply-templates select="def-head"/>
                    </div>
                </xsl:if>
                <xsl:apply-templates select="def-item"/>
            </dl>
            <xsl:apply-templates select="def-list"/>
        </div>
    </xsl:template>


    <xsl:template match="def-item">
        <div class="def-item">
            <xsl:call-template name="assign-id"/>
            <xsl:apply-templates/>
        </div>
    </xsl:template>


    <xsl:template match="term | term-head">
        <dt class="def-term">
            <xsl:call-template name="assign-id"/>
            <xsl:apply-templates/>
        </dt>
    </xsl:template>


    <xsl:template match="def | def-head">
        <dd class="def-def">
            <xsl:call-template name="assign-id"/>
            <xsl:apply-templates/>
        </dd>
    </xsl:template>


    <xsl:template match="disp-quote">
        <blockquote class="blockquote">
            <xsl:call-template name="named-anchor"/>
            <div class="blockquote-content">
                <xsl:apply-templates select="node()[not(self::attrib)]"/>
            </div>
            <xsl:if test="attrib">
                <xsl:for-each select="attrib">
                    <div class="blockquote-attrib">
                        <p>
                            <xsl:apply-templates/>
                        </p>
                    </div>
                </xsl:for-each>
            </xsl:if>
        </blockquote>
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
