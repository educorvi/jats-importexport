# jats_importexport_client.CacheManagementApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**clear_export_cache**](CacheManagementApi.md#clear_export_cache) | **DELETE** /cache/ | Clear Export Cache
[**get_cache_status**](CacheManagementApi.md#get_cache_status) | **GET** /cache/ | Get Cache Status


# **clear_export_cache**
> CacheClearedResponse clear_export_cache(path=path, webcode=webcode)

Clear Export Cache

Clear the export cache for a given path or webcode

### Example

* Api Key Authentication (APIKeyHeader):

```python
import jats_importexport_client
from jats_importexport_client.models.cache_cleared_response import CacheClearedResponse
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
    api_instance = jats_importexport_client.CacheManagementApi(api_client)
    path = 'path_example' # str |  (optional)
    webcode = 'webcode_example' # str |  (optional)

    try:
        # Clear Export Cache
        api_response = api_instance.clear_export_cache(path=path, webcode=webcode)
        print("The response of CacheManagementApi->clear_export_cache:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CacheManagementApi->clear_export_cache: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **path** | **str**|  | [optional] 
 **webcode** | **str**|  | [optional] 

### Return type

[**CacheClearedResponse**](CacheClearedResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cache_status**
> Dict[str, CacheStatus] get_cache_status()

Get Cache Status

### Example

* Api Key Authentication (APIKeyHeader):

```python
import jats_importexport_client
from jats_importexport_client.models.cache_status import CacheStatus
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
    api_instance = jats_importexport_client.CacheManagementApi(api_client)

    try:
        # Get Cache Status
        api_response = api_instance.get_cache_status()
        print("The response of CacheManagementApi->get_cache_status:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CacheManagementApi->get_cache_status: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**Dict[str, CacheStatus]**](CacheStatus.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

