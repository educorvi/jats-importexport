# CacheClearedResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Confirmation message for cache clearance | 

## Example

```python
from jats_importexport_client.models.cache_cleared_response import CacheClearedResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CacheClearedResponse from a JSON string
cache_cleared_response_instance = CacheClearedResponse.from_json(json)
# print the JSON string representation of the object
print(CacheClearedResponse.to_json())

# convert the object into a dict
cache_cleared_response_dict = cache_cleared_response_instance.to_dict()
# create an instance of CacheClearedResponse from a dict
cache_cleared_response_from_dict = CacheClearedResponse.from_dict(cache_cleared_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


