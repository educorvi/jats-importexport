# ListArticlesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**articles** | **List[str]** | The list of article URLs | 
**count** | **int** | The total number of articles | 

## Example

```python
from jats_importexport_client.models.list_articles_response import ListArticlesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ListArticlesResponse from a JSON string
list_articles_response_instance = ListArticlesResponse.from_json(json)
# print the JSON string representation of the object
print(ListArticlesResponse.to_json())

# convert the object into a dict
list_articles_response_dict = list_articles_response_instance.to_dict()
# create an instance of ListArticlesResponse from a dict
list_articles_response_from_dict = ListArticlesResponse.from_dict(list_articles_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


