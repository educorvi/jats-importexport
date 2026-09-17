# HTTP404NotFound


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**detail** | **str** |  | [optional] [default to 'The requested resource was not found.']

## Example

```python
from jats_importexport_client.models.http404_not_found import HTTP404NotFound

# TODO update the JSON string below
json = "{}"
# create an instance of HTTP404NotFound from a JSON string
http404_not_found_instance = HTTP404NotFound.from_json(json)
# print the JSON string representation of the object
print(HTTP404NotFound.to_json())

# convert the object into a dict
http404_not_found_dict = http404_not_found_instance.to_dict()
# create an instance of HTTP404NotFound from a dict
http404_not_found_from_dict = HTTP404NotFound.from_dict(http404_not_found_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


