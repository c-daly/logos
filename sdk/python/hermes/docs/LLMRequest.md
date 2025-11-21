# LLMRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prompt** | **str** |  | [optional] 
**messages** | [**List[LLMMessage]**](LLMMessage.md) |  | [optional] 
**provider** | **str** |  | [optional] 
**model** | **str** |  | [optional] 
**temperature** | **float** |  | [optional] 
**max_tokens** | **int** |  | [optional] 
**metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from logos_hermes_sdk.models.llm_request import LLMRequest

# TODO update the JSON string below
json = "{}"
# create an instance of LLMRequest from a JSON string
llm_request_instance = LLMRequest.from_json(json)
# print the JSON string representation of the object
print(LLMRequest.to_json())

# convert the object into a dict
llm_request_dict = llm_request_instance.to_dict()
# create an instance of LLMRequest from a dict
llm_request_from_dict = LLMRequest.from_dict(llm_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


