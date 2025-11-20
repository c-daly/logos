# LLMMessage

Chat completion message payload.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role** | **str** | Role associated with the message. | 
**content** | **str** | Text content of the message. | 
**name** | **str** | Optional identifier for tool/function calls. | [optional] 

## Example

```python
from logos_hermes_sdk.models.llm_message import LLMMessage

# TODO update the JSON string below
json = "{}"
# create an instance of LLMMessage from a JSON string
llm_message_instance = LLMMessage.from_json(json)
# print the JSON string representation of the object
print(LLMMessage.to_json())

# convert the object into a dict
llm_message_dict = llm_message_instance.to_dict()
# create an instance of LLMMessage from a dict
llm_message_from_dict = LLMMessage.from_dict(llm_message_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


