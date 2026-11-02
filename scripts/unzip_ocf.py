#!/usr/bin/env python3
"""Extract OCF archives in a folder and remove each archive after extraction."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract .ocf files into same-named folders, then delete the archives."
    )
    parser.add_argument("folder", type=Path, help="Folder containing .ocf files")
    return parser.parse_args()


def _validated_members(
    archive: zipfile.ZipFile,
) -> list[tuple[zipfile.ZipInfo, PurePosixPath, bool]]:
    members = []
    for member in archive.infolist():
        normalized_name = member.filename.replace("\\", "/")
        posix_path = PurePosixPath(normalized_name)
        windows_path = PureWindowsPath(member.filename)
        if (
            posix_path.is_absolute()
            or windows_path.is_absolute()
            or windows_path.drive
            or ".." in posix_path.parts
            or not posix_path.parts
        ):
            raise ValueError(f"unsafe archive member path: {member.filename!r}")
        members.append((member, posix_path, normalized_name.endswith("/")))
    return members


def _extract_members(
    archive: zipfile.ZipFile,
    staging: Path,
    members: list[tuple[zipfile.ZipInfo, PurePosixPath, bool]],
) -> None:
    for member, relative_path, is_directory in members:
        destination = staging.joinpath(*relative_path.parts)
        if is_directory:
            destination.mkdir(parents=True, exist_ok=True)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        with archive.open(member) as source, destination.open("wb") as target:
            shutil.copyfileobj(source, target)


def _extract_and_remove(source: Path) -> bool:
    destination = source.with_suffix("")
    if destination.exists():
        print(f"error: output folder already exists: {destination}", file=sys.stderr)
        return False

    try:
        with zipfile.ZipFile(source) as archive:
            members = _validated_members(archive)
            with tempfile.TemporaryDirectory(prefix=f".{destination.name}.", dir=source.parent) as temp:
                staging = Path(temp)
                _extract_members(archive, staging, members)
                extracted_roots = list(staging.iterdir())
                extracted_root = (
                    extracted_roots[0] if len(extracted_roots) == 1 and extracted_roots[0].is_dir() else staging
                )
                extracted_root.rename(destination)
        source.unlink()
    except (OSError, zipfile.BadZipFile, ValueError) as exc:
        print(f"error: could not extract {source}: {exc}", file=sys.stderr)
        return False

    print(f"{source} -> {destination} (archive removed)")
    return True


def main() -> int:
    args = parse_args()
    if not args.folder.exists():
        print(f"error: folder does not exist: {args.folder}", file=sys.stderr)
        return 2
    if not args.folder.is_dir():
        print(f"error: not a folder: {args.folder}", file=sys.stderr)
        return 2

    archives = sorted(
        (path for path in args.folder.iterdir() if path.is_file() and path.suffix.lower() == ".ocf"),
        key=lambda path: path.name,
    )
    if not archives:
        print(f"No .ocf files found in {args.folder}")
        return 0

    failed = False
    for archive in archives:
        if not _extract_and_remove(archive):
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
