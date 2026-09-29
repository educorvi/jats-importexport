# ListFachbereicheTreeResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**fachbereiche** | [**List[ListFachbereichWithSachgebiete]**](ListFachbereichWithSachgebiete.md) | A tree structure of Fachbereiche and their associated Sachgebiete | 

## Example

```python
from jats_importexport_client.models.list_fachbereiche_tree_response import ListFachbereicheTreeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ListFachbereicheTreeResponse from a JSON string
list_fachbereiche_tree_response_instance = ListFachbereicheTreeResponse.from_json(json)
# print the JSON string representation of the object
print(ListFachbereicheTreeResponse.to_json())

# convert the object into a dict
list_fachbereiche_tree_response_dict = list_fachbereiche_tree_response_instance.to_dict()
# create an instance of ListFachbereicheTreeResponse from a dict
list_fachbereiche_tree_response_from_dict = ListFachbereicheTreeResponse.from_dict(list_fachbereiche_tree_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


