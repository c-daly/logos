# RunSimulation200ResponsePredictedOutcomesInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entity_id** | **str** |  | [optional] 
**predicted_state** | **str** |  | [optional] 
**confidence** | **float** |  | [optional] 
**timestep** | **int** |  | [optional] 

## Example

```python
from sophia_client.models.run_simulation200_response_predicted_outcomes_inner import RunSimulation200ResponsePredictedOutcomesInner

# TODO update the JSON string below
json = "{}"
# create an instance of RunSimulation200ResponsePredictedOutcomesInner from a JSON string
run_simulation200_response_predicted_outcomes_inner_instance = RunSimulation200ResponsePredictedOutcomesInner.from_json(json)
# print the JSON string representation of the object
print(RunSimulation200ResponsePredictedOutcomesInner.to_json())

# convert the object into a dict
run_simulation200_response_predicted_outcomes_inner_dict = run_simulation200_response_predicted_outcomes_inner_instance.to_dict()
# create an instance of RunSimulation200ResponsePredictedOutcomesInner from a dict
run_simulation200_response_predicted_outcomes_inner_from_dict = RunSimulation200ResponsePredictedOutcomesInner.from_dict(run_simulation200_response_predicted_outcomes_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


