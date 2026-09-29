# ListFachbereichWithSachgebiete


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**fachbereich** | **str** | The Fachbereich | 
**sachgebiete** | **List[str]** | The list of Sachgebiete associated with the Fachbereich | 

## Example

```python
from jats_importexport_client.models.list_fachbereich_with_sachgebiete import ListFachbereichWithSachgebiete

# TODO update the JSON string below
json = "{}"
# create an instance of ListFachbereichWithSachgebiete from a JSON string
list_fachbereich_with_sachgebiete_instance = ListFachbereichWithSachgebiete.from_json(json)
# print the JSON string representation of the object
print(ListFachbereichWithSachgebiete.to_json())

# convert the object into a dict
list_fachbereich_with_sachgebiete_dict = list_fachbereich_with_sachgebiete_instance.to_dict()
# create an instance of ListFachbereichWithSachgebiete from a dict
list_fachbereich_with_sachgebiete_from_dict = ListFachbereichWithSachgebiete.from_dict(list_fachbereich_with_sachgebiete_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


