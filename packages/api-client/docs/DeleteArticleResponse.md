# DeleteArticleResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**detail** | **str** |  | [optional] [default to 'Errors occurred during the deletion of the referenced assets. The article was successfully deleted but some associated files could not be removed. Check the errors list for details.']
**errors** | **List[str]** | A list of errors encountered during the deletion process | 

## Example

```python
from jats_importexport_client.models.delete_article_response import DeleteArticleResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DeleteArticleResponse from a JSON string
delete_article_response_instance = DeleteArticleResponse.from_json(json)
# print the JSON string representation of the object
print(DeleteArticleResponse.to_json())

# convert the object into a dict
delete_article_response_dict = delete_article_response_instance.to_dict()
# create an instance of DeleteArticleResponse from a dict
delete_article_response_from_dict = DeleteArticleResponse.from_dict(delete_article_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


