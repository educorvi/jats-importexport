# UpdateArticlesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**updated_articles** | **List[str]** | The list of updated article paths (relative to the storage base URL) | 

## Example

```python
from jats_importexport_client.models.update_articles_response import UpdateArticlesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateArticlesResponse from a JSON string
update_articles_response_instance = UpdateArticlesResponse.from_json(json)
# print the JSON string representation of the object
print(UpdateArticlesResponse.to_json())

# convert the object into a dict
update_articles_response_dict = update_articles_response_instance.to_dict()
# create an instance of UpdateArticlesResponse from a dict
update_articles_response_from_dict = UpdateArticlesResponse.from_dict(update_articles_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


