# SimpleNlp200ResponseEntitiesInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** |  | [optional] 
**label** | **str** |  | [optional] 
**start** | **int** |  | [optional] 
**end** | **int** |  | [optional] 

## Example

```python
from hermes_client.models.simple_nlp200_response_entities_inner import SimpleNlp200ResponseEntitiesInner

# TODO update the JSON string below
json = "{}"
# create an instance of SimpleNlp200ResponseEntitiesInner from a JSON string
simple_nlp200_response_entities_inner_instance = SimpleNlp200ResponseEntitiesInner.from_json(json)
# print the JSON string representation of the object
print(SimpleNlp200ResponseEntitiesInner.to_json())

# convert the object into a dict
simple_nlp200_response_entities_inner_dict = simple_nlp200_response_entities_inner_instance.to_dict()
# create an instance of SimpleNlp200ResponseEntitiesInner from a dict
simple_nlp200_response_entities_inner_from_dict = SimpleNlp200ResponseEntitiesInner.from_dict(simple_nlp200_response_entities_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


