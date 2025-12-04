# LLM Integration Layer

This document describes the LLM integration layer for Easy Dataset, which provides unified access to multiple LLM providers.

## Overview

The LLM integration layer provides:

- **Unified Interface**: Single API for all LLM providers
- **Multiple Providers**: Support for OpenAI, Ollama, OpenRouter, LiteLLM, and Gemini
- **Streaming Support**: Both regular and streaming completions
- **Vision Models**: Support for multimodal inputs (text + images)
- **Retry Logic**: Automatic retry with exponential backoff
- **Chain-of-Thought**: Extraction of reasoning chains from responses

## Supported Providers

### 1. OpenAI
- **Models**: GPT-3.5-turbo, GPT-4, GPT-4-turbo, GPT-4o, o1
- **Features**: Streaming, vision, reasoning models
- **Installation**: `pip install openai`

### 2. Ollama
- **Models**: Llama2, Mistral, and other local models
- **Features**: Local inference, model listing, streaming
- **Installation**: Install Ollama from https://ollama.ai

### 3. OpenRouter
- **Models**: 100+ models from various providers
- **Features**: Unified API, streaming, vision (model-dependent)
- **Installation**: Uses OpenAI SDK (included)

### 4. LiteLLM
- **Models**: 100+ providers through unified interface
- **Features**: Fallback, load balancing, streaming
- **Installation**: `pip install litellm`

### 5. Google Gemini
- **Models**: Gemini Pro, Gemini Pro Vision
- **Features**: Multimodal, streaming, Google authentication
- **Installation**: `pip install google-generativeai`

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LLMService                            │
│  (Orchestrator for managing providers and configs)      │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
┌────────▼────────┐    ┌────────▼────────┐
│ BaseLLMProvider │    │  Provider Cache │
│  (Abstract Base)│    │                 │
└────────┬────────┘    └─────────────────┘
         │
    ┌────┴────┬────────┬──────────┬─────────┐
    │         │        │          │         │
┌───▼───┐ ┌──▼──┐ ┌───▼────┐ ┌───▼───┐ ┌──▼────┐
│OpenAI │ │Ollama│ │OpenRouter│ │LiteLLM│ │Gemini│
└───────┘ └─────┘ └────────┘ └───────┘ └───────┘
```

## Usage

### Basic Usage

```python
from easy_dataset.llm import LLMService

# Create service
service = LLMService()

# Configure provider
config = {
    "provider": "openai",
    "api_key": "your-api-key",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000,
}

# Simple chat
messages = [
    {"role": "user", "content": "What is Python?"}
]

response = await service.chat(config, messages)
print(response['text'])
```

### Streaming Responses

```python
# Stream response chunks
async for chunk in service.chat_stream(config, messages):
    print(chunk, end="", flush=True)
```

### Vision/Multimodal Input

```python
# Chat with image
response = await service.vision_chat(
    config=config,
    prompt="What do you see in this image?",
    image_data="data:image/jpeg;base64,...",
    mime_type="image/jpeg"
)
```

### Using Different Providers

#### OpenAI
```python
config = {
    "provider": "openai",
    "api_key": "sk-...",
    "model": "gpt-4",
}
```

#### Ollama (Local)
```python
config = {
    "provider": "ollama",
    "endpoint": "http://localhost:11434",
    "model": "llama2",
}
```

#### OpenRouter
```python
config = {
    "provider": "openrouter",
    "api_key": "sk-or-...",
    "model": "anthropic/claude-2",
}
```

#### LiteLLM
```python
config = {
    "provider": "litellm",
    "api_key": "your-key",
    "model": "claude-2",
    "fallback_models": ["gpt-4", "gpt-3.5-turbo"],
}
```

#### Gemini
```python
config = {
    "provider": "gemini",
    "api_key": "your-google-api-key",
    "model": "gemini-pro",
}
```

### Direct Provider Usage

```python
from easy_dataset.llm import OpenAIProvider

# Create provider directly
provider = OpenAIProvider({
    "api_key": "sk-...",
    "model": "gpt-4",
    "temperature": 0.7,
})

# Chat
response = await provider.chat(messages)
```

### Chain-of-Thought Extraction

```python
# Get response with reasoning
response = await service.chat(config, messages)

# Extract answer and chain-of-thought
result = service.extract_answer_and_cot(response)
print(f"Answer: {result['answer']}")
print(f"Reasoning: {result['cot']}")
```

### Database Configuration

```python
from sqlalchemy.orm import Session

# Create service with database session
service = LLMService(db_session=session)

# Load config from database
config = service.load_config_from_db(model_config_id="abc123")

# Use loaded config
response = await service.chat(config, messages)

# Or use config ID directly
response = await service.chat_with_config_id(
    model_config_id="abc123",
    messages=messages
)
```

## Configuration Options

### Common Parameters

All providers support these parameters:

- `provider` (str): Provider name (openai, ollama, etc.)
- `endpoint` (str): API endpoint URL (optional for some providers)
- `api_key` (str): API key for authentication
- `model` (str): Model name to use
- `temperature` (float): Temperature parameter (default: 0.7)
- `max_tokens` (int): Maximum tokens to generate (default: 8192)
- `top_p` (float): Top-p sampling parameter (default: 0.9)
- `top_k` (int): Top-k sampling parameter (optional)

### Retry Configuration

- `max_retries` (int): Maximum retry attempts (default: 3)
- `initial_retry_delay` (float): Initial delay in seconds (default: 1.0)
- `max_retry_delay` (float): Maximum delay in seconds (default: 60.0)
- `retry_multiplier` (float): Backoff multiplier (default: 2.0)

## Response Format

All providers return responses in this format:

```python
{
    "text": "Generated text response",
    "reasoning": "Chain-of-thought reasoning (if available)",
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 50,
        "total_tokens": 60
    },
    "response": {...}  # Raw provider response
}
```

## Error Handling

The integration layer includes automatic retry logic with exponential backoff:

```python
# Retry configuration
config = {
    "provider": "openai",
    "api_key": "sk-...",
    "model": "gpt-4",
    "max_retries": 3,
    "initial_retry_delay": 1.0,
    "retry_multiplier": 2.0,
}

# Automatic retry on transient failures
response = await service.chat(config, messages)
```

## Best Practices

1. **Use LLMService**: Use the service orchestrator instead of providers directly for better configuration management and caching.

2. **Cache Providers**: The service automatically caches provider instances. Clear cache when needed:
   ```python
   service.clear_cache()
   ```

3. **Handle Errors**: Wrap calls in try-except blocks:
   ```python
   try:
       response = await service.chat(config, messages)
   except Exception as e:
       logger.error(f"LLM call failed: {e}")
   ```

4. **Use Streaming**: For long responses, use streaming to improve user experience:
   ```python
   async for chunk in service.chat_stream(config, messages):
       # Process chunk immediately
       pass
   ```

5. **Vision Models**: Ensure you're using a vision-capable model for image inputs:
   - OpenAI: gpt-4-vision-preview, gpt-4o
   - Gemini: gemini-pro-vision
   - Check provider documentation for vision support

## Testing

See `examples/llm_usage_example.py` for comprehensive usage examples.

## Dependencies

Required:
- `openai>=1.0` - For OpenAI and OpenAI-compatible providers
- `httpx>=0.24` - For HTTP requests (Ollama)

Optional:
- `litellm>=1.0` - For LiteLLM provider
- `google-generativeai>=0.3` - For Gemini provider

Install all:
```bash
pip install openai httpx litellm google-generativeai
```

## Troubleshooting

### Connection Errors

If you get connection errors with Ollama:
- Ensure Ollama is running: `ollama serve`
- Check endpoint URL: `http://localhost:11434`
- Verify model is installed: `ollama list`

### API Key Errors

- Verify API key is correct
- Check API key has necessary permissions
- Ensure endpoint URL is correct for the provider

### Import Errors

If you get import errors for optional providers:
```bash
# Install missing dependencies
pip install litellm  # For LiteLLM
pip install google-generativeai  # For Gemini
```

## Future Enhancements

- [ ] Support for more providers (Anthropic, Cohere, etc.)
- [ ] Request/response caching
- [ ] Rate limiting
- [ ] Cost tracking
- [ ] Model performance metrics
- [ ] Automatic model selection based on task
