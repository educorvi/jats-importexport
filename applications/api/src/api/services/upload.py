from pathlib import Path
import shutil
import stat
import tempfile
from typing import Any, BinaryIO
from urllib.parse import unquote, urlparse
import zipfile

from fastapi import File, HTTPException, UploadFile
from lxml import etree

from jats_classes import JATSDocument
from jats_storage_adapters.interface import AvailableStorageAdapters, StorageAdapter

from ..config import StorageConfig
from ..models import UploadFileResponse


XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"
MAX_ZIP_FILE_COUNT = StorageConfig.MAX_ZIP_FILE_COUNT
MAX_ZIP_UNCOMPRESSED_SIZE = StorageConfig.MAX_ZIP_UNCOMPRESSED_SIZE
CONTAINER = StorageConfig.CONTAINER
STORAGE_ADAPTER = StorageConfig.STORAGE_ADAPTER


async def upload_xml(uploaded_file: UploadFile = File(...)):
    adapter_instance = _get_adapter_instance()

    try:
        # Check file size
        uploaded_file.file.seek(0, 2)
        file_size = uploaded_file.file.tell()
        if file_size > MAX_ZIP_UNCOMPRESSED_SIZE:
            raise HTTPException(status_code=413, detail="Uploaded file is too large.")
        uploaded_file.file.seek(0)

        parser = etree.XMLParser(resolve_entities=False, no_network=True)
        xml_tree = etree.parse(uploaded_file.file, parser=parser)

        document = _create_JATSDocument_from_xml_tree(xml_tree)

        url = _save_jats_document(adapter_instance, document)

        return UploadFileResponse(url=url)

    except HTTPException:
        raise
    except etree.XMLSyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Uploaded XML is malformed: {e}")
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected error while processing the upload.")
    finally:
        await uploaded_file.close()


async def upload_zip(uploaded_file: UploadFile = File(...)):
    adapter_instance = _get_adapter_instance()

    try:
        # Check if file is a ZIP
        uploaded_file.file.seek(0)
        if not zipfile.is_zipfile(uploaded_file.file):
            raise HTTPException(status_code=415, detail="Uploaded file must be a ZIP archive.")
        uploaded_file.file.seek(0)

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir_path = Path(tmp_dir)

            _validate_and_extract_zip(uploaded_file.file, tmp_dir_path)

            xml_file = _find_xml_file(tmp_dir_path)

            parser = etree.XMLParser(resolve_entities=False, no_network=True)
            xml_tree = etree.parse(str(xml_file), parser=parser)

            _create_JATSDocument_from_xml_tree(xml_tree)

            _upload_files_and_update_references(xml_tree, xml_file, tmp_dir_path, adapter_instance=adapter_instance)

            modified_document = _create_JATSDocument_from_xml_tree(xml_tree)

            url = _save_jats_document(adapter_instance, modified_document)

            return UploadFileResponse(url=url)

    except HTTPException:
        raise
    except etree.XMLSyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Uploaded XML is malformed: {e}")
    except OSError as e:
        raise HTTPException(status_code=400, detail=f"Could not process uploaded ZIP content: {e}")
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected error while processing the upload.")
    finally:
        await uploaded_file.close()


# General helper functions for file processing

def _get_adapter_instance() -> StorageAdapter:
    try:
        return AvailableStorageAdapters.create_instance_by_name(STORAGE_ADAPTER)
    except ValueError:
        raise HTTPException(status_code=500, detail="Could not connect to the storage adapter.")


def _create_JATSDocument_from_xml_tree(xml_tree: etree._ElementTree | Any) -> JATSDocument:
    xml_content = etree.tostring(xml_tree.getroot(), encoding="unicode")
    try:
        return JATSDocument.from_xml(xml_content, xsd_path=None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JATS XML: {e}")

def _save_jats_document(adapter_instance: StorageAdapter, document: JATSDocument) -> str:
    try:
        return adapter_instance.save_jats_document(document, CONTAINER)
    except Exception:
        raise HTTPException(status_code=500, detail="Could not save the JATS document to the storage adapter.")


# Helper functions for ZIP processing and XML reference handling

def _is_path_within(parent: Path, child: Path) -> bool:
    """Check if the child path is within the parent directory."""
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _validate_and_extract_zip(zip_file: BinaryIO, target_directory: Path) -> None:
    """Perform security and size validations on the ZIP file and extract it to the target directory if valid.
    Validations include:
    - Total file count does not exceed MAX_ZIP_FILE_COUNT.
    - Total uncompressed size does not exceed MAX_ZIP_UNCOMPRESSED_SIZE.
    - No member has an absolute path or path traversal components.
    - No symbolic links are present in the archive.
    - Extraction is performed with checks to prevent path traversal vulnerabilities.
    """
    with zipfile.ZipFile(zip_file) as archive:
        target_root = target_directory.resolve()

        members = archive.infolist()
        if not members:
            raise HTTPException(status_code=400, detail="Uploaded ZIP archive is empty.")

        if len(members) > MAX_ZIP_FILE_COUNT:
            raise HTTPException(status_code=413, detail="ZIP archive contains too many files.")

        if sum(member.file_size for member in members) > MAX_ZIP_UNCOMPRESSED_SIZE:
            raise HTTPException(status_code=413, detail="ZIP archive is too large after extraction.")

        for member in members:
            if not member.filename:
                continue

            member_path = Path(member.filename)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise HTTPException(status_code=400, detail="ZIP archive contains invalid file paths.")

            # Reject symlinks to avoid reading unintended files after extraction.
            mode = member.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise HTTPException(status_code=400, detail="ZIP archive must not contain symbolic links.")

            if not member.filename:
                continue

            relative_path = Path(member.filename)
            target_path = (target_root / relative_path).resolve()
            if not _is_path_within(target_root, target_path):
                raise HTTPException(status_code=400, detail="ZIP archive contains invalid file paths that escape the target directory.")

            if member.is_dir():
                target_path.mkdir(parents=True, exist_ok=True)
                continue

            with archive.open(member) as source, target_path.open("wb") as destination:
                shutil.copyfileobj(source, destination)

    return None


def _find_xml_file(extraction_root: Path) -> Path:
    """Search for a single XML file within the given directory and its subdirectories.
    Returns the path to the XML file if exactly one is found, or raises an HTTPException if none or multiple are found.
    """
    top_level_entries = [
        entry for entry in extraction_root.iterdir()
    ]
    if len(top_level_entries) == 1 and top_level_entries[0].is_dir():
        search_root = top_level_entries[0]
    else:
        search_root = extraction_root

    xml_files = [path for path in search_root.rglob("*.xml") if path.is_file()]

    if not xml_files:
        raise HTTPException(status_code=400, detail="No XML file found in uploaded ZIP archive.")
    if len(xml_files) > 1:
        raise HTTPException(status_code=400, detail="Multiple XML files found in uploaded ZIP archive.")

    return xml_files[0]


def _upload_files_and_update_references(xml_tree: etree._ElementTree | Any, xml_file: Path, extraction_root: Path, adapter_instance: StorageAdapter) -> None:
    """Find all xlink:href attributes in the XML tree, upload the referenced files to the storage adapter, and update the href values to point to the uploaded file URLs.
    Only local file references that are within the extracted archive directory are processed. External URLs and fragment identifiers are ignored.
    """
    href_attr = f"{{{XLINK_NAMESPACE}}}href"
    uploaded_files: dict[Path, str] = {}
    xml_directory = xml_file.parent.resolve()
    archive_root = extraction_root.resolve()

    root = xml_tree.getroot()
    for element in root.iterfind(".//*[@xlink:href]", namespaces={"xlink": XLINK_NAMESPACE}):
        href_value_raw = element.get(href_attr)
        href_value = href_value_raw if isinstance(href_value_raw, str) else ""
        if not href_value:
            continue

        parsed = urlparse(href_value)
        if parsed.scheme or parsed.netloc or href_value.startswith("#"):
            continue

        local_reference = unquote(parsed.path)
        if not local_reference:
            continue

        # TODO unix path could also contain windows backslashes in the filename
        local_reference = local_reference.replace("\\", "/")

        referenced_path = (xml_directory / local_reference).resolve()
        if not _is_path_within(archive_root, referenced_path):
            continue
        if not referenced_path.is_file():
            continue

        if referenced_path not in uploaded_files:
            try:
                with referenced_path.open("rb") as referenced_file:
                    uploaded_files[referenced_path] = adapter_instance.upload_file(referenced_file, CONTAINER)
            except Exception:
                raise HTTPException(status_code=500, detail=f"Failed to upload referenced file '{referenced_path.name}' to the storage adapter.")

        element.set(href_attr, uploaded_files[referenced_path])
