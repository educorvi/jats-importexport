import argparse
import sys
from collections import defaultdict
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).parent))

from files import find_xml_files_and_apply_function


def _localname(element: etree._Element) -> str:
    return etree.QName(element).localname if isinstance(element.tag, str) else str(element.tag)


def _has_mixed_content(element: etree._Element) -> bool:
    children = [child for child in element if isinstance(child.tag, str)]
    if not children:
        return False
    if element.text and element.text.strip():
        return True
    return any(child.tail and child.tail.strip() for child in element)


def _display_path(file_path: str) -> str:
    if "::" not in file_path:
        return file_path
    archive, member = file_path.split("::", 1)
    member = member.removeprefix("content/").removeprefix("content\\")
    return f"{archive}::{member}"


class Scanner:
    def __init__(self, element_name: str) -> None:
        self.element_name = element_name
        self.scanned_documents = 0
        self.parse_failures = 0
        self.occurrences: dict[str, list[tuple[str, int]]] = defaultdict(list)
        self.mixed_content: dict[str, list[tuple[str, int]]] = defaultdict(list)

    def scan_xml(self, data: bytes, path: str) -> None:
        self.scanned_documents += 1
        parser = etree.XMLParser(recover=True, resolve_entities=False)
        try:
            root = etree.fromstring(data, parser=parser)
        except etree.XMLSyntaxError as exc:
            self.parse_failures += 1
            print(f"[ERROR] Failed to parse {path}: {exc}", file=sys.stderr)
            return
        if root is None:
            self.parse_failures += 1
            print(f"[ERROR] Failed to parse {path}: no root element", file=sys.stderr)
            return

        display = _display_path(path)
        for element in root.iter():
            if _localname(element) != self.element_name:
                continue
            element_name = _localname(element)
            child_names = sorted({_localname(child) for child in element if isinstance(child.tag, str)})
            if _has_mixed_content(element):
                self.mixed_content[", ".join(child_names)].append((display, element.sourceline or 0))
            if not child_names:
                child_names = ["(no children)"]
            for child_name in child_names:
                child_path = f"{element_name}/{child_name}"
                self.occurrences[child_path].append((display, element.sourceline or 0))

    def write_report(self, path: Path) -> None:
        documents = {document for occurrences in self.occurrences.values() for document, _ in occurrences}
        total_occurrences = sum(len(occurrences) for occurrences in self.occurrences.values())
        total_mixed = sum(len(occurrences) for occurrences in self.mixed_content.values())
        lines = [
            f"# `<{self.element_name}>` element scan",
            "",
            "## Summary",
            "",
            f"- XML documents scanned: {self.scanned_documents}",
            f"- Files containing `<{self.element_name}>`: {len(documents)}",
            f"- Total `<{self.element_name}>` occurrences: {total_occurrences}",
            f"- XML parse failures: {self.parse_failures}",
            f"- `<{self.element_name}>` elements with children and direct text: {total_mixed}",
            "",
            "### Occurrences by element/child",
            "",
            "| Element/child | Occurrences |",
            "| --- | ---: |",
        ]
        if self.occurrences:
            lines.extend(
                f"| `{child_path}` | {len(occurrences)} |"
                for child_path, occurrences in sorted(self.occurrences.items())
            )
        else:
            lines.append("| None | 0 |")
        lines.extend(
            (
                "",
                f"## `<{self.element_name}>` occurrences by element/child",
                "",
            )
        )
        if self.occurrences:
            for child_path, occurrences in sorted(self.occurrences.items()):
                lines.extend((f"### `{child_path}`", ""))
                for document, line_number in sorted(occurrences):
                    lines.append(f"- **{document}**, line {line_number}")
                lines.append("")
        else:
            lines.append("- None found.")

        lines.extend(("", f"## `<{self.element_name}>` elements with children and direct text", ""))
        if self.mixed_content:
            for children_key, occurrences in sorted(self.mixed_content.items()):
                lines.extend((f"### Children: `{children_key}`", ""))
                for document, line_number in sorted(occurrences):
                    lines.append(f"- **{document}**, line {line_number}")
                lines.append("")
        else:
            lines.append("- None found.")
        lines.append("")

        try:
            path.write_text("\n".join(lines), encoding="utf-8")
            print(f"Result successfully written to {path}", file=sys.stderr)
        except OSError as exc:
            print(f"[ERROR] Failed to write result to {path}: {exc}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan JATS XML/OCF files for the child elements of a named element.")
    parser.add_argument("path", type=Path, help="File or directory to scan")
    parser.add_argument("element", help="Element name to find, for example 'section'")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("element_report.md"),
        help="Markdown report path",
    )
    args = parser.parse_args()

    scanner = Scanner(args.element)
    try:
        find_xml_files_and_apply_function(args.path, scanner.scan_xml)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    scanner.write_report(args.output)
    found_documents = {file for entries in scanner.occurrences.values() for file, _ in entries}
    print(f"XML documents scanned: {scanner.scanned_documents}")
    print(f"Files containing <{args.element}>: {len(found_documents)}")
    print(f"Element occurrences: {sum(len(entries) for entries in scanner.occurrences.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
