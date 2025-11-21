# SimpleNLPRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** | Text to process | 
**operations** | **List[str]** | List of NLP operations to perform | [optional] [default to [tokenize]]

## Example

```python
from logos_hermes_sdk.models.simple_nlp_request import SimpleNLPRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SimpleNLPRequest from a JSON string
simple_nlp_request_instance = SimpleNLPRequest.from_json(json)
# print the JSON string representation of the object
print(SimpleNLPRequest.to_json())

# convert the object into a dict
simple_nlp_request_dict = simple_nlp_request_instance.to_dict()
# create an instance of SimpleNLPRequest from a dict
simple_nlp_request_from_dict = SimpleNLPRequest.from_dict(simple_nlp_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


