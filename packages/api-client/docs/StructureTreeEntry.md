# StructureTreeEntry


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the article part | 
**path** | **str** | The path of the article part, relative to the article base path | 
**level** | **int** | The level of the article part | 
**type** | **str** | The type of the article part | 
**children** | [**List[StructureTreeEntry]**](StructureTreeEntry.md) | The child entries of the article part, if any | 

## Example

```python
from jats_importexport_client.models.structure_tree_entry import StructureTreeEntry

# TODO update the JSON string below
json = "{}"
# create an instance of StructureTreeEntry from a JSON string
structure_tree_entry_instance = StructureTreeEntry.from_json(json)
# print the JSON string representation of the object
print(StructureTreeEntry.to_json())

# convert the object into a dict
structure_tree_entry_dict = structure_tree_entry_instance.to_dict()
# create an instance of StructureTreeEntry from a dict
structure_tree_entry_from_dict = StructureTreeEntry.from_dict(structure_tree_entry_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


