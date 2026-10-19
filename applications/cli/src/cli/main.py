import glob
import shutil
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from enum import StrEnum
from functools import partial
from pathlib import Path

import jats_classes
import typer
import xmlschema
from jats_classes import JATSDocument
from jats_exporters.jats import JatsExporter
from jats_importexport_client import ApiClient, Configuration
from jats_importexport_client.api.export_api import ExportApi
from jats_importexport_client.api.list_api import ListApi
from jats_importexport_client.api.upload_api import UploadApi
from jats_importexport_client.exceptions import ApiException
from lxml import etree
from rich.console import Console
from rich.panel import Panel

console = Console()
app = typer.Typer(help="Sort, upload, validate and export JATS documents.", no_args_is_help=True)


# General utility functions for the CLI application


def _resolve_paths(file_patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    for pattern in file_patterns:
        matches = glob.glob(pattern, recursive=True)
        if not matches:
            console.print(f"[bold red]✖ Error:[/bold red] No file or directory found for pattern '{pattern}'")
        for match in matches:
            path = Path(match)
            if not path.is_file() and not path.is_dir():
                console.print(f"[bold yellow]✖ Warning:[/bold yellow] Path '{path}' is neither a file nor a directory.")
                continue
            if path.is_file() and path.suffix.lower() not in [".xml", ".zip", ".ocf"]:
                console.print(
                    f"[bold red]✖ Error:[/bold red] Unsupported file extension '{path.suffix}' for file "
                    f"'{path.name}'. Must be .xml, .zip, or .ocf"
                )
                continue
            files.append(path)
    if not files:
        console.print("[bold red]✖ Error:[/bold red] No files or directories found to process.")
        raise typer.Exit(code=1)
    return files


def _create_zip(directory: Path) -> Path:
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_zip:
        zip_path = Path(tmp_zip.name)
    console.print(f"[bold yellow]📦 Zipping directory '{directory.name}' to '{zip_path}'...[/bold yellow]")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for entry in directory.rglob("*"):
            if entry.is_file():
                zipf.write(entry, entry.relative_to(directory))
    return zip_path


# Uploading files to the server


def _upload_single_file(
    file: Path,
    configuration: Configuration,
    host: str,
    container: str | None,
) -> int:
    exit_code = 0
    temp_file_to_upload: Path | None = None
    file_to_process = file
    response: object = None

    try:
        if file.is_dir():
            temp_file_to_upload = _create_zip(file)
            file_to_process = temp_file_to_upload
            file_ext = ".zip"
        else:
            file_ext = file_to_process.suffix.lower()

        # Each call gets its own ApiClient to avoid thread-safety issues with shared connections.
        with ApiClient(configuration) as api_client:
            upload_api = UploadApi(api_client)
            console.print(
                f"[bold cyan]↑ Uploading {file_ext[1:].upper()} file '{file_to_process.name}' to {host}...[/bold cyan]"
            )
            with open(file_to_process, "rb") as f:
                file_bytes = f.read()
            if file_ext == ".xml":
                response = upload_api.upload_xml(
                    xml_file=file_bytes, _content_type="multipart/form-data", container=container
                )
            elif file_ext in [".zip", ".ocf"]:
                response = upload_api.upload_zip(
                    zip_file=file_bytes,
                    _content_type="multipart/form-data",
                    container=container,
                )

        console.print(f"[bold green]✔ Upload successful for '{file_to_process.name}'![/bold green]")
        console.print(Panel(str(response), title=f"API Response for '{file_to_process.name}'", border_style="green"))

    except ApiException as e:
        console.print(f"[bold red]✖ Exception when calling UploadApi for '{file.name}':[/bold red]\n{e}")
        exit_code = 1
    except Exception as e:
        console.print(f"[bold red]✖ An unexpected error occurred for '{file.name}':[/bold red] {e}")
        exit_code = 1
    finally:
        if temp_file_to_upload and temp_file_to_upload.exists():
            console.print(f"[bold yellow]🗑 Deleting temporary zip file '{temp_file_to_upload}'...[/bold yellow]")
            temp_file_to_upload.unlink()

    return exit_code


@app.command("upload")
def upload_command(
    file_patterns: list[str] = typer.Argument(
        ...,
        help=(
            "Path(s) to the ZIP, XML file(s) or directory (supports glob patterns) to upload. "
            "Can be specified multiple times. Unquoted glob patterns will be expanded by the shell."
        ),
    ),
    host: str = typer.Option("http://localhost:8000", "--host", help="API host URL"),
    api_key: str = typer.Option(None, "--api-key", "-k", help="Optional API key for authentication (X-API-Key header)"),
    container: str = typer.Option(
        None,
        "--container",
        "-c",
        help="Optional: Target container for the uploaded JATS file(s).",
        rich_help_panel="Advanced",
    ),
    workers: int = typer.Option(1, "--workers", "-w", min=1, help="Number of concurrent upload workers."),
):
    """
    Upload a JATS document (XML or ZIP) via the API.
    """
    files = _resolve_paths(file_patterns)

    configuration = Configuration(host=host)
    if api_key:
        configuration.api_key["APIKeyHeader"] = api_key

    overall_exit_code = 0
    func = partial(_upload_single_file, configuration=configuration, host=host, container=container)
    if workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            results = list(executor.map(func, files))
            if any(result != 0 for result in results):
                overall_exit_code = 1
    else:
        for file in files:
            result = func(file)
            if result != 0:
                overall_exit_code = 1

    if overall_exit_code != 0:
        raise typer.Exit(code=overall_exit_code)


# Sort JATS files by journal title into separate directories


JOURNAL_TITLE_DIRECTORY_MAP = {
    "Muster-DGUV Vorschrift": "vorschriften",
    "DGUV Information": "informationen",
    "DGUV Regel": "regeln",
    "DGUV Grundsatz": "grundsaetze",
}
DEFAULT_SORT_DIRECTORY = "sonstige"


def _get_journal_title(xml_content: bytes) -> str | None:
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    article = etree.fromstring(xml_content, parser=parser)
    titles = article.xpath(
        "./*[local-name()='front']/*[local-name()='journal-meta']"
        "/*[local-name()='journal-title-group']/*[local-name()='journal-title']"
    )
    if not isinstance(titles, list) or not titles:
        return None
    title = titles[0]
    if not isinstance(title, etree._Element):
        return None
    return "".join(text for text in title.itertext() if isinstance(text, str)).strip() or None


def _get_ocf_journal_title(ocf_file: Path) -> tuple[str | None, bool]:
    with zipfile.ZipFile(ocf_file) as archive:
        xml_entries = [
            entry
            for entry in archive.infolist()
            if not entry.is_dir() and Path(entry.filename).suffix.lower() == ".xml"
        ]
        if not xml_entries:
            raise ValueError("Archive contains no XML files")
        titles = {_get_journal_title(archive.read(entry)) for entry in xml_entries}

    if len(titles) > 1:
        return None, True
    return next(iter(titles)), False


@app.command("sort-local")
def sort_local_command(
    input_dir: Path = typer.Argument(..., help="Flat directory containing only .ocf documents."),
    output_dir: Path = typer.Argument(..., help="Directory to store the sorted JATS files."),
):
    """Sort unchanged OCF documents by the journal titles of their XML files."""
    if not input_dir.is_dir():
        console.print(f"[bold red]✖ Input directory does not exist or is not a directory:[/bold red] {input_dir}")
        raise typer.Exit(code=1)

    entries = sorted(input_dir.iterdir())
    invalid_entries = [entry for entry in entries if not entry.is_file() or entry.suffix.lower() != ".ocf"]
    if invalid_entries:
        for entry in invalid_entries:
            console.print(
                f"[bold red]✖ Expected a flat directory containing only .ocf files; found:[/bold red] {entry}"
            )
        raise typer.Exit(code=1)
    if not entries:
        console.print(f"[bold red]✖ No .ocf files found in '{input_dir}'.[/bold red]")
        raise typer.Exit(code=1)

    input_dir_resolved = input_dir.resolve()
    output_dir_resolved = output_dir.resolve()
    if output_dir_resolved == input_dir_resolved or input_dir_resolved in output_dir_resolved.parents:
        console.print("[bold red]✖ Output directory must be outside the input directory.[/bold red]")
        raise typer.Exit(code=1)

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        console.print(f"[bold red]✖ Could not create output directory '{output_dir}':[/bold red] {error}")
        raise typer.Exit(code=1) from error

    exit_code = 0
    for ocf_file in entries:
        try:
            journal_title, has_mixed_titles = _get_ocf_journal_title(ocf_file)
            if has_mixed_titles:
                destination_directory = DEFAULT_SORT_DIRECTORY
                console.print(
                    f"[bold yellow]⚠ '{ocf_file.name}' contains XML files with different journal titles; "
                    f"sorting it into '{DEFAULT_SORT_DIRECTORY}'.[/bold yellow]"
                )
            else:
                destination_directory = JOURNAL_TITLE_DIRECTORY_MAP.get(journal_title or "", DEFAULT_SORT_DIRECTORY)

            destination = output_dir / destination_directory / ocf_file.name
            if destination.exists():
                raise FileExistsError(f"Output file already exists: {destination}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(ocf_file, destination)
            # console.print(f"[bold green]✔ Sorted[/bold green] {ocf_file} → {destination}")
        except Exception as error:
            console.print(f"[bold red]✖ Could not sort '{ocf_file}':[/bold red] {error}")
            exit_code = 1

    if exit_code:
        raise typer.Exit(code=exit_code)


# Exporting documents and saving them to files


class ExportType(StrEnum):
    JATS = "jats"
    HTML = "html"
    MD = "md"
    PDF = "pdf"
    METADATA = "metadata"


@app.command("export")
def export_command(
    path: str = typer.Argument(..., help="Path of the document in the API storage."),
    output_file: Path = typer.Argument(..., help="File to write the exported document to."),
    export_type: ExportType = typer.Option(..., "--type", "-t", help="Required export format."),
    host: str = typer.Option("http://localhost:8000", "--host", help="API host URL"),
    api_key: str = typer.Option(None, "--api-key", "-k", help="Optional API key for authentication (X-API-Key header)"),
):
    """Export a stored document and save it to a file."""
    configuration = Configuration(host=host)
    if api_key:
        configuration.api_key["APIKeyHeader"] = api_key

    try:
        with ApiClient(configuration) as api_client:
            api = ExportApi(api_client)
            if export_type == ExportType.PDF:
                output_file.write_bytes(api.export_pdf(path=path))
            else:
                if export_type == ExportType.JATS:
                    content = api.export_jats(path=path).jats
                elif export_type == ExportType.HTML:
                    response = api.export_html(path=path)
                    content = response.front + "\n" + response.html
                elif export_type == ExportType.MD:
                    content = api.export_md(path=path).md
                else:
                    content = api.export_metadata(path=path).metadata.model_dump_json(indent=2)
                output_file.write_text(content, encoding="utf-8")
    except ApiException as error:
        console.print(f"[bold red]✖ API export failed for '{path}':[/bold red]\n{error}")
        raise typer.Exit(code=1) from error
    except OSError as error:
        console.print(f"[bold red]✖ Could not write '{output_file}':[/bold red]\n{error}")
        raise typer.Exit(code=1) from error

    console.print(f"[bold green]✔ Exported {export_type.value} to {output_file}[/bold green]")


# JATS / XML schema validation


def _get_jats_schema_path() -> str:
    return str(Path(jats_classes.__file__).parent / "schema" / "dguv_jats.xsd")


def _parse_jats_schema(xsd_path: str) -> xmlschema.XMLSchema:
    return xmlschema.XMLSchema(xsd_path)


def _validate_xml_content(xml_content: str, source_name: str, xsd_path: str) -> None:
    try:
        document = JATSDocument.from_xml(xml_content, xsd_path=xsd_path)
    except Exception as error:
        raise ValueError(f"Source JATS '{source_name}' is invalid: {error}") from error

    try:
        exported_xml = JatsExporter().export(document)
        JATSDocument.from_xml(exported_xml, xsd_path=xsd_path)
    except Exception as error:
        raise ValueError(f"Exported JATS for '{source_name}' is invalid: {error}") from error


def _validate_single_file(file: Path, xsd_path: str) -> int:
    temporary_zip: Path | None = None
    try:
        file_to_process = file
        if file.is_dir():
            temporary_zip = _create_zip(file)
            file_to_process = temporary_zip

        if file_to_process.suffix.lower() == ".xml":
            _validate_xml_content(file_to_process.read_text(encoding="utf-8"), str(file), xsd_path)
            validated_sources = [str(file)]
        else:
            with zipfile.ZipFile(file_to_process) as archive:
                xml_entries = [entry for entry in archive.infolist() if entry.filename.lower().endswith(".xml")]
                if not xml_entries:
                    raise ValueError("Archive contains no XML files")
                for entry in xml_entries:
                    _validate_xml_content(archive.read(entry).decode("utf-8"), entry.filename, xsd_path)
                validated_sources = [entry.filename for entry in xml_entries]
    except Exception as error:
        console.print(f"[bold red]✖ INVALID[/bold red] {file}\n[red]{error}[/red]")
        return 1
    finally:
        if temporary_zip and temporary_zip.exists():
            console.print(f"[bold yellow]🗑 Deleting temporary zip file '{temporary_zip}'...[/bold yellow]")
            temporary_zip.unlink()

    console.print(
        f"[bold green]✔ VALID[/bold green] {file} "
        f"[dim]({len(validated_sources)} JATS document(s), import and export)[/dim]"
    )
    return 0


@app.command("validate")
def validate_command(
    file_patterns: list[str] = typer.Argument(
        ...,
        help="Path(s) to JATS XML file(s) or directories to validate without uploading.",
    ),
    workers: int = typer.Option(1, "--workers", "-w", min=1, help="Number of concurrent validation workers."),
):
    """Validate source JATS and JATS regenerated by the exporter."""
    files = _resolve_paths(file_patterns)

    xsd_path = _get_jats_schema_path()
    func = partial(_validate_single_file, xsd_path=xsd_path)
    if workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            results = list(executor.map(func, files))
    else:
        results = [func(file) for file in files]

    valid_count = sum(result == 0 for result in results)
    console.print(f"\n[bold]Validation summary:[/bold] {valid_count}/{len(files)} files valid")
    if valid_count != len(files):
        raise typer.Exit(code=1)


def _reformat_and_save_jats_xml(jats: str, output_path: str = "exported_jats.xml") -> None:
    """Reformat and save JATS XML to a file."""
    from lxml import etree

    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.fromstring(jats.encode("utf-8"), parser)
    pretty_jats = etree.tostring(tree, pretty_print=True, encoding="utf-8").decode("utf-8")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_jats)


@app.command("validate-remote")
def validate_remote_command(
    path: str = typer.Argument(..., help="Path of the JATS document in the API storage."),
    host: str = typer.Option("http://localhost:8000", "--host", help="API host URL"),
    api_key: str = typer.Option(None, "--api-key", "-k", help="Optional API key for authentication (X-API-Key header)"),
):
    """Export one document from the API and validate the returned JATS."""
    configuration = Configuration(host=host)
    if api_key:
        configuration.api_key["APIKeyHeader"] = api_key

    try:
        with ApiClient(configuration) as api_client:
            response = ExportApi(api_client).export_jats(path=path)
        _reformat_and_save_jats_xml(response.jats, output_path="exported_jats.xml")
        JATSDocument.from_xml(response.jats, xsd_path=_get_jats_schema_path())
    except ApiException as error:
        console.print(f"[bold red]✖ API export failed for '{path}':[/bold red]\n{error}")
        raise typer.Exit(code=1) from error
    except Exception as error:
        console.print(f"[bold red]✖ INVALID[/bold red] Exported JATS for '{path}'\n[red]{error}[/red]")
        raise typer.Exit(code=1) from error

    console.print(f"[bold green]✔ VALID[/bold green] Exported JATS for '{path}'")


def _safe_filename(value: str) -> str:
    return "_".join(part for part in value.replace("\\", "/").split("/") if part) or "article"


def _list_all_articles(api: ListApi) -> list[str]:
    articles: list[str] = []
    batch_start = 0
    batch_size = 200

    while True:
        response = api.list_articles(batch_start=batch_start, batch_size=batch_size)
        articles.extend(response.articles)
        if batch_start + len(response.articles) >= response.count or not response.articles:
            return articles
        batch_start += len(response.articles)


@app.command("validate-all")
def validate_all_command(
    output_folder: Path = typer.Argument(..., help="Folder where article XML and result files are written."),
    host: str = typer.Option("http://localhost:8000", "--host", help="API host URL"),
    api_key: str = typer.Option(None, "--api-key", "-k", help="Optional API key for authentication (X-API-Key header)"),
):
    """Export and validate all articles found."""
    output_folder.mkdir(parents=True, exist_ok=True)
    configuration = Configuration(host=host)
    if api_key:
        configuration.api_key["APIKeyHeader"] = api_key

    xsd_path = _get_jats_schema_path()
    xml_schema = _parse_jats_schema(xsd_path)
    try:
        with ApiClient(configuration) as api_client:
            list_api = ListApi(api_client)
            export_api = ExportApi(api_client)
            try:
                articles = _list_all_articles(list_api)
            except Exception as error:
                console.print(f"[bold red]✖ Error listing articles:[/bold red]\n{error}")
                raise typer.Exit(code=1) from error

            if not articles:
                console.print("[bold red]✖ No articles found.[/bold red]")
                raise typer.Exit(code=1)

            for index, article_path in enumerate(articles, start=1):
                stem = f"{index:04d}_{_safe_filename(article_path)}"
                xml_path = output_folder / f"{stem}.xml"
                result_path = output_folder / f"{stem}.txt"
                try:
                    response = export_api.export_jats(path=article_path)
                    JATSDocument.from_xml_with_parsed_schema(response.jats, xml_schema=xml_schema)
                except Exception as error:
                    _reformat_and_save_jats_xml(response.jats, output_path=str(xml_path))
                    result_path.write_text(
                        f"INVALID\npath: {article_path}\nerror: {error}\n",
                        encoding="utf-8",
                    )
    except ApiException as error:
        console.print(f"[bold red]✖ API error:[/bold red]\n{error}")
        raise typer.Exit(code=1) from error

    console.print(f"[bold green]✔ Results written to {output_folder}[/bold green]")


def main():
    app()


if __name__ == "__main__":
    main()
