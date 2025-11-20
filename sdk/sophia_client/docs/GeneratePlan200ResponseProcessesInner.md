# GeneratePlan200ResponseProcessesInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**capability_id** | **str** |  | [optional] 
**preconditions** | **List[str]** |  | [optional] 
**effects** | **List[str]** |  | [optional] 
**estimated_duration** | **float** |  | [optional] 

## Example

```python
from sophia_client.models.generate_plan200_response_processes_inner import GeneratePlan200ResponseProcessesInner

# TODO update the JSON string below
json = "{}"
# create an instance of GeneratePlan200ResponseProcessesInner from a JSON string
generate_plan200_response_processes_inner_instance = GeneratePlan200ResponseProcessesInner.from_json(json)
# print the JSON string representation of the object
print(GeneratePlan200ResponseProcessesInner.to_json())

# convert the object into a dict
generate_plan200_response_processes_inner_dict = generate_plan200_response_processes_inner_instance.to_dict()
# create an instance of GeneratePlan200ResponseProcessesInner from a dict
generate_plan200_response_processes_inner_from_dict = GeneratePlan200ResponseProcessesInner.from_dict(generate_plan200_response_processes_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


