# CacheStatusResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | Indicates if FastAPICache is enabled | 
**prefix** | **str** | The cache prefix used by FastAPICache | 

## Example

```python
from jats_importexport_client.models.cache_status_response import CacheStatusResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CacheStatusResponse from a JSON string
cache_status_response_instance = CacheStatusResponse.from_json(json)
# print the JSON string representation of the object
print(CacheStatusResponse.to_json())

# convert the object into a dict
cache_status_response_dict = cache_status_response_instance.to_dict()
# create an instance of CacheStatusResponse from a dict
cache_status_response_from_dict = CacheStatusResponse.from_dict(cache_status_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


