# SimpleNlp200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tokens** | **List[str]** | Tokenized text (if requested) | [optional] 
**pos_tags** | [**List[SimpleNlp200ResponsePosTagsInner]**](SimpleNlp200ResponsePosTagsInner.md) | POS tags (if requested) | [optional] 
**lemmas** | **List[str]** | Lemmatized tokens (if requested) | [optional] 
**entities** | [**List[SimpleNlp200ResponseEntitiesInner]**](SimpleNlp200ResponseEntitiesInner.md) | Named entities (if requested) | [optional] 

## Example

```python
from hermes_client.models.simple_nlp200_response import SimpleNlp200Response

# TODO update the JSON string below
json = "{}"
# create an instance of SimpleNlp200Response from a JSON string
simple_nlp200_response_instance = SimpleNlp200Response.from_json(json)
# print the JSON string representation of the object
print(SimpleNlp200Response.to_json())

# convert the object into a dict
simple_nlp200_response_dict = simple_nlp200_response_instance.to_dict()
# create an instance of SimpleNlp200Response from a dict
simple_nlp200_response_from_dict = SimpleNlp200Response.from_dict(simple_nlp200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


