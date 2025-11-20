# GeneratePlanRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**goal** | **str** | Goal description in natural language | 
**goal_state** | [**GeneratePlanRequestGoalState**](GeneratePlanRequestGoalState.md) |  | [optional] 
**context** | **Dict[str, object]** | Additional context for planning | [optional] 

## Example

```python
from sophia_client.models.generate_plan_request import GeneratePlanRequest

# TODO update the JSON string below
json = "{}"
# create an instance of GeneratePlanRequest from a JSON string
generate_plan_request_instance = GeneratePlanRequest.from_json(json)
# print the JSON string representation of the object
print(GeneratePlanRequest.to_json())

# convert the object into a dict
generate_plan_request_dict = generate_plan_request_instance.to_dict()
# create an instance of GeneratePlanRequest from a dict
generate_plan_request_from_dict = GeneratePlanRequest.from_dict(generate_plan_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


