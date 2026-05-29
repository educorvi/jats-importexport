# HTTP413PayloadTooLarge


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**detail** | **str** |  | [optional] [default to 'The uploaded file is too large.']

## Example

```python
from jats_importexport_client.models.http413_payload_too_large import HTTP413PayloadTooLarge

# TODO update the JSON string below
json = "{}"
# create an instance of HTTP413PayloadTooLarge from a JSON string
http413_payload_too_large_instance = HTTP413PayloadTooLarge.from_json(json)
# print the JSON string representation of the object
print(HTTP413PayloadTooLarge.to_json())

# convert the object into a dict
http413_payload_too_large_dict = http413_payload_too_large_instance.to_dict()
# create an instance of HTTP413PayloadTooLarge from a dict
http413_payload_too_large_from_dict = HTTP413PayloadTooLarge.from_dict(http413_payload_too_large_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


