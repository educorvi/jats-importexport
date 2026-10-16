from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from jats_importexport_client.exceptions import ApiException
from typer.testing import CliRunner

from cli.main import app


@pytest.mark.parametrize(
    ("export_type", "response", "expected"),
    [
        ("jats", SimpleNamespace(jats="<article>ä</article>"), "<article>ä</article>".encode()),
        ("html", SimpleNamespace(front="<header>Title</header>", html="<p>Body</p>"),
         b"<header>Title</header>\n<p>Body</p>"),
        ("md", SimpleNamespace(md="# Title\nä"), "# Title\nä".encode()),
        ("pdf", b"%PDF-1.7\n\x00\xff", b"%PDF-1.7\n\x00\xff"),
        ("metadata", SimpleNamespace(metadata=Mock(model_dump_json=Mock(return_value='{"title": "Title"}'))),
         b'{"title": "Title"}'),
    ],
)
def test_export_writes_format(tmp_path, export_type, response, expected):
    output = tmp_path / "exported"
    with patch("cli.main.ApiClient") as client, patch("cli.main.ExportApi") as export_api:
        method = getattr(export_api.return_value, f"export_{export_type}")
        method.return_value = response
        result = CliRunner().invoke(app, [
            "export", "storage/article.xml", str(output), "--type", export_type,
            "--host", "https://example.org", "--api-key", "secret",
        ])

    assert result.exit_code == 0, result.output
    assert output.read_bytes() == expected
    method.assert_called_once_with(path="storage/article.xml")
    configuration = client.call_args.args[0]
    assert configuration.host == "https://example.org"
    assert configuration.api_key["APIKeyHeader"] == "secret"


@pytest.mark.parametrize("options", [[], ["--type", "unknown"]])
def test_export_requires_valid_type(tmp_path, options):
    with patch("cli.main.ApiClient") as client:
        result = CliRunner().invoke(app, ["export", "article.xml", str(tmp_path / "out"), *options])
    assert result.exit_code == 2
    client.assert_not_called()


def test_export_api_failure_preserves_existing_file(tmp_path):
    output = tmp_path / "article.xml"
    output.write_text("existing")
    with patch("cli.main.ApiClient"), patch("cli.main.ExportApi") as export_api:
        export_api.return_value.export_jats.side_effect = ApiException(status=404, reason="Not found")
        result = CliRunner().invoke(app, ["export", "article.xml", str(output), "--type", "jats"])
    assert result.exit_code == 1
    assert "API export failed" in result.output
    assert output.read_text() == "existing"


def test_export_write_failure(tmp_path):
    with patch("cli.main.ApiClient"), patch("cli.main.ExportApi") as export_api:
        export_api.return_value.export_pdf.return_value = b"%PDF"
        result = CliRunner().invoke(app, ["export", "article.xml", str(tmp_path), "--type", "pdf"])
    assert result.exit_code == 1
    assert "Could not write" in result.output
