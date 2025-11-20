# RunSimulation200ResponseMetadata


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**model_version** | **str** |  | [optional] 
**horizon** | **int** |  | [optional] 
**assumptions** | **List[str]** |  | [optional] 

## Example

```python
from sophia_client.models.run_simulation200_response_metadata import RunSimulation200ResponseMetadata

# TODO update the JSON string below
json = "{}"
# create an instance of RunSimulation200ResponseMetadata from a JSON string
run_simulation200_response_metadata_instance = RunSimulation200ResponseMetadata.from_json(json)
# print the JSON string representation of the object
print(RunSimulation200ResponseMetadata.to_json())

# convert the object into a dict
run_simulation200_response_metadata_dict = run_simulation200_response_metadata_instance.to_dict()
# create an instance of RunSimulation200ResponseMetadata from a dict
run_simulation200_response_metadata_from_dict = RunSimulation200ResponseMetadata.from_dict(run_simulation200_response_metadata_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


