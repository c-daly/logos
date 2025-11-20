# GetHealth200ResponseMilvus


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connected** | **bool** |  | [optional] 
**collections** | **List[str]** |  | [optional] 

## Example

```python
from sophia_client.models.get_health200_response_milvus import GetHealth200ResponseMilvus

# TODO update the JSON string below
json = "{}"
# create an instance of GetHealth200ResponseMilvus from a JSON string
get_health200_response_milvus_instance = GetHealth200ResponseMilvus.from_json(json)
# print the JSON string representation of the object
print(GetHealth200ResponseMilvus.to_json())

# convert the object into a dict
get_health200_response_milvus_dict = get_health200_response_milvus_instance.to_dict()
# create an instance of GetHealth200ResponseMilvus from a dict
get_health200_response_milvus_from_dict = GetHealth200ResponseMilvus.from_dict(get_health200_response_milvus_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


