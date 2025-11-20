# logos_hermes_sdk.DefaultApi

All URIs are relative to *http://localhost:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**embed_text**](DefaultApi.md#embed_text) | **POST** /embed_text | Text Embedding Generation
[**llm_generate**](DefaultApi.md#llm_generate) | **POST** /llm | LLM Gateway
[**simple_nlp**](DefaultApi.md#simple_nlp) | **POST** /simple_nlp | Simple NLP Preprocessing
[**speech_to_text**](DefaultApi.md#speech_to_text) | **POST** /stt | Speech-to-Text
[**text_to_speech**](DefaultApi.md#text_to_speech) | **POST** /tts | Text-to-Speech


# **embed_text**
> EmbedText200Response embed_text(embed_text_request)

Text Embedding Generation

Generate vector embeddings for input text

### Example


```python
import logos_hermes_sdk
from logos_hermes_sdk.models.embed_text200_response import EmbedText200Response
from logos_hermes_sdk.models.embed_text_request import EmbedTextRequest
from logos_hermes_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = logos_hermes_sdk.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with logos_hermes_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logos_hermes_sdk.DefaultApi(api_client)
    embed_text_request = logos_hermes_sdk.EmbedTextRequest() # EmbedTextRequest | 

    try:
        # Text Embedding Generation
        api_response = api_instance.embed_text(embed_text_request)
        print("The response of DefaultApi->embed_text:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->embed_text: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **embed_text_request** | [**EmbedTextRequest**](EmbedTextRequest.md)|  | 

### Return type

[**EmbedText200Response**](EmbedText200Response.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Embedding generation successful |  -  |
**400** | Invalid request |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **llm_generate**
> LLMResponse llm_generate(llm_request)

LLM Gateway

Proxy chat/completion requests through the configured provider (OpenAI, local, or echo fallback).

### Example


```python
import logos_hermes_sdk
from logos_hermes_sdk.models.llm_request import LLMRequest
from logos_hermes_sdk.models.llm_response import LLMResponse
from logos_hermes_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = logos_hermes_sdk.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with logos_hermes_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logos_hermes_sdk.DefaultApi(api_client)
    llm_request = logos_hermes_sdk.LLMRequest() # LLMRequest | 

    try:
        # LLM Gateway
        api_response = api_instance.llm_generate(llm_request)
        print("The response of DefaultApi->llm_generate:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->llm_generate: %s\n" % e)
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
**200** | Completion generated successfully |  -  |
**400** | Invalid request (missing prompt/messages or schema violation) |  -  |
**502** | Provider returned an error response |  -  |
**503** | Provider not configured/available |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **simple_nlp**
> SimpleNlp200Response simple_nlp(simple_nlp_request)

Simple NLP Preprocessing

Perform basic NLP preprocessing (tokenization, POS tagging, etc.)

### Example


```python
import logos_hermes_sdk
from logos_hermes_sdk.models.simple_nlp200_response import SimpleNlp200Response
from logos_hermes_sdk.models.simple_nlp_request import SimpleNlpRequest
from logos_hermes_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = logos_hermes_sdk.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with logos_hermes_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logos_hermes_sdk.DefaultApi(api_client)
    simple_nlp_request = logos_hermes_sdk.SimpleNlpRequest() # SimpleNlpRequest | 

    try:
        # Simple NLP Preprocessing
        api_response = api_instance.simple_nlp(simple_nlp_request)
        print("The response of DefaultApi->simple_nlp:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->simple_nlp: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **simple_nlp_request** | [**SimpleNlpRequest**](SimpleNlpRequest.md)|  | 

### Return type

[**SimpleNlp200Response**](SimpleNlp200Response.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | NLP processing successful |  -  |
**400** | Invalid request |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **speech_to_text**
> SpeechToText200Response speech_to_text(audio, language=language)

Speech-to-Text

Convert audio input to text transcription

### Example


```python
import logos_hermes_sdk
from logos_hermes_sdk.models.speech_to_text200_response import SpeechToText200Response
from logos_hermes_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = logos_hermes_sdk.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with logos_hermes_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logos_hermes_sdk.DefaultApi(api_client)
    audio = None # bytearray | Audio file to transcribe
    language = 'en-US' # str | Optional language hint (e.g., \\\"en-US\\\") (optional) (default to 'en-US')

    try:
        # Speech-to-Text
        api_response = api_instance.speech_to_text(audio, language=language)
        print("The response of DefaultApi->speech_to_text:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->speech_to_text: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **audio** | **bytearray**| Audio file to transcribe | 
 **language** | **str**| Optional language hint (e.g., \\\&quot;en-US\\\&quot;) | [optional] [default to &#39;en-US&#39;]

### Return type

[**SpeechToText200Response**](SpeechToText200Response.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Transcription successful |  -  |
**400** | Invalid request (e.g., unsupported audio format) |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **text_to_speech**
> bytearray text_to_speech(text_to_speech_request)

Text-to-Speech

Convert text to synthesized speech audio

### Example


```python
import logos_hermes_sdk
from logos_hermes_sdk.models.text_to_speech_request import TextToSpeechRequest
from logos_hermes_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = logos_hermes_sdk.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with logos_hermes_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logos_hermes_sdk.DefaultApi(api_client)
    text_to_speech_request = logos_hermes_sdk.TextToSpeechRequest() # TextToSpeechRequest | 

    try:
        # Text-to-Speech
        api_response = api_instance.text_to_speech(text_to_speech_request)
        print("The response of DefaultApi->text_to_speech:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->text_to_speech: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **text_to_speech_request** | [**TextToSpeechRequest**](TextToSpeechRequest.md)|  | 

### Return type

**bytearray**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: audio/wav

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Speech synthesis successful |  -  |
**400** | Invalid request |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

