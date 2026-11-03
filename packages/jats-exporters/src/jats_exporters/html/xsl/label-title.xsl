<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <!-- Template for making label and title elements -->
    <xsl:template name="make-label-title">
        <xsl:param name="generated-title"/>
        <xsl:variable name="level"
                      select="count(ancestor::sec | ancestor::app-group | ancestor::app | ancestor::glossary | ancestor::ref-list) + 2"/>
        <xsl:variable name="heading-tag">
            <xsl:choose>
                <xsl:when test="$level &lt;= 6">
                    <xsl:value-of select="concat('h', $level)"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="'h6'"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:choose>
            <xsl:when test="label or title">
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


    <!-- ============================================================= -->
    <!--  Drop titles and labels in certain contexts                   -->
    <!-- ============================================================= -->


    <xsl:template match="*" mode="drop-title">
        <xsl:apply-templates select="."/>
    </xsl:template>


    <xsl:template match="title | label" mode="drop-title"/>


    <!-- ============================================================= -->
    <!--  Default title, labels, default labels                        -->
    <!-- ============================================================= -->


    <!-- default: any other titles found -->
    <xsl:template match="title">
        <xsl:if test="normalize-space(string(.))">
            <h3 class="title">
                <xsl:apply-templates/>
            </h3>
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
        <h5 class="label">
            <xsl:apply-templates/>
        </h5>
    </xsl:template>

</xsl:stylesheet>
