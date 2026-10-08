# ruff: noqa: E501
import argparse
import re
import sys
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).parent))

from files import find_xml_files_and_apply_function

DASHES = "-–—"  # Unicode: 002D, 2013, 2014

# IMPORTANT: the alternatives must be wrapped in a non-capturing group, otherwise the
# number/reject parts after the alternation only apply to the LAST branch ("Grundsatz").
TITLE_PATTERN = rf"(?:DGUV[{DASHES}\s](?:Vorschrift|Regel|Information|Grundsatz))"

NUMBER_PATTERN = rf"\d+(?:[{DASHES}]\d+)?"

# The number must not be followed by more digits/hyphens, so "100-001" is one reference.
# Note: the dash must come first in the class (or be escaped), otherwise it forms a range.
BOUNDARY_PATTERN = rf"(?![{DASHES}\d])"

REJECTED_PATTERN = r"(?!\s*[,/]\s*\d)(?!\s+(?:und|sowie|bzw\.|bzw|oder|and|or)\s+\d)"

PATTERN = re.compile(rf"{TITLE_PATTERN} {NUMBER_PATTERN}{BOUNDARY_PATTERN}{REJECTED_PATTERN}")

# Block-level elements from dguv_jats.xsd that own a piece of text in <body>/<back>.
# Anything not in this set (emphasis.class: bold/italic/sc/strike/underline, subsup.class:
# sub/sup, phrase-content.class: named-content/styled-content, xref, ext-link, math, ...)
# is treated as inline: its text is attributed to the nearest block ancestor.
BLOCK_LEVEL_TAGS = {
    # headings & labels
    "label",
    "title",
    "subtitle",
    "trans-title",
    # paragraphs & quotes
    "p",
    "disp-quote",
    "boxed-text",
    "abstract",
    "trans-abstract",
    # lists & definition lists
    "list",
    "list-item",
    "def-list",
    "def-item",
    "def",
    "def-head",
    "term",
    "term-head",
    # footnotes
    "fn",
    "fn-group",
    # figures & tables
    "fig",
    "fig-group",
    "caption",
    "table-wrap",
    "table-wrap-group",
    "table",
    "col",
    "colgroup",
    "thead",
    "tbody",
    "tfoot",
    "tr",
    "td",
    "th",
    # formulas & preformatted text
    "disp-formula",
    "disp-formula-group",
    "preformat",
    "code",
    # structural containers
    "sec",
    "sec-meta",
    "ack",
    "app",
    "app-group",
    "glossary",
    "notes",
    # references (back matter)
    "ref-list",
    "ref",
    "mixed-citation",
    "element-citation",
    # misc text holders
    "alt-text",
    "comment",
    "kwd",
}


def _localname(element: etree._Element) -> str:
    return etree.QName(element).localname if isinstance(element.tag, str) else str(element.tag)


def _count_matches(text: str) -> list[str]:
    return [match.group(0) for match in PATTERN.finditer(text)]


def _display_path(file_path: str) -> str:
    return file_path.split("::", 1)[1].removeprefix("content\\") if "::" in file_path else file_path


class Scanner:
    def __init__(self) -> None:
        self.scanned_documents = 0
        self.matching_documents_block = 0
        self.matching_documents_flat = 0
        # tag -> number of matches, once per attribution mode
        self.tags_block: dict[str, int] = {}
        self.tags_flat: dict[str, int] = {}
        # per attribution mode: list of (tag, match, display_path, text)
        self.results_block: list[tuple[str, str, str, str]] = []
        self.results_flat: list[tuple[str, str, str, str]] = []

    def _parse(self, data: bytes) -> etree._Element | None:
        parser = etree.XMLParser(recover=True, resolve_entities=False)
        try:
            root = etree.fromstring(data, parser=parser)
        except etree.XMLSyntaxError as exc:
            print(f"[ERROR] Failed to parse XML document: {exc}", file=sys.stderr)
            return None
        if root is None:
            print("[ERROR] Failed to parse XML document: Root element is None", file=sys.stderr)
            return None
        return root

    def _collect_element_texts(self, root: etree._Element, block_level: bool) -> dict[etree._Element, list[str]]:
        """Assign every text node under body/back to its owner element, exactly once.

        block_level=True: owner is the nearest block-level ancestor (BLOCK_LEVEL_TAGS),
        so inline elements like <italic> contribute their text to the surrounding block.
        block_level=False: owner is the element that directly contains the text node,
        so inline elements like <italic> become owners themselves.
        """
        containers = []
        for name in ("body", "back"):
            element = root.find(name)
            if element is not None:
                containers.append(element)

        element_texts: dict[etree._Element, list[str]] = {}
        for container in containers:
            for subelement in container.iter(tag=etree.Element):
                if block_level:
                    owner = subelement
                    while owner is not None and owner is not container and _localname(owner) not in BLOCK_LEVEL_TAGS:
                        owner = owner.getparent()
                    if owner is None or owner is container:
                        continue
                else:
                    owner = subelement
                if subelement.text:
                    element_texts.setdefault(owner, []).append(subelement.text)
                for child in subelement:
                    if child.tail:
                        element_texts.setdefault(owner, []).append(child.tail)
        return element_texts

    def scan_xml(self, data: bytes, path: str) -> None:
        """Scan an XML document in memory with both attribution modes."""
        self.scanned_documents += 1
        root = self._parse(data)
        if root is None:
            return

        display = _display_path(path)
        matched = {True: False, False: False}
        modes = ((True, self.tags_block, self.results_block), (False, self.tags_flat, self.results_flat))
        for block_level, tags, results in modes:
            for element, texts in self._collect_element_texts(root, block_level).items():
                text = " ".join(" ".join(texts).split())
                matches = _count_matches(text)
                if not matches:
                    continue
                tag = _localname(element)
                tags[tag] = tags.get(tag, 0) + len(matches)
                results.extend((tag, match, display, text) for match in matches)
                matched[block_level] = True

        if matched[True]:
            self.matching_documents_block += 1
        if matched[False]:
            self.matching_documents_flat += 1

    def write_results(self, path_block: str, path_flat: str) -> None:
        variants = ((path_block, self.results_block, self.tags_block), (path_flat, self.results_flat, self.tags_flat))
        for path, results, tags in variants:
            lines = [f"# Link-Kandidaten nach Tag ({sum(tags.values())} Treffer in {len(tags)} Tags)\n"]
            for tag in sorted({tag for tag, _, _, _ in results}):
                tag_results = [row for row in results if row[0] == tag]
                lines.append(f"\n## <{tag}> ({len(tag_results)} Treffer)\n")
                for _, match, display, text in tag_results:
                    lines.append(f"- **{match}** ({display}): {text}")
            lines.append("")
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
                print(f"Result successfully written to {path}", file=sys.stderr)
            except OSError as exc:
                print(f"[ERROR] Failed to write result to {path}: {exc}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=("Compare per-tag match counts with and without BLOCK_LEVEL_TAGS attribution.")
    )
    parser.add_argument("path", type=Path, help="File or directory to scan")
    parser.add_argument(
        "--output-block", type=Path, default=Path("result_block.md"), help="File to write the block-level results to"
    )
    parser.add_argument(
        "--output-flat", type=Path, default=Path("result_flat.md"), help="File to write the no-block-level results to"
    )
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

    all_tags = sorted(set(scanner.tags_block) | set(scanner.tags_flat))
    print(f"XML documents scanned: {scanner.scanned_documents}")
    print(
        f"Matching documents: block-level={scanner.matching_documents_block}, no-block-level={scanner.matching_documents_flat}"
    )
    print(
        f"Total matches: block-level={sum(scanner.tags_block.values())}, no-block-level={sum(scanner.tags_flat.values())}"
    )
    print(f"{'tag':<20} {'block-level':>12} {'no-block-level':>15}")
    for tag in all_tags:
        print(f"{tag:<20} {scanner.tags_block.get(tag, 0):>12} {scanner.tags_flat.get(tag, 0):>15}")

    scanner.write_results(str(args.output_block), str(args.output_flat))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
