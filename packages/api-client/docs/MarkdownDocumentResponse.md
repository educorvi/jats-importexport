# MarkdownDocumentResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**md** | **str** | The Markdown document | 

## Example

```python
from jats_importexport_client.models.markdown_document_response import MarkdownDocumentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of MarkdownDocumentResponse from a JSON string
markdown_document_response_instance = MarkdownDocumentResponse.from_json(json)
# print the JSON string representation of the object
print(MarkdownDocumentResponse.to_json())

# convert the object into a dict
markdown_document_response_dict = markdown_document_response_instance.to_dict()
# create an instance of MarkdownDocumentResponse from a dict
markdown_document_response_from_dict = MarkdownDocumentResponse.from_dict(markdown_document_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


