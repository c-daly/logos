# DefaultApi

All URIs are relative to *http://localhost:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**generatePlan**](DefaultApi.md#generateplanoperation) | **POST** /plan | Generate Plan |
| [**getHealth**](DefaultApi.md#gethealth) | **GET** /health | Health Check |
| [**getState**](DefaultApi.md#getstate) | **GET** /state | Get Current State |
| [**runSimulation**](DefaultApi.md#runsimulationoperation) | **POST** /simulate | Run Simulation |



## generatePlan

> GeneratePlan200Response generatePlan(generatePlanRequest)

Generate Plan

Accepts a goal structure, reads from Neo4j, runs the planner, and returns a process graph with simulation predictions. 

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '@logos/sophia-client';
import type { GeneratePlanOperationRequest } from '@logos/sophia-client';

async function example() {
  console.log("🚀 Testing @logos/sophia-client SDK...");
  const api = new DefaultApi();

  const body = {
    // GeneratePlanRequest
    generatePlanRequest: ...,
  } satisfies GeneratePlanOperationRequest;

  try {
    const data = await api.generatePlan(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **generatePlanRequest** | [GeneratePlanRequest](GeneratePlanRequest.md) |  | |

### Return type

[**GeneratePlan200Response**](GeneratePlan200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Plan generated successfully |  -  |
| **400** | Invalid request (e.g., malformed goal) |  -  |
| **422** | Unprocessable entity (e.g., goal cannot be achieved) |  -  |
| **500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getHealth

> GetHealth200Response getHealth()

Health Check

Returns health status of Sophia service and its dependencies

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '@logos/sophia-client';
import type { GetHealthRequest } from '@logos/sophia-client';

async function example() {
  console.log("🚀 Testing @logos/sophia-client SDK...");
  const api = new DefaultApi();

  try {
    const data = await api.getHealth();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**GetHealth200Response**](GetHealth200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Service is healthy |  -  |
| **503** | Service is unhealthy |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getState

> GetState200Response getState(cursor, limit, modelType, status, tags)

Get Current State

Returns the latest entity states, persona metadata, and diagnostic information for Apollo and other clients. Supports pagination via cursor. 

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '@logos/sophia-client';
import type { GetStateRequest } from '@logos/sophia-client';

async function example() {
  console.log("🚀 Testing @logos/sophia-client SDK...");
  const api = new DefaultApi();

  const body = {
    // string | Pagination cursor from previous response (optional)
    cursor: cursor_example,
    // number | Maximum number of states to return (optional)
    limit: 56,
    // 'CWM_A' | 'CWM_G' | 'CWM_E' | Filter by CWM model type (optional)
    modelType: modelType_example,
    // 'observed' | 'imagined' | 'reflected' | Filter by state status (optional)
    status: status_example,
    // Array<string> | Filter by tags (comma-separated) (optional)
    tags: ...,
  } satisfies GetStateRequest;

  try {
    const data = await api.getState(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **cursor** | `string` | Pagination cursor from previous response | [Optional] [Defaults to `undefined`] |
| **limit** | `number` | Maximum number of states to return | [Optional] [Defaults to `50`] |
| **modelType** | `CWM_A`, `CWM_G`, `CWM_E` | Filter by CWM model type | [Optional] [Defaults to `undefined`] [Enum: CWM_A, CWM_G, CWM_E] |
| **status** | `observed`, `imagined`, `reflected` | Filter by state status | [Optional] [Defaults to `undefined`] [Enum: observed, imagined, reflected] |
| **tags** | `Array<string>` | Filter by tags (comma-separated) | [Optional] |

### Return type

[**GetState200Response**](GetState200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | State retrieved successfully |  -  |
| **400** | Invalid query parameters |  -  |
| **500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## runSimulation

> RunSimulation200Response runSimulation(runSimulationRequest)

Run Simulation

Triggers CWM-G to perform short-horizon predictions. Results are tagged as imagined:true in Neo4j. Accepts capability_id and context with entity references, sensor frames, and optional Talos metadata. 

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '@logos/sophia-client';
import type { RunSimulationOperationRequest } from '@logos/sophia-client';

async function example() {
  console.log("🚀 Testing @logos/sophia-client SDK...");
  const api = new DefaultApi();

  const body = {
    // RunSimulationRequest
    runSimulationRequest: ...,
  } satisfies RunSimulationOperationRequest;

  try {
    const data = await api.runSimulation(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **runSimulationRequest** | [RunSimulationRequest](RunSimulationRequest.md) |  | |

### Return type

[**RunSimulation200Response**](RunSimulation200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Simulation completed successfully |  -  |
| **400** | Invalid request |  -  |
| **422** | Simulation failed or capability not available |  -  |
| **500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

