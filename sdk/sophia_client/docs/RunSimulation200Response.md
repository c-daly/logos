# RunSimulation200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**simulation_id** | **str** | Unique identifier for this simulation run | [optional] 
**imagined_states** | [**List[CWMState]**](CWMState.md) |  | [optional] 
**predicted_outcomes** | [**List[RunSimulation200ResponsePredictedOutcomesInner]**](RunSimulation200ResponsePredictedOutcomesInner.md) |  | [optional] 
**metadata** | [**RunSimulation200ResponseMetadata**](RunSimulation200ResponseMetadata.md) |  | [optional] 

## Example

```python
from sophia_client.models.run_simulation200_response import RunSimulation200Response

# TODO update the JSON string below
json = "{}"
# create an instance of RunSimulation200Response from a JSON string
run_simulation200_response_instance = RunSimulation200Response.from_json(json)
# print the JSON string representation of the object
print(RunSimulation200Response.to_json())

# convert the object into a dict
run_simulation200_response_dict = run_simulation200_response_instance.to_dict()
# create an instance of RunSimulation200Response from a dict
run_simulation200_response_from_dict = RunSimulation200Response.from_dict(run_simulation200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


