# PlanRequestGoal

Goal specification with description and target_state

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | Natural-language description of the goal | 
**target_state** | **str** | Identifier for the desired target state | 

## Example

```python
from logos_sophia_sdk.models.plan_request_goal import PlanRequestGoal

# TODO update the JSON string below
json = "{}"
# create an instance of PlanRequestGoal from a JSON string
plan_request_goal_instance = PlanRequestGoal.from_json(json)
# print the JSON string representation of the object
print(PlanRequestGoal.to_json())

# convert the object into a dict
plan_request_goal_dict = plan_request_goal_instance.to_dict()
# create an instance of PlanRequestGoal from a dict
plan_request_goal_from_dict = PlanRequestGoal.from_dict(plan_request_goal_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


