# CWMState

Unified causal world model state envelope.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**state_id** | **str** | Globally unique identifier (&#x60;cwm_&lt;model&gt;_&lt;uuid&gt;&#x60;) | 
**model_type** | **str** |  | 
**source** | **str** | Subsystem that emitted the record (e.g., orchestrator, jepa_runner) | 
**timestamp** | **datetime** |  | 
**confidence** | **float** |  | 
**status** | **str** |  | 
**links** | [**CWMStateLinks**](CWMStateLinks.md) |  | 
**tags** | **List[str]** | Free-form labels for diagnostics filtering | [optional] 
**data** | [**CWMStateData**](CWMStateData.md) |  | 

## Example

```python
from logos_sophia_sdk.models.cwm_state import CWMState

# TODO update the JSON string below
json = "{}"
# create an instance of CWMState from a JSON string
cwm_state_instance = CWMState.from_json(json)
# print the JSON string representation of the object
print(CWMState.to_json())

# convert the object into a dict
cwm_state_dict = cwm_state_instance.to_dict()
# create an instance of CWMState from a dict
cwm_state_from_dict = CWMState.from_dict(cwm_state_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


