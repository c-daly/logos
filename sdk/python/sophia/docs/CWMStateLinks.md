# CWMStateLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_ids** | **List[str]** |  | [optional] 
**plan_id** | **str** |  | [optional] 
**entity_ids** | **List[str]** |  | [optional] 
**media_sample_id** | **str** |  | [optional] 
**persona_entry_id** | **str** |  | [optional] 
**talos_run_id** | **str** |  | [optional] 

## Example

```python
from logos_sophia_sdk.models.cwm_state_links import CWMStateLinks

# TODO update the JSON string below
json = "{}"
# create an instance of CWMStateLinks from a JSON string
cwm_state_links_instance = CWMStateLinks.from_json(json)
# print the JSON string representation of the object
print(CWMStateLinks.to_json())

# convert the object into a dict
cwm_state_links_dict = cwm_state_links_instance.to_dict()
# create an instance of CWMStateLinks from a dict
cwm_state_links_from_dict = CWMStateLinks.from_dict(cwm_state_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


