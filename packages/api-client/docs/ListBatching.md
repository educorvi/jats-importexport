# ListBatching


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**current** | **str** | URL of the current batch | 
**next** | **str** | URL of the next batch, if one exists | 
**previous** | **str** | URL of the previous batch, if one exists | 
**first** | **str** | URL of the first batch | 
**last** | **str** | URL of the last batch | 

## Example

```python
from jats_importexport_client.models.list_batching import ListBatching

# TODO update the JSON string below
json = "{}"
# create an instance of ListBatching from a JSON string
list_batching_instance = ListBatching.from_json(json)
# print the JSON string representation of the object
print(ListBatching.to_json())

# convert the object into a dict
list_batching_dict = list_batching_instance.to_dict()
# create an instance of ListBatching from a dict
list_batching_from_dict = ListBatching.from_dict(list_batching_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


