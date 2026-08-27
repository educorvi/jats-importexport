# jats_importexport_client.ModifyApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**link_related_articles**](ModifyApi.md#link_related_articles) | **POST** /modify/link-related-articles | Link related articles IDs to the real articles in the storage


# **link_related_articles**
> UpdateArticlesResponse link_related_articles()

Link related articles IDs to the real articles in the storage

### Example

* Api Key Authentication (APIKeyHeader):

```python
import jats_importexport_client
from jats_importexport_client.models.update_articles_response import UpdateArticlesResponse
from jats_importexport_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = jats_importexport_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: APIKeyHeader
configuration.api_key['APIKeyHeader'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['APIKeyHeader'] = 'Bearer'

# Enter a context with an instance of the API client
with jats_importexport_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = jats_importexport_client.ModifyApi(api_client)

    try:
        # Link related articles IDs to the real articles in the storage
        api_response = api_instance.link_related_articles()
        print("The response of ModifyApi->link_related_articles:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModifyApi->link_related_articles: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**UpdateArticlesResponse**](UpdateArticlesResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**400** | Bad Request |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

