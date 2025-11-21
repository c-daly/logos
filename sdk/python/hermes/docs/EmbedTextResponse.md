# EmbedTextResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**embedding** | **List[float]** | Vector embedding | 
**dimension** | **int** | Embedding dimension | 
**model** | **str** | Model used for embedding | 
**embedding_id** | **str** | Unique identifier for this embedding | 

## Example

```python
from logos_hermes_sdk.models.embed_text_response import EmbedTextResponse

# TODO update the JSON string below
json = "{}"
# create an instance of EmbedTextResponse from a JSON string
embed_text_response_instance = EmbedTextResponse.from_json(json)
# print the JSON string representation of the object
print(EmbedTextResponse.to_json())

# convert the object into a dict
embed_text_response_dict = embed_text_response_instance.to_dict()
# create an instance of EmbedTextResponse from a dict
embed_text_response_from_dict = EmbedTextResponse.from_dict(embed_text_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


