# SpeechToText200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** | Transcribed text | [optional] 
**confidence** | **float** | Confidence score (0.0 to 1.0) | [optional] 

## Example

```python
from logos_hermes_sdk.models.speech_to_text200_response import SpeechToText200Response

# TODO update the JSON string below
json = "{}"
# create an instance of SpeechToText200Response from a JSON string
speech_to_text200_response_instance = SpeechToText200Response.from_json(json)
# print the JSON string representation of the object
print(SpeechToText200Response.to_json())

# convert the object into a dict
speech_to_text200_response_dict = speech_to_text200_response_instance.to_dict()
# create an instance of SpeechToText200Response from a dict
speech_to_text200_response_from_dict = SpeechToText200Response.from_dict(speech_to_text200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


