# logos_hermes_sdk.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**embed_text_embed_text_post**](DefaultApi.md#embed_text_embed_text_post) | **POST** /embed_text | Embed Text
[**health_health_get**](DefaultApi.md#health_health_get) | **GET** /health | Health
[**llm_generate_llm_post**](DefaultApi.md#llm_generate_llm_post) | **POST** /llm | Llm Generate
[**root_get**](DefaultApi.md#root_get) | **GET** / | Root
[**simple_nlp_simple_nlp_post**](DefaultApi.md#simple_nlp_simple_nlp_post) | **POST** /simple_nlp | Simple Nlp
[**speech_to_text_stt_post**](DefaultApi.md#speech_to_text_stt_post) | **POST** /stt | Speech To Text
[**text_to_speech_tts_post**](DefaultApi.md#text_to_speech_tts_post) | **POST** /tts | Text To Speech


# **embed_text_embed_text_post**
> EmbedTextResponse embed_text_embed_text_post(embed_text_request)

Embed Text

Generate vector embeddings for input text.

Args:
    request: EmbedTextRequest with text and model

Returns:
    EmbedTextResponse with embedding vector

### Example


```python
import logos_hermes_sdk
from logos_hermes_sdk.models.embed_text_request import EmbedTextRequest
from logos_hermes_sdk.models.embed_text_response import EmbedTextResponse
from logos_hermes_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = logos_hermes_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with logos_hermes_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logos_hermes_sdk.DefaultApi(api_client)
    embed_text_request = logos_hermes_sdk.EmbedTextRequest() # EmbedTextRequest | 

    try:
        # Embed Text
        api_response = api_instance.embed_text_embed_text_post(embed_text_request)
        print("The response of DefaultApi->embed_text_embed_text_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->embed_text_embed_text_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **embed_text_request** | [**EmbedTextRequest**](EmbedTextRequest.md)|  | 

### Return type

[**EmbedTextResponse**](EmbedTextResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **health_health_get**
> HealthResponse health_health_get()

Health

Health check endpoint with detailed service status.

Returns the overall health status and availability of ML services,
Milvus connectivity, and internal queue status.
This is useful for monitoring and integration with other LOGOS components.

### Example


```python
import logos_hermes_sdk
from logos_hermes_sdk.models.health_response import HealthResponse
from logos_hermes_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = logos_hermes_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with logos_hermes_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logos_hermes_sdk.DefaultApi(api_client)

    try:
        # Health
        api_response = api_instance.health_health_get()
        print("The response of DefaultApi->health_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->health_health_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**HealthResponse**](HealthResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **llm_generate_llm_post**
> LLMResponse llm_generate_llm_post(llm_request)

Llm Generate

Proxy language model completions through Hermes.

### Example


```python
import logos_hermes_sdk
from logos_hermes_sdk.models.llm_request import LLMRequest
from logos_hermes_sdk.models.llm_response import LLMResponse
from logos_hermes_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = logos_hermes_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with logos_hermes_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logos_hermes_sdk.DefaultApi(api_client)
    llm_request = logos_hermes_sdk.LLMRequest() # LLMRequest | 

    try:
        # Llm Generate
        api_response = api_instance.llm_generate_llm_post(llm_request)
        print("The response of DefaultApi->llm_generate_llm_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->llm_generate_llm_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **llm_request** | [**LLMRequest**](LLMRequest.md)|  | 

### Return type

[**LLMResponse**](LLMResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **root_get**
> Dict[str, object] root_get()

Root

Root endpoint with API information.

### Example


```python
import logos_hermes_sdk
from logos_hermes_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = logos_hermes_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with logos_hermes_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logos_hermes_sdk.DefaultApi(api_client)

    try:
        # Root
        api_response = api_instance.root_get()
        print("The response of DefaultApi->root_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->root_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**Dict[str, object]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **simple_nlp_simple_nlp_post**
> SimpleNLPResponse simple_nlp_simple_nlp_post(simple_nlp_request)

Simple Nlp

Perform basic NLP preprocessing.

Args:
    request: SimpleNLPRequest with text and operations

Returns:
    SimpleNLPResponse with requested NLP results

### Example


```python
import logos_hermes_sdk
from logos_hermes_sdk.models.simple_nlp_request import SimpleNLPRequest
from logos_hermes_sdk.models.simple_nlp_response import SimpleNLPResponse
from logos_hermes_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = logos_hermes_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with logos_hermes_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logos_hermes_sdk.DefaultApi(api_client)
    simple_nlp_request = logos_hermes_sdk.SimpleNLPRequest() # SimpleNLPRequest | 

    try:
        # Simple Nlp
        api_response = api_instance.simple_nlp_simple_nlp_post(simple_nlp_request)
        print("The response of DefaultApi->simple_nlp_simple_nlp_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->simple_nlp_simple_nlp_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **simple_nlp_request** | [**SimpleNLPRequest**](SimpleNLPRequest.md)|  | 

### Return type

[**SimpleNLPResponse**](SimpleNLPResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **speech_to_text_stt_post**
> STTResponse speech_to_text_stt_post(audio, language=language)

Speech To Text

Convert audio input to text transcription.

Args:
    audio: Audio file to transcribe
    language: Optional language hint (e.g., "en-US")

Returns:
    STTResponse with transcribed text and confidence score

### Example


```python
import logos_hermes_sdk
from logos_hermes_sdk.models.stt_response import STTResponse
from logos_hermes_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = logos_hermes_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with logos_hermes_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logos_hermes_sdk.DefaultApi(api_client)
    audio = None # bytearray | 
    language = 'en-US' # str |  (optional) (default to 'en-US')

    try:
        # Speech To Text
        api_response = api_instance.speech_to_text_stt_post(audio, language=language)
        print("The response of DefaultApi->speech_to_text_stt_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->speech_to_text_stt_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **audio** | **bytearray**|  | 
 **language** | **str**|  | [optional] [default to &#39;en-US&#39;]

### Return type

[**STTResponse**](STTResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **text_to_speech_tts_post**
> object text_to_speech_tts_post(tts_request)

Text To Speech

Convert text to synthesized speech audio.

Args:
    request: TTSRequest with text, voice, and language

Returns:
    Audio file in WAV format

### Example


```python
import logos_hermes_sdk
from logos_hermes_sdk.models.tts_request import TTSRequest
from logos_hermes_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = logos_hermes_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with logos_hermes_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logos_hermes_sdk.DefaultApi(api_client)
    tts_request = logos_hermes_sdk.TTSRequest() # TTSRequest | 

    try:
        # Text To Speech
        api_response = api_instance.text_to_speech_tts_post(tts_request)
        print("The response of DefaultApi->text_to_speech_tts_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->text_to_speech_tts_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tts_request** | [**TTSRequest**](TTSRequest.md)|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

