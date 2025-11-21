
# SimpleNLPResponse


## Properties

Name | Type
------------ | -------------
`tokens` | Array&lt;string&gt;
`posTags` | [Array&lt;POSTag&gt;](POSTag.md)
`lemmas` | Array&lt;string&gt;
`entities` | [Array&lt;Entity&gt;](Entity.md)

## Example

```typescript
import type { SimpleNLPResponse } from '@logos/hermes-sdk'

// TODO: Update the object below with actual values
const example = {
  "tokens": null,
  "posTags": null,
  "lemmas": null,
  "entities": null,
} satisfies SimpleNLPResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SimpleNLPResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


