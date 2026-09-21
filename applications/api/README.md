# api

FastAPI REST service for uploading, storing, and exporting [JATS XML](https://jats.nlm.nih.gov/) documents.

## Endpoints

| Method   | Path           | Description                                                                                          |
|----------|----------------|------------------------------------------------------------------------------------------------------|
| `GET`    | `/status`      | Health check                                                                                         |
| `POST`   | `/upload/xml`  | Upload a JATS document as an XML file                                                                |
| `POST`   | `/upload/zip`  | Upload a JATS document as a ZIP archive                                                              |
| `GET`    | `/export/jats` | Retrieve and export a stored document as JATS XML                                                    |
| `GET`    | `/export/html` | Retrieve and export a stored document as HTML                                                        |
| `GET`    | `/cache/`      | Get cache status (`implementation` and `items_in_cache`)                                             |
| `DELETE` | `/cache/`      | Clear the export cache (optionally for a specific `path` or `webcode`; requires `manage` permission) |

Upload endpoints accept either a `multipart/form-data` upload or a JSON body with a base64-encoded data URI (e.g.
`data:application/xml;base64,<data>`).

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

| Variable                 | Default   | Description                                                                                       |
|--------------------------|-----------|---------------------------------------------------------------------------------------------------|
| `API_KEY`                | *(unset)* | API key required in `X-API-Key` header; auth disabled when unset                                  |
| `API_KEY_MANAGER_URL`    | *(unset)* | Base URL of an external API key manager used to validate keys (requires `API_KEY_MANAGER_API_ID`) |
| `API_KEY_MANAGER_API_ID` | *(unset)* | API ID sent to the API key manager when validating keys                                           |
| `API_HOST`               | `0.0.0.0` | Bind host                                                                                         |
| `API_PORT`               | `8000`    | Bind port                                                                                         |
| `API_METRICS_PORT`       | `8222`    | Port serving Prometheus metrics at `/metrics`                                                     |
| `API_RELOAD`             | `false`   | Enable auto-reload (development only)                                                             |
| `API_WORKERS`            | `1`       | Number of worker processes                                                                        |
| `API_CORS_ORIGINS`       | `*`       | Comma-separated list of allowed CORS origins                                                      |
| `API_LIST_BATCH_SIZE`    | `200`     | Default and maximum number of articles returned by one `/list/` request                           |

### Storage

| Variable                    | Default       | Description                                                                |
|-----------------------------|---------------|----------------------------------------------------------------------------|
| `STORAGE_ADAPTER`           | `plone`       | Storage backend to use (`plone`)                                           |
| `STORAGE_CONTAINER`         | `jats-file`   | Default container path for JATS XML files                                  |
| `ASSETS_STORAGE_CONTAINER`  | `jats-assets` | Default container path for referenced asset files                          |
| `MAX_ZIP_FILE_COUNT`        | `10000`       | Maximum number of files allowed in an uploaded ZIP                         |
| `MAX_ZIP_UNCOMPRESSED_SIZE` | `536870912`   | Maximum uncompressed ZIP size in bytes (512 MB)                            |
| `CACHE_IMPLEMENTATION`      | `inmemory`    | Cache backend: `inmemory` or `valkey`                                      |
| `VALKEY_HOST`               | `localhost`   | Valkey hostname; falls back to deprecated `REDIS_HOST` when unset or empty |
| `VALKEY_DB_EXPORT`          | `0`           | Integer database index used by the shared export cache and as its cache ID |

Plone-specific environment variables are documented in [`jats-storage-adapters`](../../packages/jats-storage-adapters).

## Caching

JATS, HTML, and Markdown exports use the cache backend selected by `CACHE_IMPLEMENTATION`.
The default `inmemory` backend stores entries within each API worker; entries are lost on restart
and are not shared between workers. Set `CACHE_IMPLEMENTATION=valkey` to use Valkey.
Synchronous and asynchronous exports share the cache configured by `VALKEY_DB_EXPORT`.
This setting is parsed as an integer and defaults to database `0`.

Cache entries are identified by document path (with leading and trailing slashes removed)
and export type. HTML with edit links uses a separate entry. Valkey keys look like
`vol1/article:ExportTypes.JATS`; `CACHE_PREFIX` is no longer used.

The XML, ZIP, and DOCX upload endpoints invalidate cache entries for each successfully saved article path.
Use the cache management endpoint to clear stale entries. With `inmemory`, management requests
affect only the worker handling the request. Valkey cache status currently reports
`items_in_cache` as `0` regardless of the actual number of entries.

You can also manage the cache manually:

```sh
# Check cache status
curl -H "X-API-Key: <your-key>" http://localhost:8000/cache/

# Clear the entire export cache
curl -X DELETE -H "X-API-Key: <your-key>" http://localhost:8000/cache/

# Clear cache for a specific document
curl -X DELETE -H "X-API-Key: <your-key>" "http://localhost:8000/cache/?path=vol1/article"
```

**Valkey:** clearing the entire cache calls asynchronous `FLUSHDB`, deleting all keys in the configured database.

## Prometheus cache metrics

`start-api` exposes metrics at `/metrics` on `API_METRICS_PORT` (default `8222`),
aggregated across API workers. Configure Prometheus to scrape this port.

`vur_hub_export_cache_requests_total{type="jats",result="hit",cache_id="0"}` counts
completed cache lookups through `CacheImplementation.get`, with `hit` and `miss` results.
Currently, JATS (`jats`) and Markdown (`md`) exports use this instrumented method;
HTML lookups bypass it, and PDF and metadata exports do not use the cache.
Document paths are not metric labels. Misses are counted even if the subsequent export fails.
`Cache-Control` headers do not currently bypass or refresh the cache.

Cache hit percentage per export type and cache over five minutes:

```promql
100 * sum by (type, cache_id) (rate(vur_hub_export_cache_requests_total{result="hit"}[5m]))
  / sum by (type, cache_id) (rate(vur_hub_export_cache_requests_total[5m]))
```

Series with zero cache traffic in the window have an undefined (`NaN`) ratio.

## Generating the OpenAPI client

```sh
make update-client
```

This regenerates [`packages/api-client`](../../packages/api-client) from the current OpenAPI schema.
