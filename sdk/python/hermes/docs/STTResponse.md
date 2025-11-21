# STTResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** | Transcribed text | 
**confidence** | **float** | Confidence score (0.0 to 1.0) | 

## Example

```python
from logos_hermes_sdk.models.stt_response import STTResponse

# TODO update the JSON string below
json = "{}"
# create an instance of STTResponse from a JSON string
stt_response_instance = STTResponse.from_json(json)
# print the JSON string representation of the object
print(STTResponse.to_json())

# convert the object into a dict
stt_response_dict = stt_response_instance.to_dict()
# create an instance of STTResponse from a dict
stt_response_from_dict = STTResponse.from_dict(stt_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


