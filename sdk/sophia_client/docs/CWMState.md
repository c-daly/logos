# CWMState

Unified Causal World Model State envelope. All world-model emissions (CWM-A, CWM-G, CWM-E) serialize to this structure. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**state_id** | **str** | Globally unique identifier (cwm_&lt;model&gt;_&lt;uuid&gt;) | 
**model_type** | **str** | Which CWM model produced this state | 
**source** | **str** | Subsystem that produced the record (e.g., orchestrator, jepa_runner) | 
**timestamp** | **datetime** | ISO-8601 UTC time the state became valid | 
**confidence** | **float** | Certainty score (JEPA probability, validation score, etc.) | 
**status** | **str** | Distinguishes real-time telemetry from simulations/reflections | 
**links** | [**CWMStateLinks**](CWMStateLinks.md) |  | [optional] 
**tags** | **List[str]** | Free-form labels for filtering (e.g., capability:perception) | [optional] 
**data** | **Dict[str, object]** | Model-specific payload | [optional] 

## Example

```python
from sophia_client.models.cwm_state import CWMState

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


