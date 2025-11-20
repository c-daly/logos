# TextToSpeechRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** | Text to synthesize | 
**voice** | **str** | Optional voice identifier | [optional] [default to 'default']
**language** | **str** | Language code (e.g., \&quot;en-US\&quot;) | [optional] [default to 'en-US']

## Example

```python
from hermes_client.models.text_to_speech_request import TextToSpeechRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TextToSpeechRequest from a JSON string
text_to_speech_request_instance = TextToSpeechRequest.from_json(json)
# print the JSON string representation of the object
print(TextToSpeechRequest.to_json())

# convert the object into a dict
text_to_speech_request_dict = text_to_speech_request_instance.to_dict()
# create an instance of TextToSpeechRequest from a dict
text_to_speech_request_from_dict = TextToSpeechRequest.from_dict(text_to_speech_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


