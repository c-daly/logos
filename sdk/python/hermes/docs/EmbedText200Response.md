# EmbedText200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**embedding** | **List[float]** | Vector embedding | [optional] 
**dimension** | **int** | Embedding dimension | [optional] 
**model** | **str** | Model used for embedding | [optional] 

## Example

```python
from logos_hermes_sdk.models.embed_text200_response import EmbedText200Response

# TODO update the JSON string below
json = "{}"
# create an instance of EmbedText200Response from a JSON string
embed_text200_response_instance = EmbedText200Response.from_json(json)
# print the JSON string representation of the object
print(EmbedText200Response.to_json())

# convert the object into a dict
embed_text200_response_dict = embed_text200_response_instance.to_dict()
# create an instance of EmbedText200Response from a dict
embed_text200_response_from_dict = EmbedText200Response.from_dict(embed_text200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


