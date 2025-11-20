# GetState200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**states** | [**List[CWMState]**](CWMState.md) |  | [optional] 
**cursor** | **str** | Cursor for next page (null if no more results) | [optional] 
**total** | **int** | Total number of states matching filters | [optional] 

## Example

```python
from sophia_client.models.get_state200_response import GetState200Response

# TODO update the JSON string below
json = "{}"
# create an instance of GetState200Response from a JSON string
get_state200_response_instance = GetState200Response.from_json(json)
# print the JSON string representation of the object
print(GetState200Response.to_json())

# convert the object into a dict
get_state200_response_dict = get_state200_response_instance.to_dict()
# create an instance of GetState200Response from a dict
get_state200_response_from_dict = GetState200Response.from_dict(get_state200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


