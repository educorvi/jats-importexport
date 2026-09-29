from .base import get_jats_doc



SECTION_WITH_DURCHFUEHRUNGSANWEISUNG = """
	<sec>
		<label>1.</label>
		<title>Main Section</title>
		<p>Normal content.</p>
		<p><italic>Durchführungsanweisung</italic> instruction text</p>
		<p>Following content.</p>
	</sec>
"""

SECTION_WITHOUT_DURCHFUEHRUNGSANWEISUNG = """
	<sec>
		<label>1.</label>
		<title>Main Section</title>
		<p>Some content.</p>
		<p>More content.</p>
	</sec>
"""

SECTION_WITH_NESTED_DURCHFUEHRUNGSANWEISUNG = """
	<sec>
		<label>1.</label>
		<title>Main Section</title>
		<p>Intro content.</p>
		<sec>
			<title>Nested</title>
			<p><italic>Durchführungsanweisung</italic> inside nested sec</p>
		</sec>
	</sec>
"""

SECTION_WITH_NESTED_VORBEMERKUNGEN = """
	<sec>
		<label>1.</label>
		<title>Main Section</title>
		<p>Intro content.</p>
		<sec>
			<title>Nested</title>
			<p><span>Vorbemerkungen</span> inside nested sec</p>
		</sec>
	</sec>
"""

SECTION_WITH_PARTIAL_VORBEMERKUNGEN = """
	<sec>
		<label>1.</label>
		<title>Main Section</title>
		<p>Normal content.</p>
		<p><named-content content-type="term">Vorbemerkungen und mehr</named-content> extra text</p>
		<p>Following content.</p>
	</sec>
"""

# --------------------------------------------------
# Durchführungsanweisung: plural form and split guard
# --------------------------------------------------

SECTION_WITH_DURCHFUEHRUNGSANWEISUNGEN_PLURAL = """
	<sec>
		<label>1.</label>
		<title>Main Section</title>
		<p>Normal content.</p>
		<p><italic>Durchführungsanweisungen</italic> plural instruction text</p>
	</sec>
"""

# The DA heading is the very first content: nothing precedes it to split off,
# so no subsection should be created (see the "actual content before the split
# point" guard in Section._split_on_durchfuehrungsanweisung).
SECTION_WITH_DURCHFUEHRUNGSANWEISUNG_AS_FIRST_CONTENT = """
	<sec>
		<label>1.</label>
		<title>Main Section</title>
		<p><italic>Durchführungsanweisung</italic> instruction text</p>
	</sec>
"""

# --------------------------------------------------
# Vorbemerkungen: the split logic only ever matches <named-content>, not <span>
# (the existing SECTION_WITH_*VORBEMERKUNGEN fixtures above use <span> and are
# therefore vacuous - the xpath never matches, so "no split" is trivially true)
# --------------------------------------------------

SECTION_WITH_VORBEMERKUNGEN = """
	<sec>
		<label>1.</label>
		<title>Main Section</title>
		<p><named-content content-type="term">Vorbemerkungen</named-content></p>
		<p>Following content.</p>
	</sec>
"""

SECTION_WITH_NESTED_VORBEMERKUNGEN_NAMED_CONTENT = """
	<sec>
		<label>1.</label>
		<title>Main Section</title>
		<p>Intro content.</p>
		<sec>
			<title>Nested</title>
			<p><named-content content-type="term">Vorbemerkungen</named-content> inside nested sec</p>
		</sec>
	</sec>
"""

# --------------------------------------------------
# Inhaltsverzeichnis / table-of-contents heading variants
# --------------------------------------------------

SECTION_WITH_INHALTSVERZEICHNIS = """
	<sec>
		<title>Main Section</title>
		<p><named-content content-type="term">Inhaltsverzeichnis</named-content></p>
		<p>Following content.</p>
	</sec>
"""

SECTION_WITH_INHALT = """
	<sec>
		<title>Main Section</title>
		<p><named-content content-type="term">Inhalt</named-content></p>
		<p>Following content.</p>
	</sec>
"""

SECTION_WITH_CONTENTS = """
	<sec>
		<title>Main Section</title>
		<p><named-content content-type="term">Contents</named-content></p>
		<p>Following content.</p>
	</sec>
"""

SECTION_WITH_TABLE_OF_CONTENTS = """
	<sec>
		<title>Main Section</title>
		<p><named-content content-type="term">Table of Contents</named-content></p>
		<p>Following content.</p>
	</sec>
"""

# "Manual" table of contents: no named-content text matches directly, but a
# nested <bold>Inhaltsverzeichnis</bold> does (see the "better find manual
# inhaltsverzeichnis" fix).
SECTION_WITH_MANUAL_INHALTSVERZEICHNIS = """
	<sec>
		<title>Main Section</title>
		<p><named-content content-type="term"><bold>Inhaltsverzeichnis</bold></named-content></p>
		<p>Following content.</p>
	</sec>
"""

SECTION_WITH_TOC_BY_ID = """
	<sec>
		<title>Main Section</title>
		<p><named-content id="_Toc_Inhaltsverzeichnis">Some heading text</named-content></p>
		<p>Following content.</p>
	</sec>
"""

SECTION_WITHOUT_TOC_HEADING = """
	<sec>
		<title>Main Section</title>
		<p><named-content content-type="term">Just a regular term</named-content></p>
		<p>Following content.</p>
	</sec>
"""
