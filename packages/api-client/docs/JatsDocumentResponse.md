# JatsDocumentResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**jats** | **str** | The JATS XML document | 

## Example

```python
from jats_importexport_client.models.jats_document_response import JatsDocumentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of JatsDocumentResponse from a JSON string
jats_document_response_instance = JatsDocumentResponse.from_json(json)
# print the JSON string representation of the object
print(JatsDocumentResponse.to_json())

# convert the object into a dict
jats_document_response_dict = jats_document_response_instance.to_dict()
# create an instance of JatsDocumentResponse from a dict
jats_document_response_from_dict = JatsDocumentResponse.from_dict(jats_document_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


