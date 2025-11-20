# logos_sophia_sdk.SystemApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**health_check**](SystemApi.md#health_check) | **GET** /health | Health check


# **health_check**
> HealthResponse health_check()

Health check

Returns service status and dependency connectivity.

### Example


```python
import logos_sophia_sdk
from logos_sophia_sdk.models.health_response import HealthResponse
from logos_sophia_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = logos_sophia_sdk.Configuration(
    host = "http://localhost:8000"
)


# Enter a context with an instance of the API client
with logos_sophia_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logos_sophia_sdk.SystemApi(api_client)

    try:
        # Health check
        api_response = api_instance.health_check()
        print("The response of SystemApi->health_check:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SystemApi->health_check: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**HealthResponse**](HealthResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Service is healthy |  -  |
**500** | Service unavailable |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

