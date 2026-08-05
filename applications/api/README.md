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
| `GET` | `/export/cache` | Get Redis cache status (enabled flag and prefix) |
| `DELETE` | `/export/cache` | Clear the export cache (optionally for a specific `path`) |

Upload endpoints accept either a `multipart/form-data` upload or a JSON body with a base64-encoded data URI (e.g. `data:application/xml;base64,<data>`).

Export endpoints always return JSON.

An interactive API reference is available at `/docs` when the server is running.

## Running

```sh
uv run start-api
```

Or with Docker (from the repo root):

```sh
docker run -p 8000:8000 \
  -e API_KEY=your-secret-key \
  -e STORAGE_ADAPTER=plone \
  -e PLONE_BASE_URL=http://localhost:8080/Plone \
  -e PLONE_USERNAME=admin \
  -e PLONE_PASSWORD=admin \
  ghcr.io/educorvi/jats-importexport:latest
```

## Authentication

All `/upload/*` and `/export/*` endpoints require an API key when `API_KEY` is set.
`/status` is always public.

Pass the key in the `X-API-Key` request header:

```sh
curl -H "X-API-Key: <your-key>" http://localhost:8000/export/jats?path=vol1/article
```

When `API_KEY` is **not** set, authentication is disabled and all endpoints are open.
The server logs a warning on startup in that case.

> **Production note:** always set `API_KEY` in production deployments.

## Configuration

All settings are read from environment variables.

### Server

| Variable | Default | Description |
|---|---|---|
| `API_KEY` | *(unset)* | API key required in `X-API-Key` header; auth disabled when unset |
| `API_KEY_MANAGER_URL` | *(unset)* | Base URL of an external API key manager used to validate keys (requires `API_KEY_MANAGER_API_ID`) |
| `API_KEY_MANAGER_API_ID` | *(unset)* | API ID sent to the API key manager when validating keys |
| `API_HOST` | `0.0.0.0` | Bind host |
| `API_PORT` | `8000` | Bind port |
| `API_RELOAD` | `false` | Enable auto-reload (development only) |
| `API_WORKERS` | `1` | Number of worker processes |
| `API_CORS_ORIGINS` | `*` | Comma-separated list of allowed CORS origins |

### Storage

| Variable | Default | Description |
|---|---|---|
| `STORAGE_ADAPTER` | `plone` | Storage backend to use (`plone`) |
| `STORAGE_CONTAINER` | `jats-file` | Default container path for JATS XML files |
| `ASSETS_STORAGE_CONTAINER` | `jats-assets` | Default container path for referenced asset files |
| `MAX_ZIP_FILE_COUNT` | `10000` | Maximum number of files allowed in an uploaded ZIP |
| `MAX_ZIP_UNCOMPRESSED_SIZE` | `536870912` | Maximum uncompressed ZIP size in bytes (512 MB) |
| `REDIS_HOST` | `localhost` | Hostname of the Redis instance used for caching |
| `CACHE_PREFIX` | `jats-importexport-cache` | Key prefix used by the Redis cache |

Plone-specific environment variables are documented in [`jats-storage-adapters`](../../packages/jats-storage-adapters).

## Caching

Export responses are cached in Redis via [FastAPI Cache 2](https://github.com/long2ice/fastapi-cache).

Cache keys encode the export function name and the (URL-encoded) document path, e.g. `jats-importexport-cache:export:export_jats:vol1%2Farticle`.

When a document is **uploaded or overwritten**, the cache entries for that document path are automatically invalidated.

You can also manage the cache manually:

```sh
# Check cache status
curl -H "X-API-Key: <your-key>" http://localhost:8000/export/cache

# Clear the entire export cache
curl -X DELETE -H "X-API-Key: <your-key>" http://localhost:8000/export/cache

# Clear cache for a specific document
curl -X DELETE -H "X-API-Key: <your-key>" "http://localhost:8000/export/cache?path=vol1/article"
```

## Generating the OpenAPI client

```sh
make update-client
```

This regenerates [`packages/api-client`](../../packages/api-client) from the current OpenAPI schema.
