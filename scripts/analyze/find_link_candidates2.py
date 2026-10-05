# ruff: noqa: E501
import argparse
import re
import sys
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).parent))

from files import find_xml_files_and_apply_function

TITLES = ["DGUV Vorschrift", "DGUV Regel", "DGUV Information", "DGUV Grundsatz"]

NUMBER_PATTERN = r"\d+(?:-\d+)?"

# The number must not be followed by more digits/hyphens, so "100-001" is one reference.
BOUNDARY = r"(?![\d-])"

NOTHING_PATTERNS = [re.compile(rf"{title} {NUMBER_PATTERN}{BOUNDARY}$") for title in TITLES]
SPACE_PATTERNS = [re.compile(rf"{title} {NUMBER_PATTERN}{BOUNDARY}(?=\s)") for title in TITLES]
DOT_PATTERNS = [re.compile(rf"{title} {NUMBER_PATTERN}{BOUNDARY}(?=\.)") for title in TITLES]
SLASH_PATTERNS = [re.compile(rf"{title} {NUMBER_PATTERN}{BOUNDARY}(?=/)") for title in TITLES]
COMMA_PATTERNS = [re.compile(rf"{title} {NUMBER_PATTERN}{BOUNDARY}(?=,)") for title in TITLES]
RPAREN_PATTERNS = [re.compile(rf"{title} {NUMBER_PATTERN}{BOUNDARY}(?=\))") for title in TITLES]
OTHER_PATTERNS = [re.compile(rf"{title} {NUMBER_PATTERN}{BOUNDARY}(?=[^\s.,)/])") for title in TITLES]

# Block-level elements from dguv_jats.xsd that own a piece of text in <body>/<back>.
# Anything not in this set (emphasis.class: bold/italic/sc/strike/underline, subsup.class:
# sub/sup, phrase-content.class: named-content/styled-content, xref, ext-link, math, ...)
# is treated as inline: its text is attributed to the nearest block ancestor.
BLOCK_LEVEL_TAGS = {
    # headings & labels
    "label", "title", "subtitle", "trans-title",
    # paragraphs & quotes
    "p", "disp-quote", "boxed-text", "abstract", "trans-abstract",
    # lists & definition lists
    "list", "list-item", "def-list", "def-item", "def", "def-head", "term", "term-head",
    # footnotes
    "fn", "fn-group",
    # figures & tables
    "fig", "fig-group", "caption", "table-wrap", "table-wrap-group", "table", "col", "colgroup",
    "thead", "tbody", "tfoot", "tr", "td", "th",
    # formulas & preformatted text
    "disp-formula", "disp-formula-group", "preformat", "code",
    # structural containers
    "sec", "sec-meta", "ack", "app", "app-group", "glossary", "notes",
    # references (back matter)
    "ref-list", "ref", "mixed-citation", "element-citation",
    # misc text holders
    "alt-text", "comment", "kwd",
}


def _localname(element: etree._Element) -> str:
    return etree.QName(element).localname if isinstance(element.tag, str) else str(element.tag)


def _find_patterns(
    text: str,
) -> tuple[list[str], list[str], list[str], list[str], list[str], list[str], list[str]]:
    return (
        [match.group(0) for pattern in NOTHING_PATTERNS for match in pattern.finditer(text)],
        [match.group(0) for pattern in SPACE_PATTERNS for match in pattern.finditer(text)],
        [match.group(0) for pattern in DOT_PATTERNS for match in pattern.finditer(text)],
        [match.group(0) for pattern in SLASH_PATTERNS for match in pattern.finditer(text)],
        [match.group(0) for pattern in COMMA_PATTERNS for match in pattern.finditer(text)],
        [match.group(0) for pattern in RPAREN_PATTERNS for match in pattern.finditer(text)],
        [match.group(0) for pattern in OTHER_PATTERNS for match in pattern.finditer(text)],
    )


class Scanner:
    def __init__(self) -> None:
        self.matching_documents = 0
        self.scanned_documents = 0
        self.total_matches = 0

        self.result = "# Link-Kandidaten\nSuche nach möglichen Artikel-IDs im body und back\n\n"
        self.result += "Suche was nach den Mustern kommt:\n\n"
        self.result += "- Schrägstrich\n"
        self.result += "- Komma\n"
        self.result += "- Punkt\n"
        self.result += "- Schließende Klammer\n"
        self.result += "- Sonstige\n"
        self.result += "- Kein Zeichen\n"
        self.result += "- Leerzeichen / Whitespace\n"
        self.result += "\n"

        self.nothing_matches = 0
        self.nothing_results = []
        self.space_matches = 0
        self.space_results = []
        self.dot_matches = 0
        self.dot_results = []
        self.slash_matches = 0
        self.slash_results = []
        self.comma_matches = 0
        self.comma_results = []
        self.rparen_matches = 0
        self.rparen_results = []
        self.other_matches = 0
        self.other_results = []

    def extract_candidates(
        self, data: bytes
    ) -> list[tuple[str, str, tuple[list[str], list[str], list[str], list[str], list[str], list[str], list[str]]]]:
        """Return (tag, element-text, matches-per-category) tuples for body/back of an article."""
        parser = etree.XMLParser(recover=True, resolve_entities=False)
        try:
            root = etree.fromstring(data, parser=parser)
        except etree.XMLSyntaxError as exc:
            print(f"[ERROR] Failed to parse XML document: {exc}", file=sys.stderr)
            return []
        if root is None:
            print("[ERROR] Failed to parse XML document: Root element is None", file=sys.stderr)
            return []

        elements = []
        body = root.find("body")
        if body is not None:
            elements.append(body)
        back = root.find("back")
        if back is not None:
            elements.append(back)

        # Assign every text node under body/back to its nearest block-level ancestor, exactly once.
        block_texts: dict[etree._Element, list[str]] = {}
        for container in elements:
            for subelement in container.iter(tag=etree.Element):
                owner = subelement
                while owner is not None and owner is not container and _localname(owner) not in BLOCK_LEVEL_TAGS:
                    owner = owner.getparent()
                if owner is None or owner is container:
                    continue
                if subelement.text:
                    block_texts.setdefault(owner, []).append(subelement.text)
                for child in subelement:
                    if child.tail:
                        block_texts.setdefault(owner, []).append(child.tail)

        candidates = []
        for element, texts in block_texts.items():
            text = " ".join(" ".join(texts).split())
            categories = _find_patterns(text)
            if not any(categories):
                continue
            candidates.append((_localname(element), text, categories))
        return candidates

    def scan_xml(self, data: bytes, path: str) -> None:
        """Scan an XML document in memory."""
        self.scanned_documents += 1
        document_matched = False
        for tag, text, (nothing, space, dot, slash, comma, rparen, other) in self.extract_candidates(data):
            for match in nothing:
                self.nothing_results.append((match, tag, path, text))
            for match in space:
                self.space_results.append((match, tag, path, text))
            for match in dot:
                self.dot_results.append((match, tag, path, text))
            for match in slash:
                self.slash_results.append((match, tag, path, text))
            for match in comma:
                self.comma_results.append((match, tag, path, text))
            for match in rparen:
                self.rparen_results.append((match, tag, path, text))
            for match in other:
                self.other_results.append((match, tag, path, text))
            if any((nothing, space, dot, slash, comma, rparen, other)):
                document_matched = True
        if document_matched:
            self.matching_documents += 1
        self.nothing_matches = len(self.nothing_results)
        self.space_matches = len(self.space_results)
        self.dot_matches = len(self.dot_results)
        self.slash_matches = len(self.slash_results)
        self.comma_matches = len(self.comma_results)
        self.rparen_matches = len(self.rparen_results)
        self.other_matches = len(self.other_results)
        self.total_matches = sum(
            (
                self.nothing_matches,
                self.space_matches,
                self.dot_matches,
                self.slash_matches,
                self.comma_matches,
                self.rparen_matches,
                self.other_matches,
            )
        )

    def safe_result(self, path: str):
        sections = [
            ("Schrägstrich", self.slash_matches, self.slash_results),
            ("Komma", self.comma_matches, self.comma_results),
            ("Punkt", self.dot_matches, self.dot_results),
            ("Schließende Klammer", self.rparen_matches, self.rparen_results),
            ("Sonstige", self.other_matches, self.other_results),
            ("Kein Zeichen", self.nothing_matches, self.nothing_results),
            ("Leerzeichen / Whitespace", self.space_matches, self.space_results),
        ]
        for title, count, results in sections:
            self.result += f"## {title} ({count} Treffer)\n\n"
            if not results:
                self.result += "Keine Treffer.\n\n"
                continue
            for match, tag, file_path, text in results:
                display_path = file_path.split("::", 1)[1].removeprefix("content\\") if "::" in file_path else file_path
                self.result += f"- **{match}** (\\<{tag}\\>, {display_path}): {text}\n"
            self.result += "\n"
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.result)
            print(f"Result successfully written to {path}", file=sys.stderr)
        except OSError as exc:
            print(f"[ERROR] Failed to write result to {path}: {exc}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=("Recursively search XML files and archives for DGUV title patterns in <article>/<body>.")
    )
    parser.add_argument("path", type=Path, help="File or directory to scan")
    parser.add_argument("--output", type=Path, default=Path("result.md"), help="File to write the results to")
    args = parser.parse_args()

    scanner = Scanner()

    try:
        find_xml_files_and_apply_function(args.path, scanner.scan_xml)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    print(f"\nMatching documents: {scanner.matching_documents}", file=sys.stderr)
    print(f"XML documents scanned: {scanner.scanned_documents}", file=sys.stderr)

    scanner.safe_result(str(args.output))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
