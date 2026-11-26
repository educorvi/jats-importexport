"""Report where Section.py detects Durchführungsanweisung, Vorbemerkungen and table-of-contents headings.

The XPaths and guards mirror packages/jats-classes/src/jats_classes/section/Section.py and are applied to
every <sec> that Section.from_xml_element processes (body-level <sec> and nested <sec> chains).
"""

import argparse
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).parent))

from files import find_xml_files_and_apply_function

DA_XPATH = './/italic[contains(.,"Durchführungsanweisung")]'
DA_TEXTS = ("Durchführungsanweisung", "Durchführungsanweisungen")
TOC_HEADINGS = (
    "Inhaltsverzeichnis",
    "Inhalt",
    "Contents",
    "Table of contents",
    "Table of content",
    "Table of Contents",
    "Table of Content",
)
TOC_ID = "_Toc_Inhaltsverzeichnis"
TEXT_LIMIT = 80

CATEGORIES = (
    ("Durchführungsanweisung", "Durchführungsanweisung"),
    ("Vorbemerkungen", "Vorbemerkungen"),
    ("Inhaltsverzeichnis", "Inhaltsverzeichnis / TOC"),
    ("DGUV TOC PI", "<?dguv toc?> processing instruction"),
)


@dataclass(frozen=True)
class Finding:
    category: str
    variant: str
    document: str
    line: int
    matched_text: str
    section_title: str
    outcome: str


def _display_path(file_path: str) -> str:
    if "::" not in file_path:
        return file_path
    archive, member = file_path.split("::", 1)
    member = member.removeprefix("content/").removeprefix("content\\")
    return f"{archive}::{member}"


def _text(element: etree._Element, limit: int = TEXT_LIMIT) -> str:
    text = " ".join("".join(element.itertext()).split())
    return text if len(text) <= limit else f"{text[: limit - 1]}…"


def _iter_sections(section: etree._Element) -> Iterator[etree._Element]:
    yield section
    for child in section:
        if child.tag == "sec":
            yield from _iter_sections(child)


def _first_match(section: etree._Element, xpath: str) -> etree._Element | None:
    matches = section.xpath(xpath)
    return matches[0] if matches else None


def _heading_xpath(heading: str) -> str:
    return f'.//named-content[text()="{heading}" or .//bold[text()="Inhaltsverzeichnis"]]'


HEADING_QUERIES: tuple[tuple[str, str, str, str], ...] = (
    ("Vorbemerkungen", "Vorbemerkungen", _heading_xpath("Vorbemerkungen"), "preamble"),
    ("Vorbemerkungen", "Vorbemerkung", _heading_xpath("Vorbemerkung"), "preamble"),
    *(("Inhaltsverzeichnis", heading, _heading_xpath(heading), "toc") for heading in TOC_HEADINGS),
    ("Inhaltsverzeichnis", f"id={TOC_ID}", f'.//named-content[@id="{TOC_ID}"]', "toc"),
)


def _durchfuehrungsanweisung_outcome(section: etree._Element, italic: etree._Element) -> str | None:
    """Return the split outcome for an italic in this section, or None if a nested <sec> owns it."""
    node = italic
    while True:
        parent = node.getparent()
        if parent is None or parent is section:
            break
        node = parent
    if node.getparent() is not section or node.tag == "sec":
        return None
    siblings = list(section)
    idx = siblings.index(node)
    if any(s.tag not in ("label", "title") for s in siblings[:idx]):
        return "split: following content moves into a new highlight-info <sec>"
    return "no split: nothing precedes the heading"


def _detect(section: etree._Element, document: str) -> Iterator[Finding]:
    title = section.find("title")
    section_title = _text(title) if title is not None else "(no title)"

    italic = _first_match(section, DA_XPATH)
    if italic is not None and (italic.text or "").strip() in DA_TEXTS:
        outcome = _durchfuehrungsanweisung_outcome(section, italic)
        if outcome is not None:
            yield Finding(
                "Durchführungsanweisung",
                (italic.text or "").strip(),
                document,
                italic.sourceline or 0,
                _text(italic),
                section_title,
                outcome,
            )

    for category, variant, xpath, sec_type in HEADING_QUERIES:
        match = _first_match(section, xpath)
        if match is not None:
            yield Finding(
                category,
                variant,
                document,
                match.sourceline or 0,
                _text(match),
                section_title,
                f'sets sec-type="{sec_type}" on this section',
            )


def _detect_dguv_toc(root: etree._Element, document: str) -> Iterator[Finding]:
    for pi in root.iter(etree.PI):
        if pi.target != "dguv" or (pi.text or "").strip() != "toc":
            continue
        parent = pi.getparent()
        parent_tag = parent.tag if parent is not None else "(root)"
        enclosing_sec = next(pi.iterancestors("sec"), None)
        enclosing_title = enclosing_sec.find("title") if enclosing_sec is not None else None
        section_title = _text(enclosing_title) if enclosing_title is not None else "(no enclosing section)"
        yield Finding(
            "DGUV TOC PI",
            "`<?dguv toc?>`",
            document,
            pi.sourceline or 0,
            "`<?dguv toc?>`",
            section_title,
            f"inside <{parent_tag}>",
        )


class Scanner:
    def __init__(self) -> None:
        self.scanned_documents = 0
        self.parse_failures = 0
        self.findings: list[Finding] = []

    def scan_xml(self, data: bytes, path: str) -> None:
        self.scanned_documents += 1
        display = _display_path(path)
        try:
            root = etree.fromstring(data, parser=etree.XMLParser(remove_pis=False, remove_comments=False))
        except etree.XMLSyntaxError as exc:
            self.parse_failures += 1
            print(f"[ERROR] Failed to parse {path}: {exc}", file=sys.stderr)
            return
        self.findings.extend(_detect_dguv_toc(root, display))
        body = root.find("body")
        if body is None:
            return
        for top_level_section in body.findall("sec"):
            for section in _iter_sections(top_level_section):
                self.findings.extend(_detect(section, display))

    def count(self, category: str) -> tuple[int, int]:
        matching = [f for f in self.findings if f.category == category]
        return len(matching), len({f.document for f in matching})

    def write_report(self, path: Path) -> None:
        lines = [
            "# Section detection report",
            "",
            "Occurrences detected exactly as in `Section.py` "
            "(`_split_on_durchfuehrungsanweisung`, `_split_on_vorbemerkungen`, `_split_on_inhaltsverzeichnis`).",
            "",
            "## Summary",
            "",
            f"- XML documents scanned: {self.scanned_documents}",
            f"- XML parse failures: {self.parse_failures}",
            "",
            "| Category | Occurrences | Documents |",
            "| --- | ---: | ---: |",
        ]
        for category, label in CATEGORIES:
            occurrences, documents = self.count(category)
            lines.append(f"| {label} | {occurrences} | {documents} |")
        lines.append("")

        for category, label in CATEGORIES:
            findings = sorted(
                (f for f in self.findings if f.category == category),
                key=lambda f: (f.document, f.line),
            )
            lines.extend((f"## {label}", ""))
            if not findings:
                lines.extend(("None found.", ""))
                continue
            lines.extend(
                (
                    "| Document | Line | Variant | Matched text | Section | Outcome |",
                    "| --- | ---: | --- | --- | --- | --- |",
                )
            )
            for f in findings:
                cells = (f.document, str(f.line), f.variant, f.matched_text, f.section_title, f.outcome)
                lines.append("| " + " | ".join(_md_cell(c) for c in cells) + " |")
            lines.append("")

        lines.extend(
            (
                "## Notes",
                "",
                "- Vorbemerkungen and TOC matches set `sec-type` on the section being processed, even when the "
                "matched element sits in a nested `<sec>`.",
                "- The heading queries also match any `<named-content>` containing `<bold>Inhaltsverzeichnis</bold>`, "
                "so such elements appear under Vorbemerkungen as well.",
                "",
            )
        )

        try:
            path.write_text("\n".join(lines), encoding="utf-8")
            print(f"Result successfully written to {path}", file=sys.stderr)
        except OSError as exc:
            print(f"[ERROR] Failed to write result to {path}: {exc}", file=sys.stderr)


def _md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan JATS XML/OCF files for Section.py split/TOC detections.")
    parser.add_argument("path", type=Path, help="File or directory to scan")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("section_detection_report.md"),
        help="Markdown report path",
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

    scanner.write_report(args.output)
    for category, label in CATEGORIES:
        occurrences, documents = scanner.count(category)
        print(f"{label}: {occurrences} occurrences in {documents} documents")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
