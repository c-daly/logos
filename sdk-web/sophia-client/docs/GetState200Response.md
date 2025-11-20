
# GetState200Response


## Properties

Name | Type
------------ | -------------
`states` | [Array&lt;CWMState&gt;](CWMState.md)
`cursor` | string
`total` | number

## Example

```typescript
import type { GetState200Response } from '@logos/sophia-client'

// TODO: Update the object below with actual values
const example = {
  "states": null,
  "cursor": null,
  "total": null,
} satisfies GetState200Response

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as GetState200Response
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


