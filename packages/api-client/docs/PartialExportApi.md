# jats_importexport_client.PartialExportApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**export_partial_html**](PartialExportApi.md#export_partial_html) | **GET** /export/partial/html | Export Html
[**export_partial_jats**](PartialExportApi.md#export_partial_jats) | **GET** /export/partial/jats | Export Jats
[**export_partial_md**](PartialExportApi.md#export_partial_md) | **GET** /export/partial/md | Export Md
[**export_partial_pdf**](PartialExportApi.md#export_partial_pdf) | **GET** /export/partial/pdf | Export Pdf


# **export_partial_html**
> HtmlDocumentPartialResponse export_partial_html(include_edit_links=include_edit_links, path=path, webcode=webcode, sub_path=sub_path)

Export Html

### Example

* Api Key Authentication (APIKeyHeader):

```python
import jats_importexport_client
from jats_importexport_client.models.html_document_partial_response import HtmlDocumentPartialResponse
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
    api_instance = jats_importexport_client.PartialExportApi(api_client)
    include_edit_links = False # bool |  (optional) (default to False)
    path = 'path_example' # str |  (optional)
    webcode = 'webcode_example' # str |  (optional)
    sub_path = '' # str |  (optional) (default to '')

    try:
        # Export Html
        api_response = api_instance.export_partial_html(include_edit_links=include_edit_links, path=path, webcode=webcode, sub_path=sub_path)
        print("The response of PartialExportApi->export_partial_html:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PartialExportApi->export_partial_html: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **include_edit_links** | **bool**|  | [optional] [default to False]
 **path** | **str**|  | [optional] 
 **webcode** | **str**|  | [optional] 
 **sub_path** | **str**|  | [optional] [default to &#39;&#39;]

### Return type

[**HtmlDocumentPartialResponse**](HtmlDocumentPartialResponse.md)

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
**404** | Not Found |  -  |
**409** | Conflict |  -  |
**422** | Unprocessable Content |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **export_partial_jats**
> JatsDocumentResponse export_partial_jats(path=path, webcode=webcode, sub_path=sub_path)

Export Jats

### Example

* Api Key Authentication (APIKeyHeader):

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
    api_instance = jats_importexport_client.PartialExportApi(api_client)
    path = 'path_example' # str |  (optional)
    webcode = 'webcode_example' # str |  (optional)
    sub_path = '' # str |  (optional) (default to '')

    try:
        # Export Jats
        api_response = api_instance.export_partial_jats(path=path, webcode=webcode, sub_path=sub_path)
        print("The response of PartialExportApi->export_partial_jats:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PartialExportApi->export_partial_jats: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **path** | **str**|  | [optional] 
 **webcode** | **str**|  | [optional] 
 **sub_path** | **str**|  | [optional] [default to &#39;&#39;]

### Return type

[**JatsDocumentResponse**](JatsDocumentResponse.md)

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
**404** | Not Found |  -  |
**409** | Conflict |  -  |
**422** | Unprocessable Content |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **export_partial_md**
> MarkdownDocumentResponse export_partial_md(include_edit_links=include_edit_links, path=path, webcode=webcode, sub_path=sub_path)

Export Md

### Example

* Api Key Authentication (APIKeyHeader):

```python
import jats_importexport_client
from jats_importexport_client.models.markdown_document_response import MarkdownDocumentResponse
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
    api_instance = jats_importexport_client.PartialExportApi(api_client)
    include_edit_links = False # bool |  (optional) (default to False)
    path = 'path_example' # str |  (optional)
    webcode = 'webcode_example' # str |  (optional)
    sub_path = '' # str |  (optional) (default to '')

    try:
        # Export Md
        api_response = api_instance.export_partial_md(include_edit_links=include_edit_links, path=path, webcode=webcode, sub_path=sub_path)
        print("The response of PartialExportApi->export_partial_md:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PartialExportApi->export_partial_md: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **include_edit_links** | **bool**|  | [optional] [default to False]
 **path** | **str**|  | [optional] 
 **webcode** | **str**|  | [optional] 
 **sub_path** | **str**|  | [optional] [default to &#39;&#39;]

### Return type

[**MarkdownDocumentResponse**](MarkdownDocumentResponse.md)

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
**404** | Not Found |  -  |
**409** | Conflict |  -  |
**422** | Unprocessable Content |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **export_partial_pdf**
> bytes export_partial_pdf(path=path, webcode=webcode, sub_path=sub_path)

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
    api_instance = jats_importexport_client.PartialExportApi(api_client)
    path = 'path_example' # str |  (optional)
    webcode = 'webcode_example' # str |  (optional)
    sub_path = '' # str |  (optional) (default to '')

    try:
        # Export Pdf
        api_response = api_instance.export_partial_pdf(path=path, webcode=webcode, sub_path=sub_path)
        print("The response of PartialExportApi->export_partial_pdf:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PartialExportApi->export_partial_pdf: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **path** | **str**|  | [optional] 
 **webcode** | **str**|  | [optional] 
 **sub_path** | **str**|  | [optional] [default to &#39;&#39;]

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
**400** | Bad Request |  -  |
**404** | Not Found |  -  |
**409** | Conflict |  -  |
**422** | Unprocessable Content |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

