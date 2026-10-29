# jats_importexport_client.ExportApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**export_html**](ExportApi.md#export_html) | **GET** /export/html | Export Html
[**export_jats**](ExportApi.md#export_jats) | **GET** /export/jats | Export Jats
[**export_md**](ExportApi.md#export_md) | **GET** /export/md | Export Md
[**export_metadata**](ExportApi.md#export_metadata) | **GET** /export/metadata | Export Metadata
[**export_pdf**](ExportApi.md#export_pdf) | **GET** /export/pdf | Export Pdf
[**export_zip**](ExportApi.md#export_zip) | **GET** /export/zip | Export a ZIP file containing the assets (if present) and all export formats
[**structure_tree**](ExportApi.md#structure_tree) | **GET** /export/structure-tree | Structure Tree


# **export_html**
> HtmlDocumentResponse export_html(include_edit_links=include_edit_links, path=path, webcode=webcode)

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
    api_instance = jats_importexport_client.ExportApi(api_client)
    include_edit_links = False # bool |  (optional) (default to False)
    path = 'path_example' # str |  (optional)
    webcode = 'webcode_example' # str |  (optional)

    try:
        # Export Html
        api_response = api_instance.export_html(include_edit_links=include_edit_links, path=path, webcode=webcode)
        print("The response of ExportApi->export_html:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExportApi->export_html: %s\n" % e)
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
**404** | Not Found |  -  |
**409** | Conflict |  -  |
**422** | Unprocessable Content |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **export_jats**
> JatsDocumentResponse export_jats(path=path, webcode=webcode)

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
    api_instance = jats_importexport_client.ExportApi(api_client)
    path = 'path_example' # str |  (optional)
    webcode = 'webcode_example' # str |  (optional)

    try:
        # Export Jats
        api_response = api_instance.export_jats(path=path, webcode=webcode)
        print("The response of ExportApi->export_jats:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExportApi->export_jats: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **path** | **str**|  | [optional] 
 **webcode** | **str**|  | [optional] 

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
**404** | Not Found |  -  |
**409** | Conflict |  -  |
**422** | Unprocessable Content |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **export_md**
> MarkdownDocumentResponse export_md(include_edit_links=include_edit_links, path=path, webcode=webcode)

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
    api_instance = jats_importexport_client.ExportApi(api_client)
    include_edit_links = False # bool |  (optional) (default to False)
    path = 'path_example' # str |  (optional)
    webcode = 'webcode_example' # str |  (optional)

    try:
        # Export Md
        api_response = api_instance.export_md(include_edit_links=include_edit_links, path=path, webcode=webcode)
        print("The response of ExportApi->export_md:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExportApi->export_md: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **include_edit_links** | **bool**|  | [optional] [default to False]
 **path** | **str**|  | [optional] 
 **webcode** | **str**|  | [optional] 

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
**404** | Not Found |  -  |
**409** | Conflict |  -  |
**422** | Unprocessable Content |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **export_metadata**
> MetadataResponse export_metadata(path=path, webcode=webcode)

Export Metadata

### Example

* Api Key Authentication (APIKeyHeader):

```python
import jats_importexport_client
from jats_importexport_client.models.metadata_response import MetadataResponse
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
    api_instance = jats_importexport_client.ExportApi(api_client)
    path = 'path_example' # str |  (optional)
    webcode = 'webcode_example' # str |  (optional)

    try:
        # Export Metadata
        api_response = api_instance.export_metadata(path=path, webcode=webcode)
        print("The response of ExportApi->export_metadata:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExportApi->export_metadata: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **path** | **str**|  | [optional] 
 **webcode** | **str**|  | [optional] 

### Return type

[**MetadataResponse**](MetadataResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Not Found |  -  |
**409** | Conflict |  -  |
**422** | Unprocessable Content |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **export_pdf**
> bytes export_pdf(path=path, webcode=webcode)

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
    api_instance = jats_importexport_client.ExportApi(api_client)
    path = 'path_example' # str |  (optional)
    webcode = 'webcode_example' # str |  (optional)

    try:
        # Export Pdf
        api_response = api_instance.export_pdf(path=path, webcode=webcode)
        print("The response of ExportApi->export_pdf:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExportApi->export_pdf: %s\n" % e)
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
**404** | Not Found |  -  |
**409** | Conflict |  -  |
**422** | Unprocessable Content |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **export_zip**
> bytes export_zip(path=path, webcode=webcode)

Export a ZIP file containing the assets (if present) and all export formats

The assets (media files) are exported to a media directory (if present). In the exported JATS, HTML and Markdown files, the links to media files are replaced with the corresponding paths in the media directory. In the PDF file, the media files are embedded directly.

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
    api_instance = jats_importexport_client.ExportApi(api_client)
    path = 'path_example' # str |  (optional)
    webcode = 'webcode_example' # str |  (optional)

    try:
        # Export a ZIP file containing the assets (if present) and all export formats
        api_response = api_instance.export_zip(path=path, webcode=webcode)
        print("The response of ExportApi->export_zip:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExportApi->export_zip: %s\n" % e)
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
 - **Accept**: application/zip, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | ZIP file |  -  |
**404** | Not Found |  -  |
**409** | Conflict |  -  |
**422** | Unprocessable Content |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **structure_tree**
> StructureTreeResponse structure_tree(max_level=max_level, path=path, webcode=webcode)

Structure Tree

### Example

* Api Key Authentication (APIKeyHeader):

```python
import jats_importexport_client
from jats_importexport_client.models.structure_tree_response import StructureTreeResponse
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
    api_instance = jats_importexport_client.ExportApi(api_client)
    max_level = 56 # int |  (optional)
    path = 'path_example' # str |  (optional)
    webcode = 'webcode_example' # str |  (optional)

    try:
        # Structure Tree
        api_response = api_instance.structure_tree(max_level=max_level, path=path, webcode=webcode)
        print("The response of ExportApi->structure_tree:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExportApi->structure_tree: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **max_level** | **int**|  | [optional] 
 **path** | **str**|  | [optional] 
 **webcode** | **str**|  | [optional] 

### Return type

[**StructureTreeResponse**](StructureTreeResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Not Found |  -  |
**409** | Conflict |  -  |
**422** | Unprocessable Content |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

