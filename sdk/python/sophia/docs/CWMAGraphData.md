# CWMAGraphData

Payload for CWM-A (abstract reasoning) outputs.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entities** | **List[object]** | Normalized entity diffs | [optional] 
**relations** | **List[object]** | Relationship diffs | [optional] 
**violations** | **List[str]** | SHACL validation issues, if any | [optional] 
**validation** | [**CWMAGraphDataValidation**](CWMAGraphDataValidation.md) |  | [optional] 

## Example

```python
from logos_sophia_sdk.models.cwma_graph_data import CWMAGraphData

# TODO update the JSON string below
json = "{}"
# create an instance of CWMAGraphData from a JSON string
cwma_graph_data_instance = CWMAGraphData.from_json(json)
# print the JSON string representation of the object
print(CWMAGraphData.to_json())

# convert the object into a dict
cwma_graph_data_dict = cwma_graph_data_instance.to_dict()
# create an instance of CWMAGraphData from a dict
cwma_graph_data_from_dict = CWMAGraphData.from_dict(cwma_graph_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


