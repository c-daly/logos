# GeneratePlan200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**plan_id** | **str** | Unique identifier for the generated plan | [optional] 
**processes** | [**List[GeneratePlan200ResponseProcessesInner]**](GeneratePlan200ResponseProcessesInner.md) |  | [optional] 
**causal_links** | [**List[GeneratePlan200ResponseCausalLinksInner]**](GeneratePlan200ResponseCausalLinksInner.md) |  | [optional] 
**cwm_states** | [**List[CWMState]**](CWMState.md) | Newly created CWMState records from planning | [optional] 
**confidence** | **float** | Overall plan confidence (0.0 to 1.0) | [optional] 

## Example

```python
from sophia_client.models.generate_plan200_response import GeneratePlan200Response

# TODO update the JSON string below
json = "{}"
# create an instance of GeneratePlan200Response from a JSON string
generate_plan200_response_instance = GeneratePlan200Response.from_json(json)
# print the JSON string representation of the object
print(GeneratePlan200Response.to_json())

# convert the object into a dict
generate_plan200_response_dict = generate_plan200_response_instance.to_dict()
# create an instance of GeneratePlan200Response from a dict
generate_plan200_response_from_dict = GeneratePlan200Response.from_dict(generate_plan200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


