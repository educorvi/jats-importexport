# ruff: noqa: E501
import argparse
import sys
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).parent))

from files import find_xml_files_and_apply_function


class Scanner:
    def __init__(self) -> None:
        self.matching_documents = 0
        self.scanned_documents = 0
        self.result = "# Keywords\nSuche nach Elementen mit specific-use=\"keyword\"\n\n"

    def extract_keywords(self, data: bytes) -> list[tuple[str, str]]:
        parser = etree.XMLParser(recover=True, resolve_entities=False)
        try:
            root = etree.fromstring(data, parser=parser)
        except etree.XMLSyntaxError as exc:
            print(f"[ERROR] Failed to parse XML document: {exc}", file=sys.stderr)
            return []
        if root is None:
            print("[ERROR] Failed to parse XML document: Root element is None", file=sys.stderr)
            return []
        keywords = []
        for element in root.iter(tag=etree.Element):
            if element.get("specific-use") != "keyword":
                continue
            content = "".join(str(text) for text in element.itertext()).strip()
            tag = etree.QName(element).localname if isinstance(element.tag, str) else str(element.tag)
            keywords.append((content, tag))
        return keywords

    def scan_xml(self, data: bytes, path: str) -> None:
        """Scan an XML document in memory."""
        self.scanned_documents += 1
        display_path = path.split("::", 1)[1].removeprefix("content\\") if "::" in path else path
        self.result += f"## {display_path}\n"
        keywords = self.extract_keywords(data)
        if keywords:
            self.matching_documents += 1
            num_empty = sum(1 for content, _ in keywords if not content)
            if num_empty > 0:
                self.result += f"{num_empty}/{len(keywords)} Keywords ohne Inhalt.\n\n"
            num_named_content = sum(1 for _, tag in keywords if tag == "named-content")
            self.result += f"Gefundene Keywords (davon im Element \\<named-content\\>: {num_named_content}/{len(keywords)}):\n"
            for content, tag in keywords:
                if not content:
                    continue
                if tag != "named-content":
                    self.result += f"- {content} (\\<{tag}\\>)\n"
                else:
                    self.result += f"- {content}\n"
        else:
            self.result += "Keine Keywords gefunden.\n"

    def safe_result(self, path: str):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.result)
            print(f"Result successfully written to {path}", file=sys.stderr)
        except OSError as exc:
            print(f"[ERROR] Failed to write result to {path}: {exc}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=("Recursively search XML files and archives for elements with specific-use=\"keyword\".")
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
