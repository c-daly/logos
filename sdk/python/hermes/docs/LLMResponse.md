# LLMResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Provider response identifier. | 
**provider** | **str** | Provider that generated the completion. | 
**model** | **str** | Model identifier returned by the provider. | 
**created** | **int** | Epoch timestamp when the completion was created. | 
**choices** | [**List[LLMChoice]**](LLMChoice.md) |  | 
**usage** | [**LLMUsage**](LLMUsage.md) |  | [optional] 
**raw** | **Dict[str, object]** | Raw provider payload for diagnostics. | [optional] 

## Example

```python
from logos_hermes_sdk.models.llm_response import LLMResponse

# TODO update the JSON string below
json = "{}"
# create an instance of LLMResponse from a JSON string
llm_response_instance = LLMResponse.from_json(json)
# print the JSON string representation of the object
print(LLMResponse.to_json())

# convert the object into a dict
llm_response_dict = llm_response_instance.to_dict()
# create an instance of LLMResponse from a dict
llm_response_from_dict = LLMResponse.from_dict(llm_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


