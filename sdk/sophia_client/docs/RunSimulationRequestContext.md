# RunSimulationRequestContext

Simulation context

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entity_ids** | **List[str]** | Entity references for simulation | 
**media_sample_id** | **str** | Reference to perception sample | [optional] 
**talos_metadata** | **Dict[str, object]** | Optional Talos-specific context | [optional] 
**horizon_steps** | **int** | Number of steps to simulate ahead | [optional] [default to 5]

## Example

```python
from sophia_client.models.run_simulation_request_context import RunSimulationRequestContext

# TODO update the JSON string below
json = "{}"
# create an instance of RunSimulationRequestContext from a JSON string
run_simulation_request_context_instance = RunSimulationRequestContext.from_json(json)
# print the JSON string representation of the object
print(RunSimulationRequestContext.to_json())

# convert the object into a dict
run_simulation_request_context_dict = run_simulation_request_context_instance.to_dict()
# create an instance of RunSimulationRequestContext from a dict
run_simulation_request_context_from_dict = RunSimulationRequestContext.from_dict(run_simulation_request_context_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


