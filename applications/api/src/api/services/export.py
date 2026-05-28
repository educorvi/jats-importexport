from api.models import JatsDocumentResponse
from jats_exporters import JatsExporter
from jats_storage_adapters.PloneStorageAdapter import PloneStorageAdapter
from enum import Enum

# TODO Replace with StorageAdapter from config
STORAGE_ADAPTER = PloneStorageAdapter()
JATS_EXPORTER = JatsExporter()

class ReturnType(Enum):
    XML = "application/xml"
    JSON = "application/json"

def jats_export(path: str, return_type: ReturnType):
    document = STORAGE_ADAPTER.get_jats_document(path)
    jats =JATS_EXPORTER.export(document)
    if return_type == ReturnType.XML:
        return jats
    return JatsDocumentResponse(jats=jats)
