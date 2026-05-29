# jats-importexport-client

Auto-generated Python client for the [JATS Import/Export API](../../applications/api).

Generated with [OpenAPI Generator](https://openapi-generator.tech) from the OpenAPI schema at
[`applications/api/openapi.json`](../../applications/api/openapi.json).

## Requirements

- Python ≥ 3.9
- `httpx`, `pydantic ≥ 2`, `python-dateutil`

## Installation

```sh
pip install .
```

## Usage

```python
import jats_importexport_client
from jats_importexport_client.rest import ApiException

configuration = jats_importexport_client.Configuration(host="http://localhost:8000")

async with jats_importexport_client.ApiClient(configuration) as api_client:
    upload_api = jats_importexport_client.UploadApi(api_client)
    response = await upload_api.upload_xml(xml_file=open("article.xml", "rb"))
    print(response.url)
```

## API

| Class | Methods |
|---|---|
| `UploadApi` | `upload_xml`, `upload_zip` |
| `ExportApi` | `export_jats`, `export_html` |
| `StatusApi` | `get_status` |

## Regenerating

Run from the repo root:

```sh
make update-client
```
