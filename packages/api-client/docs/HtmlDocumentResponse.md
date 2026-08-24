# HtmlDocumentResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**html** | **str** | The HTML document (main content) | 
**front** | **str** | The HTML of the front matter / metadata section | 

## Example

```python
from jats_importexport_client.models.html_document_response import HtmlDocumentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of HtmlDocumentResponse from a JSON string
html_document_response_instance = HtmlDocumentResponse.from_json(json)
# print the JSON string representation of the object
print(HtmlDocumentResponse.to_json())

# convert the object into a dict
html_document_response_dict = html_document_response_instance.to_dict()
# create an instance of HtmlDocumentResponse from a dict
html_document_response_from_dict = HtmlDocumentResponse.from_dict(html_document_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


