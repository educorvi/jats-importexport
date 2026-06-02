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
    file_ext = file.suffix.lower()
    if file_ext not in [".xml", ".zip"]:
        console.print(
            f"[bold red]✖ Error:[/bold red] Unsupported file extension '{file_ext}' for file '{file.name}'. Must be .xml or .zip"  # noqa: E501
        )
        return 1

    # Each call gets its own ApiClient to avoid thread-safety issues with shared connections.
    try:
        with ApiClient(configuration) as api_client:
            upload_api = UploadApi(api_client)
            console.print(f"[bold cyan]↑ Uploading {file_ext[1:].upper()} file '{file.name}' to {host}...[/bold cyan]")
            if file_ext == ".xml":
                with open(file, "rb") as f:
                    file_bytes = f.read()
                upload_api.upload_xml(xml_file=file_bytes, _content_type="multipart/form-data", container=container)
            elif file_ext == ".zip":
                with open(file, "rb") as f:
                    file_bytes = f.read()
                response = upload_api.upload_zip(
                    zip_file=file_bytes,
                    _content_type="multipart/form-data",
                    container=container,
                    assets_container=assets_container,
                )

        console.print(f"[bold green]✔ Upload successful for '{file.name}'![/bold green]")
        console.print(Panel(str(response), title=f"API Response for '{file.name}'", border_style="green"))

    except ApiException as e:
        console.print(f"[bold red]✖ Exception when calling UploadApi for '{file.name}':[/bold red]\n{e}")
        exit_code = 1
    except Exception as e:
        console.print(f"[bold red]✖ An unexpected error occurred for '{file.name}':[/bold red] {e}")
        exit_code = 1

    return exit_code


def upload_command(
    files: list[Path] = typer.Option(
        ...,
        "--file",
        "-f",
        help="Path to the ZIP or XML file(s) to upload (can be specified multiple times)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
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
    configuration = Configuration(host=host)
    if api_key:
        configuration.api_key["APIKeyHeader"] = api_key

    overall_exit_code = 0
    func = partial(
        _upload_single_file, 
        configuration=configuration, 
        host=host, 
        container=container, 
        assets_container=assets_container
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
