# LLMUsage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prompt_tokens** | **int** | Prompt token count. | 
**completion_tokens** | **int** | Completion token count. | 
**total_tokens** | **int** | Total token count. | 

## Example

```python
from logos_hermes_sdk.models.llm_usage import LLMUsage

# TODO update the JSON string below
json = "{}"
# create an instance of LLMUsage from a JSON string
llm_usage_instance = LLMUsage.from_json(json)
# print the JSON string representation of the object
print(LLMUsage.to_json())

# convert the object into a dict
llm_usage_dict = llm_usage_instance.to_dict()
# create an instance of LLMUsage from a dict
llm_usage_from_dict = LLMUsage.from_dict(llm_usage_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


