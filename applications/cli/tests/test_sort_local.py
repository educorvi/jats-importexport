import zipfile

import pytest
from cli.main import app
from typer.testing import CliRunner


def _article_xml(journal_title: str | None) -> bytes:
    title_xml = (
        f"<journal-title-group><journal-title>{journal_title}</journal-title></journal-title-group>"
        if journal_title is not None
        else ""
    )
    return f"<article><front><journal-meta>{title_xml}</journal-meta></front></article>".encode()


def _write_ocf(path, xml_documents: dict[str, bytes]) -> bytes:
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in xml_documents.items():
            archive.writestr(name, content)
    return path.read_bytes()


def test_sort_local_moves_ocf_unchanged_by_journal_title(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    ocf_file = input_dir / "article.ocf"
    original_bytes = _write_ocf(ocf_file, {"article.xml": _article_xml("DGUV Information")})
    output_dir = tmp_path / "sorted"

    result = CliRunner().invoke(app, ["sort-local", str(input_dir), str(output_dir)])

    sorted_ocf = output_dir / "informationen" / ocf_file.name
    assert result.exit_code == 0, result.output
    assert sorted_ocf.read_bytes() == original_bytes
    assert not ocf_file.exists()


def test_sort_local_accepts_multiple_xml_with_same_title(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    ocf_file = input_dir / "issue.ocf"
    original_bytes = _write_ocf(
        ocf_file,
        {
            "first.xml": _article_xml("DGUV Information"),
            "second.xml": _article_xml("DGUV Information"),
        },
    )
    output_dir = tmp_path / "sorted"

    result = CliRunner().invoke(app, ["sort-local", str(input_dir), str(output_dir)])

    assert result.exit_code == 0, result.output
    assert (output_dir / "informationen" / ocf_file.name).read_bytes() == original_bytes
    assert not ocf_file.exists()
    assert "different journal titles" not in result.output


def test_sort_local_sends_mixed_title_ocf_to_sonstige_with_warning(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    ocf_file = input_dir / "mixed.ocf"
    original_bytes = _write_ocf(
        ocf_file,
        {
            "first.xml": _article_xml("DGUV Information"),
            "second.xml": _article_xml("Other journal"),
        },
    )
    output_dir = tmp_path / "sorted"

    result = CliRunner().invoke(app, ["sort-local", str(input_dir), str(output_dir)])

    assert result.exit_code == 0, result.output
    assert (output_dir / "sonstige" / ocf_file.name).read_bytes() == original_bytes
    assert not ocf_file.exists()
    assert "different journal titles" in " ".join(result.output.split())


def test_sort_local_uses_sonstige_for_unmapped_or_missing_titles(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    unmapped_ocf = input_dir / "unmapped.ocf"
    unmapped_bytes = _write_ocf(unmapped_ocf, {"article.xml": _article_xml("Other journal")})
    missing_title_ocf = input_dir / "missing.ocf"
    missing_title_bytes = _write_ocf(missing_title_ocf, {"article.xml": _article_xml(None)})
    output_dir = tmp_path / "sorted"

    result = CliRunner().invoke(app, ["sort-local", str(input_dir), str(output_dir)])

    assert result.exit_code == 0, result.output
    assert (output_dir / "sonstige" / unmapped_ocf.name).read_bytes() == unmapped_bytes
    assert (output_dir / "sonstige" / missing_title_ocf.name).read_bytes() == missing_title_bytes
    assert not unmapped_ocf.exists()
    assert not missing_title_ocf.exists()


@pytest.mark.parametrize("invalid_entry", ["nested", "not-an-archive.zip"])
def test_sort_local_rejects_non_ocf_entries(tmp_path, invalid_entry):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    if invalid_entry == "nested":
        (input_dir / invalid_entry).mkdir()
    else:
        (input_dir / invalid_entry).write_text("not an OCF")

    result = CliRunner().invoke(app, ["sort-local", str(input_dir), str(tmp_path / "sorted")])

    assert result.exit_code == 1
    assert "only .ocf files" in " ".join(result.output.split())


def test_sort_local_rejects_ocf_archives_without_xml(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    _write_ocf(input_dir / "empty.ocf", {"readme.txt": b"not XML"})

    result = CliRunner().invoke(app, ["sort-local", str(input_dir), str(tmp_path / "sorted")])

    assert result.exit_code == 1
    assert "contains no XML files" in " ".join(result.output.split())


def test_sort_local_does_not_overwrite_existing_ocf(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    ocf_file = input_dir / "article.ocf"
    original_bytes = _write_ocf(ocf_file, {"article.xml": _article_xml("DGUV Information")})
    output_dir = tmp_path / "sorted"
    output_ocf = output_dir / "informationen" / ocf_file.name
    output_ocf.parent.mkdir(parents=True)
    output_ocf.write_bytes(b"keep me")

    result = CliRunner().invoke(app, ["sort-local", str(input_dir), str(output_dir)])

    assert result.exit_code == 1
    assert output_ocf.read_bytes() == b"keep me"
    assert ocf_file.read_bytes() == original_bytes
