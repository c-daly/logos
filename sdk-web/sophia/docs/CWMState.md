
# CWMState

Unified causal world model state envelope (thin transport wrapper). All meaningful metadata (provenance) lives in `data`, not on the envelope. This is a breaking change from the previous schema which had provenance on the envelope. 

## Properties

Name | Type
------------ | -------------
`stateId` | string
`modelType` | string
`timestamp` | Date
`data` | { [key: string]: any; }

## Example

```typescript
import type { CWMState } from '@logos/sophia-sdk'

// TODO: Update the object below with actual values
const example = {
  "stateId": null,
  "modelType": null,
  "timestamp": null,
  "data": null,
} satisfies CWMState

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as CWMState
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


