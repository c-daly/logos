
# GeneratePlan200Response


## Properties

Name | Type
------------ | -------------
`planId` | string
`processes` | [Array&lt;GeneratePlan200ResponseProcessesInner&gt;](GeneratePlan200ResponseProcessesInner.md)
`causalLinks` | [Array&lt;GeneratePlan200ResponseCausalLinksInner&gt;](GeneratePlan200ResponseCausalLinksInner.md)
`cwmStates` | [Array&lt;CWMState&gt;](CWMState.md)
`confidence` | number

## Example

```typescript
import type { GeneratePlan200Response } from '@logos/sophia-client'

// TODO: Update the object below with actual values
const example = {
  "planId": null,
  "processes": null,
  "causalLinks": null,
  "cwmStates": null,
  "confidence": null,
} satisfies GeneratePlan200Response

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as GeneratePlan200Response
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


