# HTTP400BadRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**detail** | **str** |  | [optional] [default to 'Bad request.']

## Example

```python
from jats_importexport_client.models.http400_bad_request import HTTP400BadRequest

# TODO update the JSON string below
json = "{}"
# create an instance of HTTP400BadRequest from a JSON string
http400_bad_request_instance = HTTP400BadRequest.from_json(json)
# print the JSON string representation of the object
print(HTTP400BadRequest.to_json())

# convert the object into a dict
http400_bad_request_dict = http400_bad_request_instance.to_dict()
# create an instance of HTTP400BadRequest from a dict
http400_bad_request_from_dict = HTTP400BadRequest.from_dict(http400_bad_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


