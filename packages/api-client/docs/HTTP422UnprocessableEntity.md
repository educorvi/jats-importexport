# HTTP422UnprocessableEntity


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**detail** | **str** |  | [optional] [default to 'Unprocessable entity.']

## Example

```python
from jats_importexport_client.models.http422_unprocessable_entity import HTTP422UnprocessableEntity

# TODO update the JSON string below
json = "{}"
# create an instance of HTTP422UnprocessableEntity from a JSON string
http422_unprocessable_entity_instance = HTTP422UnprocessableEntity.from_json(json)
# print the JSON string representation of the object
print(HTTP422UnprocessableEntity.to_json())

# convert the object into a dict
http422_unprocessable_entity_dict = http422_unprocessable_entity_instance.to_dict()
# create an instance of HTTP422UnprocessableEntity from a dict
http422_unprocessable_entity_from_dict = HTTP422UnprocessableEntity.from_dict(http422_unprocessable_entity_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


