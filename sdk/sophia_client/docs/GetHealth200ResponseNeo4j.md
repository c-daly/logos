# GetHealth200ResponseNeo4j


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connected** | **bool** |  | [optional] 
**latency_ms** | **float** |  | [optional] 

## Example

```python
from sophia_client.models.get_health200_response_neo4j import GetHealth200ResponseNeo4j

# TODO update the JSON string below
json = "{}"
# create an instance of GetHealth200ResponseNeo4j from a JSON string
get_health200_response_neo4j_instance = GetHealth200ResponseNeo4j.from_json(json)
# print the JSON string representation of the object
print(GetHealth200ResponseNeo4j.to_json())

# convert the object into a dict
get_health200_response_neo4j_dict = get_health200_response_neo4j_instance.to_dict()
# create an instance of GetHealth200ResponseNeo4j from a dict
get_health200_response_neo4j_from_dict = GetHealth200ResponseNeo4j.from_dict(get_health200_response_neo4j_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


