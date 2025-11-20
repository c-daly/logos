# PlanRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**goal** | **str** | Natural-language goal or structured identifier | 
**context** | **Dict[str, object]** | Optional context (entities, constraints, media references) | [optional] 
**constraints** | **List[str]** | Hard constraints the planner must honor | [optional] 
**priority** | **str** | Informational priority label (e.g., P0/P1/P2) | [optional] 
**metadata** | **Dict[str, object]** | Arbitrary metadata for downstream audits | [optional] 

## Example

```python
from logos_sophia_sdk.models.plan_request import PlanRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PlanRequest from a JSON string
plan_request_instance = PlanRequest.from_json(json)
# print the JSON string representation of the object
print(PlanRequest.to_json())

# convert the object into a dict
plan_request_dict = plan_request_instance.to_dict()
# create an instance of PlanRequest from a dict
plan_request_from_dict = PlanRequest.from_dict(plan_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


