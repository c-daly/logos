
# RunSimulationRequestContext

Simulation context

## Properties

Name | Type
------------ | -------------
`entityIds` | Array&lt;string&gt;
`mediaSampleId` | string
`talosMetadata` | { [key: string]: any; }
`horizonSteps` | number

## Example

```typescript
import type { RunSimulationRequestContext } from '@logos/sophia-client'

// TODO: Update the object below with actual values
const example = {
  "entityIds": null,
  "mediaSampleId": null,
  "talosMetadata": null,
  "horizonSteps": null,
} satisfies RunSimulationRequestContext

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as RunSimulationRequestContext
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


