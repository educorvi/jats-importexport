from pathlib import Path

import typer
from jats_importexport_client import ApiClient, Configuration
from jats_importexport_client.api.upload_api import UploadApi
from jats_importexport_client.exceptions import ApiException
from rich.console import Console
from rich.panel import Panel

console = Console()


def upload_command(
    file: Path = typer.Option(
        ...,
        "--file",
        "-f",
        help="Path to the ZIP or XML file to upload",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    host: str = typer.Option("http://localhost:8000", "--host", help="API host URL"),
):
    """
    Upload a JATS document (XML or ZIP) via the API.
    """
    file_ext = file.suffix.lower()
    if file_ext not in [".xml", ".zip"]:
        console.print(f"[bold red]✖ Error:[/bold red] Unsupported file extension '{file_ext}'. Must be .xml or .zip")
        raise typer.Exit(code=1)

    configuration = Configuration(host=host)
    api_client = ApiClient(configuration)
    upload_api = UploadApi(api_client)

    try:
        with console.status(
            f"[bold cyan]Uploading {file_ext[1:].upper()} file '{file.name}' to {host}...[/bold cyan]", spinner="dots"
        ):
            if file_ext == ".xml":
                with open(file, "rb") as f:
                    file_bytes = f.read()
                response = upload_api.upload_xml(xml_file=file_bytes)
            elif file_ext == ".zip":
                with open(file, "rb") as f:
                    file_bytes = f.read()
                response = upload_api.upload_zip(zip_file=file_bytes)

        console.print("[bold green]✔ Upload successful![/bold green]")
        console.print(Panel(str(response), title="API Response", border_style="green"))

    except ApiException as e:
        console.print(f"[bold red]✖ Exception when calling UploadApi:[/bold red]\n{e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]✖ An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


def main():
    typer.run(upload_command)


if __name__ == "__main__":
    main()
