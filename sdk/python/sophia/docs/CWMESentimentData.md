# CWMESentimentData

Payload for CWM-E (persona/emotion) outputs.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sentiment** | **str** | e.g., confident, cautious | [optional] 
**confidence_delta** | **float** |  | [optional] 
**caution_delta** | **float** |  | [optional] 
**narrative** | **str** | Short diary-style reflection | [optional] 

## Example

```python
from logos_sophia_sdk.models.cwme_sentiment_data import CWMESentimentData

# TODO update the JSON string below
json = "{}"
# create an instance of CWMESentimentData from a JSON string
cwme_sentiment_data_instance = CWMESentimentData.from_json(json)
# print the JSON string representation of the object
print(CWMESentimentData.to_json())

# convert the object into a dict
cwme_sentiment_data_dict = cwme_sentiment_data_instance.to_dict()
# create an instance of CWMESentimentData from a dict
cwme_sentiment_data_from_dict = CWMESentimentData.from_dict(cwme_sentiment_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


