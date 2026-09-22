# jats_importexport_client.ExportAsyncApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**export_html_async**](ExportAsyncApi.md#export_html_async) | **GET** /export/async/html | Export Html
[**export_pdf_async**](ExportAsyncApi.md#export_pdf_async) | **GET** /export/async/pdf | Export Pdf
[**export_status_async**](ExportAsyncApi.md#export_status_async) | **GET** /export/async/status | Export Status


# **export_html_async**
> HtmlDocumentResponse export_html_async(include_edit_links=include_edit_links, path=path, webcode=webcode)

Export Html

### Example

* Api Key Authentication (APIKeyHeader):

```python
import jats_importexport_client
from jats_importexport_client.models.html_document_response import HtmlDocumentResponse
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
    api_instance = jats_importexport_client.ExportAsyncApi(api_client)
    include_edit_links = False # bool |  (optional) (default to False)
    path = 'path_example' # str |  (optional)
    webcode = 'webcode_example' # str |  (optional)

    try:
        # Export Html
        api_response = api_instance.export_html_async(include_edit_links=include_edit_links, path=path, webcode=webcode)
        print("The response of ExportAsyncApi->export_html_async:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExportAsyncApi->export_html_async: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **include_edit_links** | **bool**|  | [optional] [default to False]
 **path** | **str**|  | [optional] 
 **webcode** | **str**|  | [optional] 

### Return type

[**HtmlDocumentResponse**](HtmlDocumentResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**202** | In Progress |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **export_pdf_async**
> bytes export_pdf_async(path=path, webcode=webcode)

Export Pdf

### Example

* Api Key Authentication (APIKeyHeader):

```python
import jats_importexport_client
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
    api_instance = jats_importexport_client.ExportAsyncApi(api_client)
    path = 'path_example' # str |  (optional)
    webcode = 'webcode_example' # str |  (optional)

    try:
        # Export Pdf
        api_response = api_instance.export_pdf_async(path=path, webcode=webcode)
        print("The response of ExportAsyncApi->export_pdf_async:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExportAsyncApi->export_pdf_async: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **path** | **str**|  | [optional] 
 **webcode** | **str**|  | [optional] 

### Return type

**bytes**

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/pdf, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | PDF file |  -  |
**202** | In Progress |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **export_status_async**
> AsyncExportAccepted export_status_async(export_type, path=path, webcode=webcode)

Export Status

### Example

* Api Key Authentication (APIKeyHeader):

```python
import jats_importexport_client
from jats_importexport_client.models.async_export_accepted import AsyncExportAccepted
from jats_importexport_client.models.export_type import ExportType
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
    api_instance = jats_importexport_client.ExportAsyncApi(api_client)
    export_type = jats_importexport_client.ExportType() # ExportType | 
    path = 'path_example' # str |  (optional)
    webcode = 'webcode_example' # str |  (optional)

    try:
        # Export Status
        api_response = api_instance.export_status_async(export_type, path=path, webcode=webcode)
        print("The response of ExportAsyncApi->export_status_async:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExportAsyncApi->export_status_async: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **export_type** | [**ExportType**](.md)|  | 
 **path** | **str**|  | [optional] 
 **webcode** | **str**|  | [optional] 

### Return type

[**AsyncExportAccepted**](AsyncExportAccepted.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**500** | Failed |  -  |
**404** | No export was started yet |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

