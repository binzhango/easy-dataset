"""
Example usage of the LLM integration layer.

This example demonstrates:
1. Creating LLM providers directly
2. Using the LLM service orchestrator
3. Streaming responses
4. Vision/multimodal inputs
"""

import asyncio
from easy_dataset.llm import (
    LLMService,
    OpenAIProvider,
    OllamaProvider,
    OpenRouterProvider,
)


async def example_direct_provider():
    """Example: Using providers directly."""
    print("\n=== Example 1: Direct Provider Usage ===\n")
    
    # Create OpenAI provider
    openai_config = {
        "provider": "openai",
        "api_key": "your-api-key-here",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 1000,
    }
    
    provider = OpenAIProvider(openai_config)
    
    # Simple chat
    messages = [
        {"role": "user", "content": "What is the capital of France?"}
    ]
    
    response = await provider.chat(messages)
    print(f"Response: {response['text']}")
    print(f"Tokens used: {response['usage']['total_tokens']}")


async def example_streaming():
    """Example: Streaming responses."""
    print("\n=== Example 2: Streaming Responses ===\n")
    
    config = {
        "provider": "openai",
        "api_key": "your-api-key-here",
        "model": "gpt-3.5-turbo",
    }
    
    provider = OpenAIProvider(config)
    
    messages = [
        {"role": "user", "content": "Write a short poem about Python programming."}
    ]
    
    print("Streaming response:")
    async for chunk in provider.chat_stream(messages):
        print(chunk, end="", flush=True)
    print("\n")


async def example_llm_service():
    """Example: Using LLM service orchestrator."""
    print("\n=== Example 3: LLM Service Orchestrator ===\n")
    
    # Create service
    service = LLMService()
    
    # Configuration for OpenAI
    config = {
        "provider": "openai",
        "api_key": "your-api-key-here",
        "model": "gpt-4",
        "temperature": 0.7,
    }
    
    # Simple chat
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain async/await in Python."}
    ]
    
    response = await service.chat(config, messages)
    print(f"Response: {response['text']}")
    
    # Extract answer and chain-of-thought
    result = service.extract_answer_and_cot(response)
    print(f"\nAnswer: {result['answer']}")
    if result['cot']:
        print(f"Chain of thought: {result['cot']}")


async def example_vision():
    """Example: Vision/multimodal input."""
    print("\n=== Example 4: Vision Input ===\n")
    
    config = {
        "provider": "openai",
        "api_key": "your-api-key-here",
        "model": "gpt-4-vision-preview",
    }
    
    provider = OpenAIProvider(config)
    
    # Base64 encoded image (example - replace with actual image data)
    image_data = "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
    
    response = await provider.vision_chat(
        prompt="What do you see in this image?",
        image_data=image_data,
        mime_type="image/jpeg"
    )
    
    print(f"Vision response: {response['text']}")


async def example_ollama():
    """Example: Using Ollama for local models."""
    print("\n=== Example 5: Ollama Local Models ===\n")
    
    config = {
        "provider": "ollama",
        "endpoint": "http://localhost:11434",
        "model": "llama2",
        "temperature": 0.7,
    }
    
    provider = OllamaProvider(config)
    
    # List available models
    models = await provider.list_models()
    print(f"Available models: {[m['name'] for m in models]}")
    
    # Chat with local model
    messages = [
        {"role": "user", "content": "Hello! How are you?"}
    ]
    
    response = await provider.chat(messages)
    print(f"Response: {response['text']}")


async def example_multiple_providers():
    """Example: Using multiple providers with service."""
    print("\n=== Example 6: Multiple Providers ===\n")
    
    service = LLMService()
    
    # Different provider configurations
    providers = [
        {
            "name": "OpenAI GPT-4",
            "config": {
                "provider": "openai",
                "api_key": "your-openai-key",
                "model": "gpt-4",
            }
        },
        {
            "name": "Ollama Llama2",
            "config": {
                "provider": "ollama",
                "endpoint": "http://localhost:11434",
                "model": "llama2",
            }
        },
        {
            "name": "OpenRouter Claude",
            "config": {
                "provider": "openrouter",
                "api_key": "your-openrouter-key",
                "model": "anthropic/claude-2",
            }
        }
    ]
    
    prompt = "What is 2+2?"
    
    for provider_info in providers:
        print(f"\nTesting {provider_info['name']}:")
        try:
            response = await service.get_response(
                provider_info['config'],
                prompt
            )
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")


async def example_with_retry():
    """Example: Automatic retry with exponential backoff."""
    print("\n=== Example 7: Retry Logic ===\n")
    
    config = {
        "provider": "openai",
        "api_key": "your-api-key-here",
        "model": "gpt-3.5-turbo",
        "max_retries": 3,
        "initial_retry_delay": 1.0,
        "retry_multiplier": 2.0,
    }
    
    provider = OpenAIProvider(config)
    
    messages = [
        {"role": "user", "content": "Hello!"}
    ]
    
    # The provider will automatically retry on transient failures
    response = await provider.chat(messages)
    print(f"Response: {response['text']}")


async def main():
    """Run all examples."""
    print("=" * 60)
    print("LLM Integration Layer Examples")
    print("=" * 60)
    
    # Note: These examples require valid API keys
    # Uncomment the examples you want to run
    
    # await example_direct_provider()
    # await example_streaming()
    # await example_llm_service()
    # await example_vision()
    # await example_ollama()
    # await example_multiple_providers()
    # await example_with_retry()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
