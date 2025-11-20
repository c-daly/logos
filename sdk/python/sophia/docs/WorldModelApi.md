# logos_sophia_sdk.WorldModelApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_state**](WorldModelApi.md#get_state) | **GET** /state | Stream world-model state


# **get_state**
> StateResponse get_state(cursor=cursor, limit=limit, model_type=model_type)

Stream world-model state

Returns the latest persisted CWM states. Supports pagination cursors and optional filtering.


### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import logos_sophia_sdk
from logos_sophia_sdk.models.state_response import StateResponse
from logos_sophia_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = logos_sophia_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = logos_sophia_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with logos_sophia_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logos_sophia_sdk.WorldModelApi(api_client)
    cursor = 'cursor_example' # str | Opaque cursor returned by previous request (for pagination) (optional)
    limit = 50 # int | Maximum number of states to return (optional) (default to 50)
    model_type = 'model_type_example' # str | Filter by causal world model layer (optional)

    try:
        # Stream world-model state
        api_response = api_instance.get_state(cursor=cursor, limit=limit, model_type=model_type)
        print("The response of WorldModelApi->get_state:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorldModelApi->get_state: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **str**| Opaque cursor returned by previous request (for pagination) | [optional] 
 **limit** | **int**| Maximum number of states to return | [optional] [default to 50]
 **model_type** | **str**| Filter by causal world model layer | [optional] 

### Return type

[**StateResponse**](StateResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of CWM state records |  -  |
**401** | Unauthorized |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

