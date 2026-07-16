#!/usr/bin/env python3
"""Convert one or more OCF (ZIP container) files to .zip files."""

from __future__ import annotations

import argparse
import glob
import shutil
import sys
import zipfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy OCF ZIP containers to files with a .zip extension."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="OCF file(s) or glob pattern(s), e.g. '*.ocf' or 'docs/**/*.ocf'",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Put all ZIP files in this directory (default: beside each input)",
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="Overwrite existing ZIP files"
    )
    return parser.parse_args()


def expand_inputs(values: list[str]) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    unmatched: list[str] = []

    for value in values:
        matches = [Path(match) for match in glob.glob(value, recursive=True)]
        matches = [path for path in matches if path.is_file()]
        if not matches:
            unmatched.append(value)
            continue
        files.extend(matches)

    # Keep the first occurrence while removing duplicates.
    return list(dict.fromkeys(files)), unmatched


def main() -> int:
    args = parse_args()
    inputs, unmatched = expand_inputs(args.inputs)
    failed = False

    for pattern in unmatched:
        print(f"error: no file matches {pattern!r}", file=sys.stderr)
        failed = True

    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    destinations: set[Path] = set()
    for source in inputs:
        if source.suffix.lower() != ".ocf":
            print(f"error: not an .ocf file: {source}", file=sys.stderr)
            failed = True
            continue
        if not zipfile.is_zipfile(source):
            print(f"error: not a valid ZIP container: {source}", file=sys.stderr)
            failed = True
            continue

        destination = (args.output_dir or source.parent) / f"{source.stem}.zip"
        destination_key = destination.resolve()
        if destination_key in destinations:
            print(f"error: multiple inputs map to {destination}", file=sys.stderr)
            failed = True
            continue
        destinations.add(destination_key)

        if destination.exists() and not args.force:
            print(f"error: output exists (use --force): {destination}", file=sys.stderr)
            failed = True
            continue

        shutil.copy2(source, destination)
        print(f"{source} -> {destination}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
