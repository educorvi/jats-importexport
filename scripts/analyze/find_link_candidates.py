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

PATTERNS = [
    re.compile(rf"{title} {NUMBER_PATTERN}") for title in TITLES
]

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


def _find_patterns(text: str) -> list[str]:
    return [match.group(0) for pattern in PATTERNS for match in pattern.finditer(text)]


class Scanner:
    def __init__(self) -> None:
        self.matching_documents = 0
        self.scanned_documents = 0
        self.total_matches = 0
        self.result = "# Link-Kandidaten\nSuche nach möglichen Artikel-IDs im body und back\n\n"
        self.result += "Gesuchte Muster:\n\n"
        for pattern in PATTERNS:
            self.result += f"- {pattern.pattern}\n"
        self.result += "\n"

    def extract_candidates(self, data: bytes) -> list[tuple[str, str, str]]:
        """Return (pattern, tag, element-text) triples for the body of an article."""
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
            for pattern in _find_patterns(text):
                candidates.append((pattern, _localname(element), text))
        return candidates

    def scan_xml(self, data: bytes, path: str) -> None:
        """Scan an XML document in memory."""
        self.scanned_documents += 1
        candidates = self.extract_candidates(data)
        if not candidates:
            return
        self.matching_documents += 1
        self.total_matches += len(candidates)
        display_path = path.split("::", 1)[1].removeprefix("content\\") if "::" in path else path
        self.result += f"## {display_path}\n\n"
        for pattern, tag, text in candidates:
            # short = text if len(text) <= 300 else f"{text[:300]} …"
            self.result += f"- **{pattern}** (\\<{tag}\\>): {text}\n"
        self.result += "\n"

    def safe_result(self, path: str):
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
