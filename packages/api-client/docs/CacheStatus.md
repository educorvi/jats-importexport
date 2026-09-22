# CacheStatus


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**implementation** | **str** | The cache implementation | 
**items_in_cache** | **int** | The number of items currently in the cache | 

## Example

```python
from jats_importexport_client.models.cache_status import CacheStatus

# TODO update the JSON string below
json = "{}"
# create an instance of CacheStatus from a JSON string
cache_status_instance = CacheStatus.from_json(json)
# print the JSON string representation of the object
print(CacheStatus.to_json())

# convert the object into a dict
cache_status_dict = cache_status_instance.to_dict()
# create an instance of CacheStatus from a dict
cache_status_from_dict = CacheStatus.from_dict(cache_status_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


