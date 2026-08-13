# jats_importexport_client.UploadApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**upload_docx**](UploadApi.md#upload_docx) | **POST** /upload/docx | Upload a DOCX file, convert it to JATS XML, and upload to the storage
[**upload_xml**](UploadApi.md#upload_xml) | **POST** /upload/xml | Upload a JATS Document (XML) to the storage
[**upload_zip**](UploadApi.md#upload_zip) | **POST** /upload/zip | Upload a JATS Document (ZIP-file) to the storage


# **upload_docx**
> UploadFileResponse upload_docx(docx_file, container=container, assets_container=assets_container, use_html_sections=use_html_sections)

Upload a DOCX file, convert it to JATS XML, and upload to the storage

This endpoint accepts a DOCX file upload, converts it to JATS XML, and uploads it to the storage backend. The file can be provided either as a multipart form upload (`docx_file` field) or as a JSON body with the `docx_file` field set to a base64-encoded data URI (e.g. `data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,<data>`). The target containers for the uploaded files and assets can be specified using the `container` and `assets_container` query parameters. If not specified, the default containers will be used. The `use_html_sections` query parameter can be set to `true` to transform sections into EasySection. This only works when using storage adapters that support EasySection, like PloneStorageAdapter.

### Example

* Api Key Authentication (APIKeyHeader):

```python
import jats_importexport_client
from jats_importexport_client.models.upload_file_response import UploadFileResponse
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
    api_instance = jats_importexport_client.UploadApi(api_client)
    docx_file = None # bytes | 
    container = 'container_example' # str |  (optional)
    assets_container = 'assets_container_example' # str |  (optional)
    use_html_sections = False # bool |  (optional) (default to False)

    try:
        # Upload a DOCX file, convert it to JATS XML, and upload to the storage
        api_response = api_instance.upload_docx(docx_file, container=container, assets_container=assets_container, use_html_sections=use_html_sections)
        print("The response of UploadApi->upload_docx:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UploadApi->upload_docx: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **docx_file** | **bytes**|  | 
 **container** | **str**|  | [optional] 
 **assets_container** | **str**|  | [optional] 
 **use_html_sections** | **bool**|  | [optional] [default to False]

### Return type

[**UploadFileResponse**](UploadFileResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: multipart/form-data, application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**400** | Bad Request |  -  |
**413** | Content Too Large |  -  |
**415** | Unsupported Media Type |  -  |
**500** | Internal Server Error |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_xml**
> UploadFileResponse upload_xml(xml_file, container=container)

Upload a JATS Document (XML) to the storage

This endpoint accepts a JATS document as an XML file upload and uploads it to the storage backend. Note that this endpoint does not support uploading referenced files, so it should only be used for simple JATS documents without external file references. The file can be provided either as a multipart form upload (`xml_file` field) or as a JSON body with the `xml_file` field set to a base64-encoded data URI (e.g. `data:application/xml;base64,<data>`). The target container for the uploaded file can be specified using the `container` query parameter. If not specified, the default container will be used.

### Example

* Api Key Authentication (APIKeyHeader):

```python
import jats_importexport_client
from jats_importexport_client.models.upload_file_response import UploadFileResponse
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
    api_instance = jats_importexport_client.UploadApi(api_client)
    xml_file = None # bytes | 
    container = 'container_example' # str |  (optional)

    try:
        # Upload a JATS Document (XML) to the storage
        api_response = api_instance.upload_xml(xml_file, container=container)
        print("The response of UploadApi->upload_xml:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UploadApi->upload_xml: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **xml_file** | **bytes**|  | 
 **container** | **str**|  | [optional] 

### Return type

[**UploadFileResponse**](UploadFileResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: multipart/form-data, application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**400** | Bad Request |  -  |
**413** | Content Too Large |  -  |
**415** | Unsupported Media Type |  -  |
**500** | Internal Server Error |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_zip**
> UploadFileResponse upload_zip(zip_file, container=container, assets_container=assets_container)

Upload a JATS Document (ZIP-file) to the storage

This endpoint accepts a ZIP file containing a JATS document (XML file) and optional referenced asset files and uploads it to the storage backend. The file can be provided either as a multipart form upload (`zip_file` field) or as a JSON body with the `zip_file` field set to a base64-encoded data URI (e.g. `data:application/zip;base64,<data>`). The target containers for the uploaded files and assets can be specified using the `container` and `assets_container` query parameters. If not specified, the default containers will be used.

### Example

* Api Key Authentication (APIKeyHeader):

```python
import jats_importexport_client
from jats_importexport_client.models.upload_file_response import UploadFileResponse
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
    api_instance = jats_importexport_client.UploadApi(api_client)
    zip_file = None # bytes | 
    container = 'container_example' # str |  (optional)
    assets_container = 'assets_container_example' # str |  (optional)

    try:
        # Upload a JATS Document (ZIP-file) to the storage
        api_response = api_instance.upload_zip(zip_file, container=container, assets_container=assets_container)
        print("The response of UploadApi->upload_zip:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UploadApi->upload_zip: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **zip_file** | **bytes**|  | 
 **container** | **str**|  | [optional] 
 **assets_container** | **str**|  | [optional] 

### Return type

[**UploadFileResponse**](UploadFileResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: multipart/form-data, application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**400** | Bad Request |  -  |
**413** | Content Too Large |  -  |
**415** | Unsupported Media Type |  -  |
**500** | Internal Server Error |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

