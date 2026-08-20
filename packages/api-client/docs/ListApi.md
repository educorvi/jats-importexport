# jats_importexport_client.ListApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_articles**](ListApi.md#list_articles) | **GET** /list/ | List Articles


# **list_articles**
> ListArticlesResponse list_articles(fachbereiche=fachbereiche, sachgebiete=sachgebiete, organisationseinheiten=organisationseinheiten)

List Articles

List articles in the storage system. Filtering is supported.

### Example

* Api Key Authentication (APIKeyHeader):

```python
import jats_importexport_client
from jats_importexport_client.models.list_articles_response import ListArticlesResponse
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
    api_instance = jats_importexport_client.ListApi(api_client)
    fachbereiche = ['fachbereiche_example'] # List[Optional[str]] |  (optional)
    sachgebiete = ['sachgebiete_example'] # List[str] |  (optional)
    organisationseinheiten = ['organisationseinheiten_example'] # List[str] |  (optional)

    try:
        # List Articles
        api_response = api_instance.list_articles(fachbereiche=fachbereiche, sachgebiete=sachgebiete, organisationseinheiten=organisationseinheiten)
        print("The response of ListApi->list_articles:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ListApi->list_articles: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **fachbereiche** | [**List[Optional[str]]**](str.md)|  | [optional] 
 **sachgebiete** | [**List[str]**](str.md)|  | [optional] 
 **organisationseinheiten** | [**List[str]**](str.md)|  | [optional] 

### Return type

[**ListArticlesResponse**](ListArticlesResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**500** | Internal Server Error |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

