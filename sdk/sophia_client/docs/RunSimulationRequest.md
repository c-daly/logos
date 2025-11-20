# RunSimulationRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**capability_id** | **str** | Capability to simulate | 
**context** | [**RunSimulationRequestContext**](RunSimulationRequestContext.md) |  | 

## Example

```python
from sophia_client.models.run_simulation_request import RunSimulationRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RunSimulationRequest from a JSON string
run_simulation_request_instance = RunSimulationRequest.from_json(json)
# print the JSON string representation of the object
print(RunSimulationRequest.to_json())

# convert the object into a dict
run_simulation_request_dict = run_simulation_request_instance.to_dict()
# create an instance of RunSimulationRequest from a dict
run_simulation_request_from_dict = RunSimulationRequest.from_dict(run_simulation_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


