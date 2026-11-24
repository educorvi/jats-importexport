<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <!-- Template for making label and title elements -->
    <xsl:template name="make-label-title">
        <xsl:param name="generated-title"/>
        <xsl:variable name="heading-tag">
            <xsl:call-template name="get-heading-tag" />
        </xsl:variable>
        <xsl:choose>
            <xsl:when test="normalize-space(string(label)) or normalize-space(string(title))">
                <xsl:element name="{$heading-tag}">
                    <xsl:attribute name="class">title</xsl:attribute>
                    <xsl:if test="normalize-space(string(label))">
                        <span class="label">
                            <xsl:apply-templates select="label/node()"/>
                        </span>
                        <xsl:text> </xsl:text>
                    </xsl:if>
                    <xsl:if test="normalize-space(string(title))">
                        <xsl:apply-templates select="title/node()"/>
                    </xsl:if>
                    <xsl:if test="processing-instruction('section-edit-link')">
                        <a aria-label="Bearbeiten" class="section-edit-link" href="{normalize-space(processing-instruction('section-edit-link'))}">
                            <i class="bi bi-pen-fill"></i>
                        </a>
                    </xsl:if>
                </xsl:element>
            </xsl:when>
            <xsl:otherwise>
                <xsl:if test="normalize-space(string($generated-title))">
                    <xsl:element name="{$heading-tag}">
                        <xsl:attribute name="class">title generated-title</xsl:attribute>
                        <xsl:copy-of select="$generated-title"/>
                    </xsl:element>
                </xsl:if>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <!-- template for making a caption -->
    <xsl:template name="make-caption">
        <xsl:if test="label or caption">
            <p class="caption">
                <xsl:attribute name="id">
                    <xsl:value-of select="concat(generate-id(), '-caption')"/>
                </xsl:attribute>
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
            </p>
        </xsl:if>
    </xsl:template>


    <!-- templates for determining the heading level / tag -->


    <xsl:template name="get-heading-level">
        <xsl:variable name="level"
                      select="count(ancestor::sec | ancestor::app-group | ancestor::app | ancestor::glossary | ancestor::ref-list) + 2"/>
        <xsl:choose>
            <xsl:when test="$level &lt;= 6">
                <xsl:value-of select="$level"/>
            </xsl:when>
            <xsl:otherwise>6</xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template name="get-heading-tag">
        <xsl:variable name="level">
            <xsl:call-template name="get-heading-level"/>
        </xsl:variable>
        <xsl:value-of select="concat('h', $level)"/>
    </xsl:template>


    <!-- ============================================================= -->
    <!--  Drop labels, titles and captions in certain contexts         -->
    <!-- ============================================================= -->


    <xsl:template match="*" mode="drop-title">
        <xsl:apply-templates select="."/>
    </xsl:template>


    <xsl:template match="title | label | caption" mode="drop-title"/>


    <!-- ============================================================= -->
    <!--  Default title, labels, default labels                        -->
    <!-- ============================================================= -->


    <!-- default: any other titles found -->
    <xsl:template match="title">
        <xsl:variable name="heading-tag">
            <xsl:call-template name="get-heading-tag"/>
        </xsl:variable>
        <xsl:if test="normalize-space(string(.))">
            <xsl:element name="{$heading-tag}">
                <xsl:attribute name="class">title other</xsl:attribute>
                <xsl:apply-templates/>
            </xsl:element>
        </xsl:if>
    </xsl:template>


    <xsl:template match="mixed-citation/label">
        <!-- these labels appear in line -->
        <span class="generated">[</span>
        <xsl:apply-templates/>
        <span class="generated">]</span>
    </xsl:template>


    <xsl:template match="p/label">
        <!-- these labels appear as inline elements within paragraphs -->
        <span class="label">
            <xsl:apply-templates/>
        </span>
    </xsl:template>


    <!-- default: any other labels found -->
    <xsl:template match="label" name="label">
        <xsl:variable name="heading-tag">
            <xsl:call-template name="get-heading-tag"/>
        </xsl:variable>
        <xsl:element name="{$heading-tag}">
            <xsl:attribute name="class">label other</xsl:attribute>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>

</xsl:stylesheet>
