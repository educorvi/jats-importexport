<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

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

        <div class="freie-liste" data-list-type="{$type}" data-list-level="{$level}">
            <xsl:call-template name="assign-id"/>
            <xsl:if test="normalize-space(string($label))">
                <div class="list-label">
                    <xsl:copy-of select="$label"/>
                </div>
            </xsl:if>
            <div class="list-item">
                <xsl:apply-templates select="node()[not(self::named-content[@specific-use='_4octextinline_ListenpunktFrei'])]"/>
            </div>
        </div>
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

</xsl:stylesheet>
