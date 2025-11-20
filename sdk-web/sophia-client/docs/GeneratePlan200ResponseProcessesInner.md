
# GeneratePlan200ResponseProcessesInner


## Properties

Name | Type
------------ | -------------
`processId` | string
`name` | string
`capabilityId` | string
`preconditions` | Array&lt;string&gt;
`effects` | Array&lt;string&gt;
`estimatedDuration` | number

## Example

```typescript
import type { GeneratePlan200ResponseProcessesInner } from '@logos/sophia-client'

// TODO: Update the object below with actual values
const example = {
  "processId": null,
  "name": null,
  "capabilityId": null,
  "preconditions": null,
  "effects": null,
  "estimatedDuration": null,
} satisfies GeneratePlan200ResponseProcessesInner

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as GeneratePlan200ResponseProcessesInner
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


