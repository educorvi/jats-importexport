# UploadDocxRequest1


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**docx_file** | **str** | Base64-encoded data URI of the file (e.g. &#x60;data:&lt;mime&gt;;base64,&lt;data&gt;&#x60;) | 

## Example

```python
from jats_importexport_client.models.upload_docx_request1 import UploadDocxRequest1

# TODO update the JSON string below
json = "{}"
# create an instance of UploadDocxRequest1 from a JSON string
upload_docx_request1_instance = UploadDocxRequest1.from_json(json)
# print the JSON string representation of the object
print(UploadDocxRequest1.to_json())

# convert the object into a dict
upload_docx_request1_dict = upload_docx_request1_instance.to_dict()
# create an instance of UploadDocxRequest1 from a dict
upload_docx_request1_from_dict = UploadDocxRequest1.from_dict(upload_docx_request1_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


