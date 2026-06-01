# jats_importexport_client.UploadApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**upload_xml**](UploadApi.md#upload_xml) | **POST** /upload/xml | Upload a JATS Document (XML) to the storage
[**upload_zip**](UploadApi.md#upload_zip) | **POST** /upload/zip | Upload a JATS Document (ZIP-file) to the storage


# **upload_xml**
> UploadFileResponse upload_xml(xml_file)

Upload a JATS Document (XML) to the storage

This endpoint accepts a JATS document as an XML file upload and uploads it to the storage backend. Note that this endpoint does not support uploading referenced files, so it should only be used for simple JATS documents without external file references. The file can be provided either as a multipart form upload (`xml_file` field) or as a JSON body with the `xml_file` field set to a base64-encoded data URI (e.g. `data:application/xml;base64,<data>`).

### Example


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


# Enter a context with an instance of the API client
with jats_importexport_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = jats_importexport_client.UploadApi(api_client)
    xml_file = None # bytes | 

    try:
        # Upload a JATS Document (XML) to the storage
        api_response = api_instance.upload_xml(xml_file)
        print("The response of UploadApi->upload_xml:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UploadApi->upload_xml: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **xml_file** | **bytes**|  | 

### Return type

[**UploadFileResponse**](UploadFileResponse.md)

### Authorization

No authorization required

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_zip**
> UploadFileResponse upload_zip(zip_file)

Upload a JATS Document (ZIP-file) to the storage

This endpoint accepts a ZIP file containing a JATS document (XML file) and optional referenced files and uploads it to the storage backend. The file can be provided either as a multipart form upload (`zip_file` field) or as a JSON body with the `zip_file` field set to a base64-encoded data URI (e.g. `data:application/zip;base64,<data>`).

### Example


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


# Enter a context with an instance of the API client
with jats_importexport_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = jats_importexport_client.UploadApi(api_client)
    zip_file = None # bytes | 

    try:
        # Upload a JATS Document (ZIP-file) to the storage
        api_response = api_instance.upload_zip(zip_file)
        print("The response of UploadApi->upload_zip:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UploadApi->upload_zip: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **zip_file** | **bytes**|  | 

### Return type

[**UploadFileResponse**](UploadFileResponse.md)

### Authorization

No authorization required

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

