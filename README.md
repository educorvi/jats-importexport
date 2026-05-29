# jats-importexport

A monorepo for uploading, parsing, converting, and storing [JATS XML](https://jats.nlm.nih.gov/) documents.

## Packages

| Package | Description |
|---|---|
| [`jats-classes`](packages/jats-classes) | Domain models and XML parser for JATS documents |
| [`jats-exporters`](packages/jats-exporters) | Export JATS documents to JATS XML or HTML |
| [`jats-storage-adapters`](packages/jats-storage-adapters) | Fetch and save JATS documents from/to external backends (e.g. Plone) |
| [`api-client`](packages/api-client) | Auto-generated Python client for the REST API |

## Applications

| Application | Description |
|---|---|
| [`api`](applications/api) | FastAPI REST service for uploading and exporting JATS documents |

## Development

Requires [uv](https://docs.astral.sh/uv/) and Python ≥ 3.13.

```sh
make install    # install all workspace dependencies
make test       # run tests
make lint       # lint with ruff
make typecheck  # type-check with ty
```

## Docker

```sh
make build-image  # build ghcr.io/educorvi/jats-importexport:latest
make push-image   # build and push
```
