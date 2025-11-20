# logos_sophia_sdk.PlanningApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_plan**](PlanningApi.md#create_plan) | **POST** /plan | Create plan
[**run_simulation**](PlanningApi.md#run_simulation) | **POST** /simulate | Run capability simulation


# **create_plan**
> PlanResponse create_plan(plan_request)

Create plan

Generate a plan for the given goal/context and persist resulting CWM state updates. Successful responses include identifiers plus any new CWM_A/CWM_G/CWM_E records.


### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import logos_sophia_sdk
from logos_sophia_sdk.models.plan_request import PlanRequest
from logos_sophia_sdk.models.plan_response import PlanResponse
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
    api_instance = logos_sophia_sdk.PlanningApi(api_client)
    plan_request = logos_sophia_sdk.PlanRequest() # PlanRequest | 

    try:
        # Create plan
        api_response = api_instance.create_plan(plan_request)
        print("The response of PlanningApi->create_plan:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PlanningApi->create_plan: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **plan_request** | [**PlanRequest**](PlanRequest.md)|  | 

### Return type

[**PlanResponse**](PlanResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Plan created successfully |  -  |
**400** | Invalid request payload |  -  |
**401** | Unauthorized |  -  |
**422** | Planning failed due to constraints/validation |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **run_simulation**
> SimulationResponse run_simulation(simulation_request)

Run capability simulation

Performs JEPA/simulator rollouts for the requested capability using supplied context. Imagined CWM states are persisted and returned to the caller.


### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import logos_sophia_sdk
from logos_sophia_sdk.models.simulation_request import SimulationRequest
from logos_sophia_sdk.models.simulation_response import SimulationResponse
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
    api_instance = logos_sophia_sdk.PlanningApi(api_client)
    simulation_request = logos_sophia_sdk.SimulationRequest() # SimulationRequest | 

    try:
        # Run capability simulation
        api_response = api_instance.run_simulation(simulation_request)
        print("The response of PlanningApi->run_simulation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PlanningApi->run_simulation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **simulation_request** | [**SimulationRequest**](SimulationRequest.md)|  | 

### Return type

[**SimulationResponse**](SimulationResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Simulation completed |  -  |
**400** | Invalid request payload |  -  |
**401** | Unauthorized |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

