# jats_importexport_client.ExportApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**export_html**](ExportApi.md#export_html) | **GET** /export/html | Export Html
[**export_jats**](ExportApi.md#export_jats) | **GET** /export/jats | Export Jats


# **export_html**
> HtmlDocumentResponse export_html(path)

Export Html

### Example


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


# Enter a context with an instance of the API client
with jats_importexport_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = jats_importexport_client.ExportApi(api_client)
    path = 'path_example' # str | 

    try:
        # Export Html
        api_response = api_instance.export_html(path)
        print("The response of ExportApi->export_html:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExportApi->export_html: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **path** | **str**|  | 

### Return type

[**HtmlDocumentResponse**](HtmlDocumentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, text/html

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **export_jats**
> JatsDocumentResponse export_jats(path)

Export Jats

### Example


```python
import jats_importexport_client
from jats_importexport_client.models.jats_document_response import JatsDocumentResponse
from jats_importexport_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = jats_importexport_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with jats_importexport_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = jats_importexport_client.ExportApi(api_client)
    path = 'path_example' # str | 

    try:
        # Export Jats
        api_response = api_instance.export_jats(path)
        print("The response of ExportApi->export_jats:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExportApi->export_jats: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **path** | **str**|  | 

### Return type

[**JatsDocumentResponse**](JatsDocumentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/xml

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

