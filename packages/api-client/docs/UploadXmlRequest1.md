# UploadXmlRequest1


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**xml_file** | **str** | Base64-encoded data URI of the file (e.g. &#x60;data:&lt;mime&gt;;base64,&lt;data&gt;&#x60;) | 

## Example

```python
from jats_importexport_client.models.upload_xml_request1 import UploadXmlRequest1

# TODO update the JSON string below
json = "{}"
# create an instance of UploadXmlRequest1 from a JSON string
upload_xml_request1_instance = UploadXmlRequest1.from_json(json)
# print the JSON string representation of the object
print(UploadXmlRequest1.to_json())

# convert the object into a dict
upload_xml_request1_dict = upload_xml_request1_instance.to_dict()
# create an instance of UploadXmlRequest1 from a dict
upload_xml_request1_from_dict = UploadXmlRequest1.from_dict(upload_xml_request1_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


