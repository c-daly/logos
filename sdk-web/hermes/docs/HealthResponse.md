
# HealthResponse


## Properties

Name | Type
------------ | -------------
`status` | string
`version` | string
`services` | { [key: string]: string; }
`milvus` | { [key: string]: any; }
`queue` | { [key: string]: any; }
`llm` | { [key: string]: any; }

## Example

```typescript
import type { HealthResponse } from '@logos/hermes-sdk'

// TODO: Update the object below with actual values
const example = {
  "status": null,
  "version": null,
  "services": null,
  "milvus": null,
  "queue": null,
  "llm": null,
} satisfies HealthResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as HealthResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


