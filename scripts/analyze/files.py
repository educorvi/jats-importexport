import io
import sys
import zipfile
from collections.abc import Callable
from pathlib import Path


def _is_xml(path: Path) -> bool:
    return path.suffix.lower() == ".xml"


def _is_archive(path: Path) -> bool:
    return path.suffix.lower() in [".zip", ".ocf"]


def _handle_xml_file(path: Path, print_path: str, func: Callable[[bytes, str], None]):
    try:
        with path.open("rb") as f:
            func(f.read(), print_path)
    except OSError as exc:
        print(f"[WARNING] could not read {path}: {exc}", file=sys.stderr)


def _handle_dir(path: Path, print_path: str, func: Callable[[bytes, str], None]):
    for child in sorted(path.iterdir(), key=lambda p: p.name):
        if child.is_file():
            if _is_xml(child):
                _handle_xml_file(child, f"{print_path}/{child.name}", func)
            elif _is_archive(child):
                _handle_archive(child, f"{print_path}/{child.name}", func)
        if child.is_dir():
            _handle_dir(child, f"{print_path}/{child.name}", func)


def _process_archive_bytes(data: bytes, print_path: str, func: Callable[[bytes, str], None]):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for member in sorted(archive.infolist(), key=lambda m: m.filename):
            if member.is_dir():
                continue
            member_path = Path(member.filename)
            member_print_path = f"{print_path}::{member.filename}"
            if not _is_xml(member_path) and not _is_archive(member_path):
                continue
            with archive.open(member) as f:
                member_data = f.read()
            if _is_archive(member_path):
                _process_archive_bytes(member_data, member_print_path, func)
            else:
                func(member_data, member_print_path)


def _handle_archive(path: Path, print_path: str, func: Callable[[bytes, str], None]):
    try:
        with path.open("rb") as f:
            _process_archive_bytes(f.read(), print_path, func)
    except (zipfile.BadZipFile, OSError) as exc:
        print(f"[WARNING] could not read archive {path}: {exc}", file=sys.stderr)


def find_xml_files_and_apply_function(path: Path, func: Callable[[bytes, str], None]):
    if not path.exists():
        raise ValueError(f"Path '{path}' does not exist.")

    if not path.is_file() and not path.is_dir():
        raise ValueError(f"Path '{path}' is neither a file nor a directory.")

    if path.is_file():
        if not _is_xml(path) and not _is_archive(path):
            raise ValueError(
                f"Unsupported file extension '{path.suffix}' for file '{path.name}'. Must be .xml, .zip, or .ocf"
            )
        if _is_archive(path):
            _handle_archive(path, str(path), func)
        if _is_xml(path):
            _handle_xml_file(path, str(path), func)

    if path.is_dir():
        _handle_dir(path, str(path), func)
