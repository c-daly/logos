# LLMChoice

Individual choice returned by the provider.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**index** | **int** | Choice index. | 
**message** | [**LLMMessage**](LLMMessage.md) |  | 
**finish_reason** | **str** | Reason generation finished (e.g., &#x60;stop&#x60;, &#x60;length&#x60;). | [optional] 

## Example

```python
from logos_hermes_sdk.models.llm_choice import LLMChoice

# TODO update the JSON string below
json = "{}"
# create an instance of LLMChoice from a JSON string
llm_choice_instance = LLMChoice.from_json(json)
# print the JSON string representation of the object
print(LLMChoice.to_json())

# convert the object into a dict
llm_choice_dict = llm_choice_instance.to_dict()
# create an instance of LLMChoice from a dict
llm_choice_from_dict = LLMChoice.from_dict(llm_choice_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


