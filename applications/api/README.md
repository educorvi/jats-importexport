# api

FastAPI REST service for uploading, storing, and exporting [JATS XML](https://jats.nlm.nih.gov/) documents.

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/status` | Health check |
| `POST` | `/upload/xml` | Upload a JATS document as an XML file |
| `POST` | `/upload/zip` | Upload a JATS document as a ZIP archive |
| `GET` | `/export/jats` | Retrieve and export a stored document as JATS XML |
| `GET` | `/export/html` | Retrieve and export a stored document as HTML |

Upload endpoints accept either a `multipart/form-data` upload or a JSON body with a base64-encoded data URI (e.g. `data:application/xml;base64,<data>`).

Export endpoints honour the `Accept` header: `application/json` (default), `application/xml`, or `text/html`.

An interactive API reference is available at `/docs` when the server is running.

## Running

```sh
uv run start-api
```

Or with Docker (from the repo root):

```sh
docker run -p 8000:8000 \
  -e STORAGE_ADAPTER=plone \
  -e PLONE_BASE_URL=http://localhost:8080/Plone \
  -e PLONE_USERNAME=admin \
  -e PLONE_PASSWORD=admin \
  ghcr.io/educorvi/jats-importexport:latest
```

## Configuration

All settings are read from environment variables.

### Server

| Variable | Default | Description |
|---|---|---|
| `API_HOST` | `0.0.0.0` | Bind host |
| `API_PORT` | `8000` | Bind port |
| `API_RELOAD` | `false` | Enable auto-reload (development only) |
| `API_WORKERS` | `1` | Number of worker processes |
| `API_CORS_ORIGINS` | `*` | Comma-separated list of allowed CORS origins |

### Storage

| Variable | Default | Description |
|---|---|---|
| `STORAGE_ADAPTER` | `plone` | Storage backend to use (`plone`) |
| `STORAGE_CONTAINER` | `jats-file` | Container path for JATS XML files |
| `ASSETS_STORAGE_CONTAINER` | `jats-assets` | Container path for referenced asset files |
| `MAX_ZIP_FILE_COUNT` | `10000` | Maximum number of files allowed in an uploaded ZIP |
| `MAX_ZIP_UNCOMPRESSED_SIZE` | `536870912` | Maximum uncompressed ZIP size in bytes (512 MB) |

Plone-specific environment variables are documented in [`jats-storage-adapters`](../../packages/jats-storage-adapters).

## Generating the OpenAPI client

```sh
make update-client
```

This regenerates [`packages/api-client`](../../packages/api-client) from the current OpenAPI schema.
