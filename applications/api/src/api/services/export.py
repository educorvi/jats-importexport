from api.services.common import get_adapter_instance
from api.models import JatsDocumentResponse
from jats_exporters import JatsExporter
from jats_storage_adapters.PloneStorageAdapter import PloneStorageAdapter
from enum import Enum


JATS_EXPORTER = JatsExporter()

class ReturnType(Enum):
    XML = "application/xml"
    JSON = "application/json"

def jats_export(path: str, return_type: ReturnType):
    document = get_adapter_instance().get_jats_document(path)
    jats =JATS_EXPORTER.export(document)
    if return_type == ReturnType.XML:
        return jats
    return JatsDocumentResponse(jats=jats)
