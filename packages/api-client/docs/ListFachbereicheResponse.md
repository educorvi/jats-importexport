# ListFachbereicheResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**fachbereiche** | **List[str]** | The list of Fachbereiche | 

## Example

```python
from jats_importexport_client.models.list_fachbereiche_response import ListFachbereicheResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ListFachbereicheResponse from a JSON string
list_fachbereiche_response_instance = ListFachbereicheResponse.from_json(json)
# print the JSON string representation of the object
print(ListFachbereicheResponse.to_json())

# convert the object into a dict
list_fachbereiche_response_dict = list_fachbereiche_response_instance.to_dict()
# create an instance of ListFachbereicheResponse from a dict
list_fachbereiche_response_from_dict = ListFachbereicheResponse.from_dict(list_fachbereiche_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


