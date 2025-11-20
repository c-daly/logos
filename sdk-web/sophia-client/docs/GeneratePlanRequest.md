
# GeneratePlanRequest


## Properties

Name | Type
------------ | -------------
`goal` | string
`goalState` | [GeneratePlanRequestGoalState](GeneratePlanRequestGoalState.md)
`context` | { [key: string]: any; }

## Example

```typescript
import type { GeneratePlanRequest } from '@logos/sophia-client'

// TODO: Update the object below with actual values
const example = {
  "goal": null,
  "goalState": null,
  "context": null,
} satisfies GeneratePlanRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as GeneratePlanRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


