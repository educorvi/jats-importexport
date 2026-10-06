# ruff: noqa: E501
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

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


class Scanner:
    def __init__(self) -> None:
        self.matches = 0
        self.no_matches = 0
        self.matches_results = []
        self.no_matches_results = []
        self.result = "# Link-Kandidaten\nSuche nach möglichen Artikel-IDs im body und back\n\n"

    def scan_json(self, path: Path) -> None:
        with open(path, encoding="utf-8") as f:
            data = f.read()
            data = json.loads(data)
            for text in data:
                matches = PATTERN.findall(text)
                if not matches:
                    self.no_matches += 1
                    self.no_matches_results.append(text)
                else:
                    self.matches += 1
                    self.matches_results.append((text, matches))

    def safe_result(self, path: str):
        self.result += f"Gesamt ({self.matches} Treffer, {self.no_matches} abgelehnte Texte)\n\n"
        self.result += "## Treffer\n\n"
        for text, matches in self.matches_results:
            self.result += f"- **{' || '.join(matches)}**: {text}\n"
        self.result += "\n"

        self.result += "## Abgelehnte Texte\n\n"
        for text in self.no_matches_results:
            self.result += f"- {text}\n"
        self.result += "\n"
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.result)
            print(f"Result successfully written to {path}", file=sys.stderr)
        except OSError as exc:
            print(f"[ERROR] Failed to write result to {path}: {exc}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=("Search strings from a json for the pattern."))
    parser.add_argument("path", type=Path, help="JSON file containing a list of strings")
    parser.add_argument("--output", type=Path, default=Path("result.md"), help="File to write the results to")
    args = parser.parse_args()

    scanner = Scanner()

    try:
        scanner.scan_json(args.path)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    scanner.safe_result(str(args.output))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
