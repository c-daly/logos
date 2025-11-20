# GeneratePlan200ResponseCausalLinksInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**from_process** | **str** |  | [optional] 
**to_process** | **str** |  | [optional] 
**condition** | **str** |  | [optional] 

## Example

```python
from sophia_client.models.generate_plan200_response_causal_links_inner import GeneratePlan200ResponseCausalLinksInner

# TODO update the JSON string below
json = "{}"
# create an instance of GeneratePlan200ResponseCausalLinksInner from a JSON string
generate_plan200_response_causal_links_inner_instance = GeneratePlan200ResponseCausalLinksInner.from_json(json)
# print the JSON string representation of the object
print(GeneratePlan200ResponseCausalLinksInner.to_json())

# convert the object into a dict
generate_plan200_response_causal_links_inner_dict = generate_plan200_response_causal_links_inner_instance.to_dict()
# create an instance of GeneratePlan200ResponseCausalLinksInner from a dict
generate_plan200_response_causal_links_inner_from_dict = GeneratePlan200ResponseCausalLinksInner.from_dict(generate_plan200_response_causal_links_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


