# GeneratePlanRequestGoalStateEntitiesInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entity_id** | **str** |  | [optional] 
**desired_state** | **str** |  | [optional] 

## Example

```python
from sophia_client.models.generate_plan_request_goal_state_entities_inner import GeneratePlanRequestGoalStateEntitiesInner

# TODO update the JSON string below
json = "{}"
# create an instance of GeneratePlanRequestGoalStateEntitiesInner from a JSON string
generate_plan_request_goal_state_entities_inner_instance = GeneratePlanRequestGoalStateEntitiesInner.from_json(json)
# print the JSON string representation of the object
print(GeneratePlanRequestGoalStateEntitiesInner.to_json())

# convert the object into a dict
generate_plan_request_goal_state_entities_inner_dict = generate_plan_request_goal_state_entities_inner_instance.to_dict()
# create an instance of GeneratePlanRequestGoalStateEntitiesInner from a dict
generate_plan_request_goal_state_entities_inner_from_dict = GeneratePlanRequestGoalStateEntitiesInner.from_dict(generate_plan_request_goal_state_entities_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


