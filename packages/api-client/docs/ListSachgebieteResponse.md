# ListSachgebieteResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sachgebiete** | **List[str]** | The list of Sachgebiete | 

## Example

```python
from jats_importexport_client.models.list_sachgebiete_response import ListSachgebieteResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ListSachgebieteResponse from a JSON string
list_sachgebiete_response_instance = ListSachgebieteResponse.from_json(json)
# print the JSON string representation of the object
print(ListSachgebieteResponse.to_json())

# convert the object into a dict
list_sachgebiete_response_dict = list_sachgebiete_response_instance.to_dict()
# create an instance of ListSachgebieteResponse from a dict
list_sachgebiete_response_from_dict = ListSachgebieteResponse.from_dict(list_sachgebiete_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


