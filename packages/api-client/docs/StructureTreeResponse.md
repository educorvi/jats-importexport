# StructureTreeResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tree** | [**List[StructureTreeEntry]**](StructureTreeEntry.md) | The list of structure tree entries | 

## Example

```python
from jats_importexport_client.models.structure_tree_response import StructureTreeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of StructureTreeResponse from a JSON string
structure_tree_response_instance = StructureTreeResponse.from_json(json)
# print the JSON string representation of the object
print(StructureTreeResponse.to_json())

# convert the object into a dict
structure_tree_response_dict = structure_tree_response_instance.to_dict()
# create an instance of StructureTreeResponse from a dict
structure_tree_response_from_dict = StructureTreeResponse.from_dict(structure_tree_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


