# SimpleNLPResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tokens** | **List[str]** |  | [optional] 
**pos_tags** | [**List[POSTag]**](POSTag.md) |  | [optional] 
**lemmas** | **List[str]** |  | [optional] 
**entities** | [**List[Entity]**](Entity.md) |  | [optional] 

## Example

```python
from logos_hermes_sdk.models.simple_nlp_response import SimpleNLPResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SimpleNLPResponse from a JSON string
simple_nlp_response_instance = SimpleNLPResponse.from_json(json)
# print the JSON string representation of the object
print(SimpleNLPResponse.to_json())

# convert the object into a dict
simple_nlp_response_dict = simple_nlp_response_instance.to_dict()
# create an instance of SimpleNLPResponse from a dict
simple_nlp_response_from_dict = SimpleNLPResponse.from_dict(simple_nlp_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


