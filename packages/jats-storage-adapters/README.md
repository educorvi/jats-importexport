# jats-storage-adapters

Storage adapters for fetching and saving [`jats-classes`](../jats-classes) documents to external backends.

## Adapters

### `PloneStorageAdapter`

Reads and writes JATS documents to a [Plone CMS](https://plone.org/) instance via its REST API.

**Required environment variables:**

| Variable | Description |
|---|---|
| `PLONE_BASE_URL` | Root URL of the Plone instance (e.g. `http://localhost:8080/Plone`) |
| `PLONE_USERNAME` | Plone username |
| `PLONE_PASSWORD` | Plone password |

```python
from jats_storage_adapters.PloneStorageAdapter import PloneStorageAdapter

adapter = PloneStorageAdapter()

# Fetch a document
doc = adapter.get_jats_document("vol1/issue2/article")

# Save a document
url = adapter.save_jats_document(doc, "vol1/issue2")

# Upload a binary file
with open("figure.png", "rb") as f:
    url = adapter.upload_file(f, "vol1/issue2")
```

## Extending

Implement `StorageAdapter` to support other backends:

```python
from jats_storage_adapters.interface import StorageAdapter

class MyAdapter(StorageAdapter):
    def upload_file(self, file, container): ...
    def get_jats_document(self, path): ...
    def save_jats_document(self, document, container): ...
```

## Requirements

- Python ≥ 3.13
- `httpx`, `jats-classes`
