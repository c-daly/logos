
# RunSimulation200Response


## Properties

Name | Type
------------ | -------------
`simulationId` | string
`imaginedStates` | [Array&lt;CWMState&gt;](CWMState.md)
`predictedOutcomes` | [Array&lt;RunSimulation200ResponsePredictedOutcomesInner&gt;](RunSimulation200ResponsePredictedOutcomesInner.md)
`metadata` | [RunSimulation200ResponseMetadata](RunSimulation200ResponseMetadata.md)

## Example

```typescript
import type { RunSimulation200Response } from '@logos/sophia-client'

// TODO: Update the object below with actual values
const example = {
  "simulationId": null,
  "imaginedStates": null,
  "predictedOutcomes": null,
  "metadata": null,
} satisfies RunSimulation200Response

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as RunSimulation200Response
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


