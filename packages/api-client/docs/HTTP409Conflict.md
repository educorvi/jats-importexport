# HTTP409Conflict


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**detail** | **str** |  | [optional] [default to 'Conflict.']

## Example

```python
from jats_importexport_client.models.http409_conflict import HTTP409Conflict

# TODO update the JSON string below
json = "{}"
# create an instance of HTTP409Conflict from a JSON string
http409_conflict_instance = HTTP409Conflict.from_json(json)
# print the JSON string representation of the object
print(HTTP409Conflict.to_json())

# convert the object into a dict
http409_conflict_dict = http409_conflict_instance.to_dict()
# create an instance of HTTP409Conflict from a dict
http409_conflict_from_dict = HTTP409Conflict.from_dict(http409_conflict_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


