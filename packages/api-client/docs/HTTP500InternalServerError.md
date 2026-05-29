# HTTP500InternalServerError


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**detail** | **str** |  | [optional] [default to 'An unexpected error occurred.']

## Example

```python
from jats_importexport_client.models.http500_internal_server_error import HTTP500InternalServerError

# TODO update the JSON string below
json = "{}"
# create an instance of HTTP500InternalServerError from a JSON string
http500_internal_server_error_instance = HTTP500InternalServerError.from_json(json)
# print the JSON string representation of the object
print(HTTP500InternalServerError.to_json())

# convert the object into a dict
http500_internal_server_error_dict = http500_internal_server_error_instance.to_dict()
# create an instance of HTTP500InternalServerError from a dict
http500_internal_server_error_from_dict = HTTP500InternalServerError.from_dict(http500_internal_server_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


