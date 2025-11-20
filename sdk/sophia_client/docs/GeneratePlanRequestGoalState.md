# GeneratePlanRequestGoalState

Target state specification

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entities** | [**List[GeneratePlanRequestGoalStateEntitiesInner]**](GeneratePlanRequestGoalStateEntitiesInner.md) |  | [optional] 

## Example

```python
from sophia_client.models.generate_plan_request_goal_state import GeneratePlanRequestGoalState

# TODO update the JSON string below
json = "{}"
# create an instance of GeneratePlanRequestGoalState from a JSON string
generate_plan_request_goal_state_instance = GeneratePlanRequestGoalState.from_json(json)
# print the JSON string representation of the object
print(GeneratePlanRequestGoalState.to_json())

# convert the object into a dict
generate_plan_request_goal_state_dict = generate_plan_request_goal_state_instance.to_dict()
# create an instance of GeneratePlanRequestGoalState from a dict
generate_plan_request_goal_state_from_dict = GeneratePlanRequestGoalState.from_dict(generate_plan_request_goal_state_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


