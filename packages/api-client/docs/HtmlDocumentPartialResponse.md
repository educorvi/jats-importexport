# HtmlDocumentPartialResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**html** | **str** | The HTML document (main content) | 

## Example

```python
from jats_importexport_client.models.html_document_partial_response import HtmlDocumentPartialResponse

# TODO update the JSON string below
json = "{}"
# create an instance of HtmlDocumentPartialResponse from a JSON string
html_document_partial_response_instance = HtmlDocumentPartialResponse.from_json(json)
# print the JSON string representation of the object
print(HtmlDocumentPartialResponse.to_json())

# convert the object into a dict
html_document_partial_response_dict = html_document_partial_response_instance.to_dict()
# create an instance of HtmlDocumentPartialResponse from a dict
html_document_partial_response_from_dict = HtmlDocumentPartialResponse.from_dict(html_document_partial_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


