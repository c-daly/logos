# SimulationRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**capability_id** | **str** | Capability or Talos action identifier | 
**context** | **Dict[str, object]** | Structured context (entity IDs, sensor frames, parameters) | 
**horizon_steps** | **int** |  | [optional] [default to 5]
**assumptions** | **List[str]** | Optional assumptions applied to the rollout | [optional] 
**metadata** | **Dict[str, object]** | Miscellaneous metadata for audit trails | [optional] 

## Example

```python
from logos_sophia_sdk.models.simulation_request import SimulationRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SimulationRequest from a JSON string
simulation_request_instance = SimulationRequest.from_json(json)
# print the JSON string representation of the object
print(SimulationRequest.to_json())

# convert the object into a dict
simulation_request_dict = simulation_request_instance.to_dict()
# create an instance of SimulationRequest from a dict
simulation_request_from_dict = SimulationRequest.from_dict(simulation_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


