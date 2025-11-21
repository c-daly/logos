# HealthResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Overall health status | 
**version** | **str** | API version | 
**services** | **Dict[str, str]** | Status of individual services | 
**milvus** | **Dict[str, object]** | Milvus connectivity status | 
**queue** | **Dict[str, object]** | Internal queue status | 
**llm** | **Dict[str, object]** | LLM provider configuration status | 

## Example

```python
from logos_hermes_sdk.models.health_response import HealthResponse

# TODO update the JSON string below
json = "{}"
# create an instance of HealthResponse from a JSON string
health_response_instance = HealthResponse.from_json(json)
# print the JSON string representation of the object
print(HealthResponse.to_json())

# convert the object into a dict
health_response_dict = health_response_instance.to_dict()
# create an instance of HealthResponse from a dict
health_response_from_dict = HealthResponse.from_dict(health_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


