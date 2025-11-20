# EmbedTextRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** | Text to embed | 
**model** | **str** | Optional embedding model identifier | [optional] [default to 'default']

## Example

```python
from hermes_client.models.embed_text_request import EmbedTextRequest

# TODO update the JSON string below
json = "{}"
# create an instance of EmbedTextRequest from a JSON string
embed_text_request_instance = EmbedTextRequest.from_json(json)
# print the JSON string representation of the object
print(EmbedTextRequest.to_json())

# convert the object into a dict
embed_text_request_dict = embed_text_request_instance.to_dict()
# create an instance of EmbedTextRequest from a dict
embed_text_request_from_dict = EmbedTextRequest.from_dict(embed_text_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


