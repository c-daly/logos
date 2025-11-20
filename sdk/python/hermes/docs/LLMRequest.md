# LLMRequest

Request payload for Hermes LLM gateway.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prompt** | **str** | Shortcut for a single user message. | [optional] 
**messages** | [**List[LLMMessage]**](LLMMessage.md) | Conversation history to send to the provider. | [optional] 
**provider** | **str** | Override configured provider (e.g., &#x60;openai&#x60;, &#x60;echo&#x60;). | [optional] 
**model** | **str** | Override provider model identifier. | [optional] 
**temperature** | **float** | Sampling temperature passed to the provider. | [optional] [default to 0.7]
**max_tokens** | **int** | Optional maximum number of tokens to generate. | [optional] 
**metadata** | **Dict[str, object]** | Additional metadata to log with the request. | [optional] 

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


