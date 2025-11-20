# CWMStateData

Model-specific payload

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entities** | **List[object]** | Normalized entity diffs | [optional] 
**relations** | **List[object]** | Relationship diffs | [optional] 
**violations** | **List[str]** | SHACL validation issues, if any | [optional] 
**validation** | [**CWMAGraphDataValidation**](CWMAGraphDataValidation.md) |  | [optional] 
**imagined** | **bool** |  | [optional] [default to True]
**horizon_steps** | **int** |  | [optional] 
**frames** | **List[str]** | URIs or identifiers for imagined frames | [optional] 
**embeddings** | **List[float]** |  | [optional] 
**assumptions** | **List[str]** |  | [optional] 
**sentiment** | **str** | e.g., confident, cautious | [optional] 
**confidence_delta** | **float** |  | [optional] 
**caution_delta** | **float** |  | [optional] 
**narrative** | **str** | Short diary-style reflection | [optional] 

## Example

```python
from logos_sophia_sdk.models.cwm_state_data import CWMStateData

# TODO update the JSON string below
json = "{}"
# create an instance of CWMStateData from a JSON string
cwm_state_data_instance = CWMStateData.from_json(json)
# print the JSON string representation of the object
print(CWMStateData.to_json())

# convert the object into a dict
cwm_state_data_dict = cwm_state_data_instance.to_dict()
# create an instance of CWMStateData from a dict
cwm_state_data_from_dict = CWMStateData.from_dict(cwm_state_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


