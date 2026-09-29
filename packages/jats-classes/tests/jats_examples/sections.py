from .base import get_jats_doc

_BODY = """
<sec sec-type="intro">
    <label>1.</label>
    <title>Introduction</title>
    <p>This is the first paragraph.</p>
    <sec sec-type="subsection">
        <label>1.1</label>
        <title>Nested Subsection</title>
        <p>Nested content.</p>
    </sec>
</sec>"""

_BACK = """
<app-group content-type="appendices">
    <label>Appendix Group Label</label>
    <title>Appendix Group Title</title>
    <app app-type="annex">
        <label>A</label>
        <title>First Appendix</title>
        <p>Appendix text content.</p>
        <sec>
            <title>Appendix Subsection</title>
            <p>Subtext.</p>
        </sec>
    </app>
</app-group>"""


SECTION_DOCUMENT = get_jats_doc(body=_BODY, back=_BACK)

SECTION_WITH_RAW_CONTENT = """
	<sec>
		<label>L</label>
		<title>T</title>
		<!-- This is a comment -->
		Text node here
		<p>Another paragraph</p>
	</sec>
"""

EMPTY_SECTION = "<sec><label>L</label><title>T</title></sec>"

# --------------------------------------------------
# Section: title/label combinations allowed by the XSD choice
# (either "label + optional title" or "title" alone)
# --------------------------------------------------

SECTION_LABEL_ONLY = """
	<sec>
		<label>2.</label>
		<p>Content with a label but no title.</p>
	</sec>
"""

SECTION_TITLE_ONLY = """
	<sec>
		<title>Title Only Section</title>
		<p>Content with a title but no label.</p>
	</sec>
"""

SECTION_EMPTY_TITLE = """
	<sec>
		<title></title>
		<p>Content.</p>
	</sec>
"""

# --------------------------------------------------
# Section: raw content must stop at the first nested <sec>
# --------------------------------------------------

SECTION_WITH_CONTENT_AFTER_NESTED_SEC = """
	<sec>
		<title>Parent</title>
		<p>Before nested section.</p>
		<sec>
			<title>Child</title>
			<p>Nested content.</p>
		</sec>
	</sec>
"""

# --------------------------------------------------
# Section: title text extraction bypasses named-content/styled-content
# but drops other inline markup (e.g. <bold>) entirely
# --------------------------------------------------

SECTION_TITLE_WITH_NAMED_CONTENT = """
	<sec>
		<title>Intro <named-content content-type="term">Term</named-content> tail</title>
		<p>Content.</p>
	</sec>
"""

SECTION_TITLE_WITH_BOLD = """
	<sec>
		<title>Intro <bold>Bold</bold> tail</title>
		<p>Content.</p>
	</sec>
"""

# --------------------------------------------------
# Body: raw content outside <sec> elements
# --------------------------------------------------

BODY_WITH_STRAY_CONTENT = """
<p>Stray paragraph before any section.</p>
<sec>
    <title>Real Section</title>
    <p>Section content.</p>
</sec>"""

BODY_WITHOUT_STRAY_CONTENT = """
<sec>
    <title>Only Section</title>
    <p>Section content.</p>
</sec>"""

# --------------------------------------------------
# Back / AppendixGroup / Appendix: optional attributes and multiplicity
# --------------------------------------------------

BACK_NO_APP_GROUP = """
<ack>
    <title>Acknowledgements</title>
    <p>Thanks.</p>
</ack>"""

BACK_MULTIPLE_APPENDIX_GROUPS = """
<app-group>
    <title>First Group</title>
    <app>
        <title>First Group Appendix</title>
        <p>Content A.</p>
    </app>
</app-group>
<app-group>
    <title>Second Group</title>
    <app>
        <title>Second Group Appendix</title>
        <p>Content B.</p>
    </app>
</app-group>"""

APP_GROUP_MULTIPLE_APPENDIXES = """
<app-group content-type="appendices">
    <title>Group With Two Appendixes</title>
    <app app-type="annex">
        <label>A</label>
        <title>Appendix A</title>
        <p>Content A.</p>
    </app>
    <app app-type="annex">
        <label>B</label>
        <title>Appendix B</title>
        <p>Content B.</p>
    </app>
</app-group>"""

# app-group's content-type and app's app-type attributes are both optional
APP_GROUP_WITHOUT_OPTIONAL_ATTRIBUTES = """
<app-group>
    <title>Group Without Optional Attributes</title>
    <app>
        <title>Appendix Without Optional Attributes</title>
        <p>Content.</p>
    </app>
</app-group>"""

# --------------------------------------------------
# Full document valid against the real DGUV JATS schema
# (the schema does not define an "app-type" attribute on <app>,
# only "content-type", so this fixture avoids it)
# --------------------------------------------------

_SCHEMA_VALID_BODY = """
<sec sec-type="intro">
    <label>1.</label>
    <title>Introduction</title>
    <p>This is the first paragraph.</p>
    <sec sec-type="subsection">
        <label>1.1</label>
        <title>Nested Subsection</title>
        <p>Nested content.</p>
    </sec>
</sec>"""

_SCHEMA_VALID_BACK = """
<app-group content-type="appendices">
    <label>Appendix Group Label</label>
    <title>Appendix Group Title</title>
    <app content-type="annex">
        <label>A</label>
        <title>First Appendix</title>
        <p>Appendix text content.</p>
        <sec>
            <title>Appendix Subsection</title>
            <p>Subtext.</p>
        </sec>
    </app>
</app-group>"""

SCHEMA_VALID_SECTION_DOCUMENT = get_jats_doc(body=_SCHEMA_VALID_BODY, back=_SCHEMA_VALID_BACK)

# --------------------------------------------------
# Invalid according to the XSD: <sec> must have a title or a label (+ optional title)
# --------------------------------------------------

INVALID_SEC_MISSING_TITLE_AND_LABEL = """
<sec>
    <p>Content without any title or label.</p>
</sec>"""

_INVALID_BODY_MISSING_TITLE_AND_LABEL = INVALID_SEC_MISSING_TITLE_AND_LABEL

INVALID_DOC_SEC_MISSING_TITLE_AND_LABEL = get_jats_doc(body=_INVALID_BODY_MISSING_TITLE_AND_LABEL)

# ref-list must come after nested <sec> elements, not before
_INVALID_BODY_REF_LIST_BEFORE_SEC = """
<sec>
    <title>Invalid Order</title>
    <ref-list>
        <ref><mixed-citation publication-format="print" publication-type="book">Some citation</mixed-citation></ref>
    </ref-list>
    <sec>
        <title>Nested</title>
        <p>Nested content.</p>
    </sec>
</sec>"""

INVALID_DOC_REF_LIST_BEFORE_SEC = get_jats_doc(body=_INVALID_BODY_REF_LIST_BEFORE_SEC)
