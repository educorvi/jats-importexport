import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from files import find_xml_files_and_apply_function

# Regex for webcode links
WEBCODE_PATTERN = r"p\d{6}"

LINK_PATTERN = re.compile(
    rf"""(?P<prefix>
            <a\b[^>]*?\bhref\s*=\s*(?P<quote>["'])
        )
        https://publikationen\.dguv\.de/
        DguvWebcode/index/query/
        (?P<webcode>{WEBCODE_PATTERN})
        /?
        (?P=quote)
    """,
    re.IGNORECASE | re.VERBOSE,
)

# pattern that also finds self-uri elements for testing
# LINK_PATTERN = re.compile(
#     rf"""(https://publikationen\.dguv\.de/
#         DguvWebcode/index/query/
#         (?P<webcode>{WEBCODE_PATTERN})
#     )""",
#     re.IGNORECASE | re.VERBOSE,
# )

# pattern to match all links
# LINK_PATTERN = re.compile(
#     r"""<(?P<tag>[A-Za-z][A-Za-z0-9:_-]*)\b[^>]*?\bhref\s*=\s*(?P<quote>["'])(?P<href>.*?)(?P=quote)[^>]*>""",
#     re.IGNORECASE | re.DOTALL,
# )


class Scanner:
    def __init__(self) -> None:
        self.matching_documents = 0
        self.scanned_documents = 0

    def count_links(self, data: bytes) -> int:
        """Count the number of matching links in the XML data."""
        text = data.decode("utf-8", errors="ignore")
        return len(LINK_PATTERN.findall(text))

    def extract_links(self, data: bytes) -> list[str]:
        """Extract all matching links from the XML data."""
        text = data.decode("utf-8", errors="ignore")
        return [f"{match.group('tag')} {match.group('href')}" for match in LINK_PATTERN.finditer(text)]

    def scan_xml(self, data: bytes, path: str) -> None:
        """Scan an XML document in memory."""
        self.scanned_documents += 1
        # links = self.extract_links(data)
        # if links:
        #     self.matching_documents += 1
        #     print(path, flush=True)
        #     print("\n".join(f"\t{link}" for link in links), flush=True)
        count = self.count_links(data)
        if count:
            self.matching_documents += 1
            print(f"{count:4d}  {path}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=("Recursively search XML files and archives for DGUV Webcode links."))
    parser.add_argument("path", type=Path, help="File or directory to scan")
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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
