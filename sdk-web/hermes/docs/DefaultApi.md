# DefaultApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**embedTextEmbedTextPost**](DefaultApi.md#embedtextembedtextpost) | **POST** /embed_text | Embed Text |
| [**healthHealthGet**](DefaultApi.md#healthhealthget) | **GET** /health | Health |
| [**llmGenerateLlmPost**](DefaultApi.md#llmgeneratellmpost) | **POST** /llm | Llm Generate |
| [**rootGet**](DefaultApi.md#rootget) | **GET** / | Root |
| [**simpleNlpSimpleNlpPost**](DefaultApi.md#simplenlpsimplenlppost) | **POST** /simple_nlp | Simple Nlp |
| [**speechToTextSttPost**](DefaultApi.md#speechtotextsttpost) | **POST** /stt | Speech To Text |
| [**textToSpeechTtsPost**](DefaultApi.md#texttospeechttspost) | **POST** /tts | Text To Speech |



## embedTextEmbedTextPost

> EmbedTextResponse embedTextEmbedTextPost(embedTextRequest)

Embed Text

Generate vector embeddings for input text.  Args:     request: EmbedTextRequest with text and model  Returns:     EmbedTextResponse with embedding vector

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '@logos/hermes-sdk';
import type { EmbedTextEmbedTextPostRequest } from '@logos/hermes-sdk';

async function example() {
  console.log("🚀 Testing @logos/hermes-sdk SDK...");
  const api = new DefaultApi();

  const body = {
    // EmbedTextRequest
    embedTextRequest: ...,
  } satisfies EmbedTextEmbedTextPostRequest;

  try {
    const data = await api.embedTextEmbedTextPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **embedTextRequest** | [EmbedTextRequest](EmbedTextRequest.md) |  | |

### Return type

[**EmbedTextResponse**](EmbedTextResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## healthHealthGet

> HealthResponse healthHealthGet()

Health

Health check endpoint with detailed service status.  Returns the overall health status and availability of ML services, Milvus connectivity, and internal queue status. This is useful for monitoring and integration with other LOGOS components.

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '@logos/hermes-sdk';
import type { HealthHealthGetRequest } from '@logos/hermes-sdk';

async function example() {
  console.log("🚀 Testing @logos/hermes-sdk SDK...");
  const api = new DefaultApi();

  try {
    const data = await api.healthHealthGet();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**HealthResponse**](HealthResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## llmGenerateLlmPost

> LLMResponse llmGenerateLlmPost(lLMRequest)

Llm Generate

Proxy language model completions through Hermes.

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '@logos/hermes-sdk';
import type { LlmGenerateLlmPostRequest } from '@logos/hermes-sdk';

async function example() {
  console.log("🚀 Testing @logos/hermes-sdk SDK...");
  const api = new DefaultApi();

  const body = {
    // LLMRequest
    lLMRequest: ...,
  } satisfies LlmGenerateLlmPostRequest;

  try {
    const data = await api.llmGenerateLlmPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **lLMRequest** | [LLMRequest](LLMRequest.md) |  | |

### Return type

[**LLMResponse**](LLMResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## rootGet

> { [key: string]: any; } rootGet()

Root

Root endpoint with API information.

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '@logos/hermes-sdk';
import type { RootGetRequest } from '@logos/hermes-sdk';

async function example() {
  console.log("🚀 Testing @logos/hermes-sdk SDK...");
  const api = new DefaultApi();

  try {
    const data = await api.rootGet();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## simpleNlpSimpleNlpPost

> SimpleNLPResponse simpleNlpSimpleNlpPost(simpleNLPRequest)

Simple Nlp

Perform basic NLP preprocessing.  Args:     request: SimpleNLPRequest with text and operations  Returns:     SimpleNLPResponse with requested NLP results

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '@logos/hermes-sdk';
import type { SimpleNlpSimpleNlpPostRequest } from '@logos/hermes-sdk';

async function example() {
  console.log("🚀 Testing @logos/hermes-sdk SDK...");
  const api = new DefaultApi();

  const body = {
    // SimpleNLPRequest
    simpleNLPRequest: ...,
  } satisfies SimpleNlpSimpleNlpPostRequest;

  try {
    const data = await api.simpleNlpSimpleNlpPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **simpleNLPRequest** | [SimpleNLPRequest](SimpleNLPRequest.md) |  | |

### Return type

[**SimpleNLPResponse**](SimpleNLPResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## speechToTextSttPost

> STTResponse speechToTextSttPost(audio, language)

Speech To Text

Convert audio input to text transcription.  Args:     audio: Audio file to transcribe     language: Optional language hint (e.g., \&quot;en-US\&quot;)  Returns:     STTResponse with transcribed text and confidence score

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '@logos/hermes-sdk';
import type { SpeechToTextSttPostRequest } from '@logos/hermes-sdk';

async function example() {
  console.log("🚀 Testing @logos/hermes-sdk SDK...");
  const api = new DefaultApi();

  const body = {
    // Blob
    audio: BINARY_DATA_HERE,
    // string (optional)
    language: language_example,
  } satisfies SpeechToTextSttPostRequest;

  try {
    const data = await api.speechToTextSttPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **audio** | `Blob` |  | [Defaults to `undefined`] |
| **language** | `string` |  | [Optional] [Defaults to `&#39;en-US&#39;`] |

### Return type

[**STTResponse**](STTResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `multipart/form-data`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## textToSpeechTtsPost

> any textToSpeechTtsPost(tTSRequest)

Text To Speech

Convert text to synthesized speech audio.  Args:     request: TTSRequest with text, voice, and language  Returns:     Audio file in WAV format

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '@logos/hermes-sdk';
import type { TextToSpeechTtsPostRequest } from '@logos/hermes-sdk';

async function example() {
  console.log("🚀 Testing @logos/hermes-sdk SDK...");
  const api = new DefaultApi();

  const body = {
    // TTSRequest
    tTSRequest: ...,
  } satisfies TextToSpeechTtsPostRequest;

  try {
    const data = await api.textToSpeechTtsPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **tTSRequest** | [TTSRequest](TTSRequest.md) |  | |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

