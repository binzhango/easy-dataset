"""Test that all LLM modules can be imported successfully."""

import pytest


def test_base_provider_import():
    """Test that BaseLLMProvider can be imported."""
    from easy_dataset.llm.base import BaseLLMProvider
    assert BaseLLMProvider is not None


def test_service_import():
    """Test that LLMService can be imported."""
    from easy_dataset.llm.service import LLMService
    assert LLMService is not None


def test_openai_provider_import():
    """Test that OpenAIProvider can be imported."""
    from easy_dataset.llm.providers.openai_provider import OpenAIProvider
    assert OpenAIProvider is not None


def test_ollama_provider_import():
    """Test that OllamaProvider can be imported."""
    from easy_dataset.llm.providers.ollama_provider import OllamaProvider
    assert OllamaProvider is not None


def test_openrouter_provider_import():
    """Test that OpenRouterProvider can be imported."""
    from easy_dataset.llm.providers.openrouter_provider import OpenRouterProvider
    assert OpenRouterProvider is not None


def test_litellm_provider_import():
    """Test that LiteLLMProvider can be imported (may warn if not installed)."""
    from easy_dataset.llm.providers.litellm_provider import LiteLLMProvider
    assert LiteLLMProvider is not None


def test_gemini_provider_import():
    """Test that GeminiProvider can be imported (may warn if not installed)."""
    from easy_dataset.llm.providers.gemini_provider import GeminiProvider
    assert GeminiProvider is not None


def test_module_exports():
    """Test that main module exports are available."""
    from easy_dataset.llm import (
        BaseLLMProvider,
        LLMService,
        OpenAIProvider,
        OllamaProvider,
        OpenRouterProvider,
        LiteLLMProvider,
        GeminiProvider,
    )
    
    assert BaseLLMProvider is not None
    assert LLMService is not None
    assert OpenAIProvider is not None
    assert OllamaProvider is not None
    assert OpenRouterProvider is not None
    assert LiteLLMProvider is not None
    assert GeminiProvider is not None


def test_service_provider_map():
    """Test that LLMService has correct provider mapping."""
    from easy_dataset.llm.service import LLMService
    
    service = LLMService()
    
    # Check that all expected providers are in the map
    expected_providers = [
        "openai",
        "ollama",
        "openrouter",
        "litellm",
        "gemini",
        "siliconflow",
        "deepseek",
        "zhipu",
        "alibailian",
    ]
    
    for provider in expected_providers:
        assert provider in service.PROVIDER_MAP


def test_service_list_providers():
    """Test that service can list supported providers."""
    from easy_dataset.llm.service import LLMService
    
    service = LLMService()
    providers = service.list_supported_providers()
    
    assert isinstance(providers, list)
    assert len(providers) > 0
    assert "openai" in providers
    assert "ollama" in providers


def test_base_provider_config():
    """Test that BaseLLMProvider accepts configuration."""
    from easy_dataset.llm.base import BaseLLMProvider
    
    # Create a concrete implementation for testing
    class TestProvider(BaseLLMProvider):
        async def chat(self, messages, **kwargs):
            return {"text": "test"}
        
        async def chat_stream(self, messages, **kwargs):
            yield "test"
    
    config = {
        "provider": "test",
        "endpoint": "http://test.com",
        "api_key": "test-key",
        "model": "test-model",
        "temperature": 0.8,
        "max_tokens": 2000,
        "top_p": 0.95,
    }
    
    provider = TestProvider(config)
    
    assert provider.endpoint == "http://test.com"
    assert provider.api_key == "test-key"
    assert provider.model == "test-model"
    assert provider.temperature == 0.8
    assert provider.max_tokens == 2000
    assert provider.top_p == 0.95


def test_service_create_provider():
    """Test that service can create providers."""
    from easy_dataset.llm.service import LLMService
    from easy_dataset.llm.providers.openai_provider import OpenAIProvider
    
    service = LLMService()
    
    config = {
        "provider": "openai",
        "api_key": "test-key",
        "model": "gpt-4",
    }
    
    provider = service.create_provider(config)
    
    assert isinstance(provider, OpenAIProvider)
    assert provider.model == "gpt-4"


def test_service_unsupported_provider():
    """Test that service raises error for unsupported provider."""
    from easy_dataset.llm.service import LLMService
    
    service = LLMService()
    
    config = {
        "provider": "unsupported-provider",
        "model": "test",
    }
    
    with pytest.raises(ValueError, match="Unsupported provider"):
        service.create_provider(config)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
