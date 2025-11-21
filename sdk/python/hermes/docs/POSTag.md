# POSTag


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**token** | **str** |  | 
**tag** | **str** |  | 

## Example

```python
from logos_hermes_sdk.models.pos_tag import POSTag

# TODO update the JSON string below
json = "{}"
# create an instance of POSTag from a JSON string
pos_tag_instance = POSTag.from_json(json)
# print the JSON string representation of the object
print(POSTag.to_json())

# convert the object into a dict
pos_tag_dict = pos_tag_instance.to_dict()
# create an instance of POSTag from a dict
pos_tag_from_dict = POSTag.from_dict(pos_tag_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


