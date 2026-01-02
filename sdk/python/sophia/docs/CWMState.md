# CWMState

Unified causal world model state envelope (thin transport wrapper). All meaningful metadata (provenance) lives in `data`, not on the envelope. This is a breaking change from the previous schema which had provenance on the envelope. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**state_id** | **str** | Globally unique identifier (&#x60;cwm_&lt;model&gt;_&lt;uuid&gt;&#x60;) | 
**model_type** | **str** |  | 
**timestamp** | **datetime** | When the response was generated | 
**data** | **Dict[str, object]** | Verbatim node properties including provenance. Contains: - source: Module/job that created it (e.g., jepa_runner, planner) - derivation: How derived (observed, imagined, reflected) - confidence: 0.0-1.0 certainty score (optional) - created: ISO8601 timestamp when node was created - updated: ISO8601 timestamp when node was last modified - tags: Free-form labels (array of strings) - links: Related entity IDs (object with process_ids, plan_id, entity_ids, etc.) - Plus model-specific content (entities, relations for CWM-A; etc.)  | 

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


