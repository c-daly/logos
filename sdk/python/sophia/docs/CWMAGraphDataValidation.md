# CWMAGraphDataValidation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] 
**message** | **str** |  | [optional] 

## Example

```python
from logos_sophia_sdk.models.cwma_graph_data_validation import CWMAGraphDataValidation

# TODO update the JSON string below
json = "{}"
# create an instance of CWMAGraphDataValidation from a JSON string
cwma_graph_data_validation_instance = CWMAGraphDataValidation.from_json(json)
# print the JSON string representation of the object
print(CWMAGraphDataValidation.to_json())

# convert the object into a dict
cwma_graph_data_validation_dict = cwma_graph_data_validation_instance.to_dict()
# create an instance of CWMAGraphDataValidation from a dict
cwma_graph_data_validation_from_dict = CWMAGraphDataValidation.from_dict(cwma_graph_data_validation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


