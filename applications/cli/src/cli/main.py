import glob
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path

import typer
from jats_importexport_client import ApiClient, Configuration
from jats_importexport_client.api.upload_api import UploadApi
from jats_importexport_client.exceptions import ApiException
from rich.console import Console
from rich.panel import Panel

console = Console()


def _upload_single_file(
    file: Path,
    configuration: Configuration,
    host: str,
    container: str | None,
    assets_container: str | None,
) -> int:
    exit_code = 0
    temp_file_to_upload: Path | None = None
    file_to_process = file

    try:
        if file.is_dir():
            # Create a temporary zip file of the directory's contents
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_zip:
                temp_file_to_upload = Path(tmp_zip.name)
                console.print(
                    f"[bold yellow]📦 Zipping directory '{file.name}' to '{temp_file_to_upload}'...[/bold yellow]"
                )
                with zipfile.ZipFile(temp_file_to_upload, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for entry in file.rglob("*"):
                        if entry.is_file():
                            zipf.write(entry, entry.relative_to(file))
                file_to_process = temp_file_to_upload
            file_ext = ".zip"
        else:
            file_ext = file_to_process.suffix.lower()

        if file_ext not in [".xml", ".zip"]:
            console.print(
                f"[bold red]✖ Error:[/bold red] Unsupported file extension '{file_ext}' for file "
                f"'{file.name}'. Must be .xml or .zip"
            )
            return 1

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
            elif file_ext == ".zip":
                response = upload_api.upload_zip(
                    zip_file=file_bytes,
                    _content_type="multipart/form-data",
                    container=container,
                    assets_container=assets_container,
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
    assets_container: str = typer.Option(
        None,
        "--assets-container",
        "-a",
        help="Optional: Target container for the uploaded asset files (ZIP uploads only).",
        rich_help_panel="Advanced",
    ),
    workers: int = typer.Option(1, "--workers", "-w", min=1, help="Number of concurrent upload workers."),
):
    """
    Upload a JATS document (XML or ZIP) via the API.
    """
    files: list[Path] = []
    for pattern in file_patterns:
        for p in glob.glob(pattern, recursive=True):
            resolved_path = Path(p)
            if resolved_path.is_file() or resolved_path.is_dir():
                files.append(resolved_path)
            else:
                console.print(f"[bold red]✖ Error:[/bold red] No file or directory found for pattern '{p}'")

    if not files:
        console.print("[bold red]✖ Error:[/bold red] No files or directories found to upload.")
        raise typer.Exit(code=1)

    configuration = Configuration(host=host)
    if api_key:
        configuration.api_key["APIKeyHeader"] = api_key

    overall_exit_code = 0
    func = partial(
        _upload_single_file,
        configuration=configuration,
        host=host,
        container=container,
        assets_container=assets_container,
    )
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


def main():
    typer.run(upload_command)


if __name__ == "__main__":
    main()
