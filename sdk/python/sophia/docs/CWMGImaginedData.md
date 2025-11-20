# CWMGImaginedData

Payload for CWM-G (grounded/JEPA) outputs.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**imagined** | **bool** |  | [optional] [default to True]
**horizon_steps** | **int** |  | [optional] 
**frames** | **List[str]** | URIs or identifiers for imagined frames | [optional] 
**embeddings** | **List[float]** |  | [optional] 
**assumptions** | **List[str]** |  | [optional] 

## Example

```python
from logos_sophia_sdk.models.cwmg_imagined_data import CWMGImaginedData

# TODO update the JSON string below
json = "{}"
# create an instance of CWMGImaginedData from a JSON string
cwmg_imagined_data_instance = CWMGImaginedData.from_json(json)
# print the JSON string representation of the object
print(CWMGImaginedData.to_json())

# convert the object into a dict
cwmg_imagined_data_dict = cwmg_imagined_data_instance.to_dict()
# create an instance of CWMGImaginedData from a dict
cwmg_imagined_data_from_dict = CWMGImaginedData.from_dict(cwmg_imagined_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


