# sophia_client.DefaultApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**generate_plan**](DefaultApi.md#generate_plan) | **POST** /plan | Generate Plan
[**get_health**](DefaultApi.md#get_health) | **GET** /health | Health Check
[**get_state**](DefaultApi.md#get_state) | **GET** /state | Get Current State
[**run_simulation**](DefaultApi.md#run_simulation) | **POST** /simulate | Run Simulation


# **generate_plan**
> GeneratePlan200Response generate_plan(generate_plan_request)

Generate Plan

Accepts a goal structure, reads from Neo4j, runs the planner, and returns
a process graph with simulation predictions.


### Example


```python
import sophia_client
from sophia_client.models.generate_plan200_response import GeneratePlan200Response
from sophia_client.models.generate_plan_request import GeneratePlanRequest
from sophia_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = sophia_client.Configuration(
    host = "http://localhost:8000"
)


# Enter a context with an instance of the API client
with sophia_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = sophia_client.DefaultApi(api_client)
    generate_plan_request = sophia_client.GeneratePlanRequest() # GeneratePlanRequest | 

    try:
        # Generate Plan
        api_response = api_instance.generate_plan(generate_plan_request)
        print("The response of DefaultApi->generate_plan:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->generate_plan: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **generate_plan_request** | [**GeneratePlanRequest**](GeneratePlanRequest.md)|  | 

### Return type

[**GeneratePlan200Response**](GeneratePlan200Response.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Plan generated successfully |  -  |
**400** | Invalid request (e.g., malformed goal) |  -  |
**422** | Unprocessable entity (e.g., goal cannot be achieved) |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_health**
> GetHealth200Response get_health()

Health Check

Returns health status of Sophia service and its dependencies

### Example


```python
import sophia_client
from sophia_client.models.get_health200_response import GetHealth200Response
from sophia_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = sophia_client.Configuration(
    host = "http://localhost:8000"
)


# Enter a context with an instance of the API client
with sophia_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = sophia_client.DefaultApi(api_client)

    try:
        # Health Check
        api_response = api_instance.get_health()
        print("The response of DefaultApi->get_health:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_health: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetHealth200Response**](GetHealth200Response.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Service is healthy |  -  |
**503** | Service is unhealthy |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_state**
> GetState200Response get_state(cursor=cursor, limit=limit, model_type=model_type, status=status, tags=tags)

Get Current State

Returns the latest entity states, persona metadata, and diagnostic information
for Apollo and other clients. Supports pagination via cursor.


### Example


```python
import sophia_client
from sophia_client.models.get_state200_response import GetState200Response
from sophia_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = sophia_client.Configuration(
    host = "http://localhost:8000"
)


# Enter a context with an instance of the API client
with sophia_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = sophia_client.DefaultApi(api_client)
    cursor = 'cursor_example' # str | Pagination cursor from previous response (optional)
    limit = 50 # int | Maximum number of states to return (optional) (default to 50)
    model_type = 'model_type_example' # str | Filter by CWM model type (optional)
    status = 'status_example' # str | Filter by state status (optional)
    tags = ['tags_example'] # List[str] | Filter by tags (comma-separated) (optional)

    try:
        # Get Current State
        api_response = api_instance.get_state(cursor=cursor, limit=limit, model_type=model_type, status=status, tags=tags)
        print("The response of DefaultApi->get_state:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_state: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **str**| Pagination cursor from previous response | [optional] 
 **limit** | **int**| Maximum number of states to return | [optional] [default to 50]
 **model_type** | **str**| Filter by CWM model type | [optional] 
 **status** | **str**| Filter by state status | [optional] 
 **tags** | [**List[str]**](str.md)| Filter by tags (comma-separated) | [optional] 

### Return type

[**GetState200Response**](GetState200Response.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | State retrieved successfully |  -  |
**400** | Invalid query parameters |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **run_simulation**
> RunSimulation200Response run_simulation(run_simulation_request)

Run Simulation

Triggers CWM-G to perform short-horizon predictions. Results are tagged
as imagined:true in Neo4j. Accepts capability_id and context with entity
references, sensor frames, and optional Talos metadata.


### Example


```python
import sophia_client
from sophia_client.models.run_simulation200_response import RunSimulation200Response
from sophia_client.models.run_simulation_request import RunSimulationRequest
from sophia_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = sophia_client.Configuration(
    host = "http://localhost:8000"
)


# Enter a context with an instance of the API client
with sophia_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = sophia_client.DefaultApi(api_client)
    run_simulation_request = sophia_client.RunSimulationRequest() # RunSimulationRequest | 

    try:
        # Run Simulation
        api_response = api_instance.run_simulation(run_simulation_request)
        print("The response of DefaultApi->run_simulation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->run_simulation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **run_simulation_request** | [**RunSimulationRequest**](RunSimulationRequest.md)|  | 

### Return type

[**RunSimulation200Response**](RunSimulation200Response.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Simulation completed successfully |  -  |
**400** | Invalid request |  -  |
**422** | Simulation failed or capability not available |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

