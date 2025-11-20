
# GetHealth200Response


## Properties

Name | Type
------------ | -------------
`status` | string
`neo4j` | [GetHealth200ResponseNeo4j](GetHealth200ResponseNeo4j.md)
`milvus` | [GetHealth200ResponseMilvus](GetHealth200ResponseMilvus.md)
`timestamp` | Date

## Example

```typescript
import type { GetHealth200Response } from '@logos/sophia-client'

// TODO: Update the object below with actual values
const example = {
  "status": null,
  "neo4j": null,
  "milvus": null,
  "timestamp": null,
} satisfies GetHealth200Response

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as GetHealth200Response
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


