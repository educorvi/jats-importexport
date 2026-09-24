# JATS Import/Export CLI

Command-line client for uploading JATS documents to the JATS Import/Export API.
It accepts JATS XML files, ZIP archives, and directories. Directories are zipped
temporarily before upload.

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)
- A running JATS Import/Export API

## Installation

From the repository root, install the workspace dependencies:

```sh
uv sync
```

Run the CLI through uv:

```sh
uv run jats-cli --help
```

To validate JATS files locally without uploading them:

```sh
uv run jats-validate article.xml
uv run jats-validate article.zip
uv run jats-validate article-with-assets
uv run jats-validate 'documents/**/*.xml' --workers 4
```

To validate JATS returned by the API export endpoint:

```sh
uv run jats-validate-remote storage/path/article.xml \
  --host https://jats.example.org \
  --api-key YOUR_API_KEY
```

This command calls `/export/jats` with the supplied path and validates the
returned JATS once against the packaged XSD. It does not upload or modify the
document.

To validate all articles belonging to one or more Rubriken:

```sh
uv run jats-validate-rubriken "Rubrik A" "Rubrik B" ./validation-results \
  --host https://jats.example.org \
  --api-key YOUR_API_KEY
```

The command reads all result pages from `/list` for each Rubrik, exports every
article through `/export/jats`, validates the returned XML once, and writes one
pretty-printed XML file and one matching `.txt` result file per article. Listing
errors and Rubriken without matches also receive `.txt` result files.

The validation command accepts `.xml`, `.zip`, `.ocf`, and directories, matching
the upload command. Directories are packaged with the same relative paths as
uploads, and every XML member in an archive is checked. Each source is parsed
into `JATSDocument`, validated against the packaged XSD, exported with
`JatsExporter`, and validated again. It prints the file or archive member,
validation stage, schema location, and schema reason for invalid input, and exits
non-zero if any document fails.

## Usage

```text
jats-cli [OPTIONS] FILE_PATTERNS...
```

The API is expected at `http://localhost:8000` by default.

Upload a JATS XML document:

```sh
uv run jats-cli article.xml
```

Upload a ZIP archive to a different API host:

```sh
uv run jats-cli article.zip --host https://jats.example.org
```

Upload a directory. Its contents are recursively packaged into a temporary ZIP
archive; the directory itself is not included as a top-level folder:

```sh
uv run jats-cli ./article-with-assets
```

Upload several files using a quoted glob pattern:

```sh
uv run jats-cli 'documents/**/*.xml'
```

Multiple paths and patterns can be supplied in one invocation:

```sh
uv run jats-cli article.xml issue.zip 'documents/*.xml'
```

### Authentication

Pass an API key with `--api-key` or `-k`. It is sent in the `X-API-Key`
request header:

```sh
uv run jats-cli article.xml --api-key YOUR_API_KEY
```

Be aware that command-line arguments may be visible in shell history and process
listings.

### Containers

Use `--container` (`-c`) to select the target container for the uploaded JATS
document:

```sh
uv run jats-cli article.xml --container articles
```

For ZIP uploads, `--assets-container` (`-a`) can select a separate target for
assets:

```sh
uv run jats-cli article.zip \
  --container articles \
  --assets-container article-assets
```

### Concurrent uploads

Uploads are sequential by default. Increase `--workers` (`-w`) to upload
multiple inputs concurrently:

```sh
uv run jats-cli 'documents/*.xml' --workers 4
```

`--workers` must be at least `1`. Output from concurrent uploads may be
interleaved.

## Options

| Option | Default | Description |
|---|---:|---|
| `--host HOST` | `http://localhost:8000` | JATS Import/Export API base URL |
| `--api-key`, `-k KEY` | none | API key sent using the `X-API-Key` header |
| `--container`, `-c NAME` | none | Target container for JATS documents |
| `--assets-container`, `-a NAME` | none | Target asset container for ZIP uploads |
| `--workers`, `-w COUNT` | `1` | Number of concurrent upload workers |
| `--help` | | Show command help |

## Input behavior

- Supported file extensions are `.xml` and `.zip`, matched case-insensitively.
- Directories are recursively zipped and uploaded as ZIP archives.
- Glob patterns are expanded recursively by the CLI. Quote patterns when the
  shell should not expand them first.
- Files and directories matched by overlapping patterns are not deduplicated.
- A failed upload or invalid input causes a non-zero exit status. When several
  inputs are supplied, the CLI attempts all of them before exiting.
- Successful uploads print the response returned by the API.

## Development

From the repository root:

```sh
uv sync
uv run ruff check applications/cli
uv run ty check applications/cli
```
