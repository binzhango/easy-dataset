"""LLM service orchestrator for managing providers and configurations."""

import logging
from typing import Any, AsyncIterator, Dict, List, Optional, Type

from sqlalchemy.orm import Session

from easy_dataset.llm.base import BaseLLMProvider
from easy_dataset.llm.providers.openai_provider import OpenAIProvider
from easy_dataset.llm.providers.ollama_provider import OllamaProvider
from easy_dataset.llm.providers.openrouter_provider import OpenRouterProvider
from easy_dataset.llm.providers.litellm_provider import LiteLLMProvider
from easy_dataset.llm.providers.gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM service orchestrator.
    
    Manages LLM providers and configurations:
    - Loads provider configuration from database
    - Creates appropriate provider instances
    - Handles provider selection based on model config
    - Extracts thinking chains and answers from responses
    """

    # Provider class mapping
    PROVIDER_MAP: Dict[str, Type[BaseLLMProvider]] = {
        "openai": OpenAIProvider,
        "ollama": OllamaProvider,
        "openrouter": OpenRouterProvider,
        "litellm": LiteLLMProvider,
        "gemini": GeminiProvider,
        # Aliases for compatibility
        "siliconflow": OpenAIProvider,  # OpenAI-compatible
        "deepseek": OpenAIProvider,     # OpenAI-compatible
        "zhipu": OpenAIProvider,        # OpenAI-compatible (GLM models)
        "alibailian": OpenAIProvider,   # OpenAI-compatible
    }

    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize LLM service.
        
        Args:
            db_session: Optional database session for loading configurations
        """
        self.db_session = db_session
        self._provider_cache: Dict[str, BaseLLMProvider] = {}

    def create_provider(
        self,
        config: Dict[str, Any]
    ) -> BaseLLMProvider:
        """
        Create an LLM provider instance based on configuration.
        
        Args:
            config: Configuration dictionary containing:
                - provider: Provider name (openai, ollama, etc.)
                - endpoint: API endpoint URL
                - api_key: API key for authentication
                - model: Model name
                - temperature: Temperature parameter
                - max_tokens: Maximum tokens
                - top_p: Top-p parameter
                - top_k: Top-k parameter (optional)
                
        Returns:
            Initialized provider instance
            
        Raises:
            ValueError: If provider is not supported
        """
        provider_name = config.get("provider", "openai").lower()
        
        # Get provider class
        provider_class = self.PROVIDER_MAP.get(provider_name)
        
        if not provider_class:
            raise ValueError(
                f"Unsupported provider: {provider_name}. "
                f"Supported providers: {', '.join(self.PROVIDER_MAP.keys())}"
            )
        
        # Create and return provider instance
        logger.info(f"Creating {provider_name} provider with model: {config.get('model')}")
        return provider_class(config)

    def get_or_create_provider(
        self,
        config: Dict[str, Any],
        cache_key: Optional[str] = None
    ) -> BaseLLMProvider:
        """
        Get cached provider or create new one.
        
        Args:
            config: Provider configuration
            cache_key: Optional cache key (defaults to provider_model combination)
            
        Returns:
            Provider instance
        """
        # Generate cache key if not provided
        if cache_key is None:
            provider = config.get("provider", "openai")
            model = config.get("model", "default")
            cache_key = f"{provider}:{model}"
        
        # Check cache
        if cache_key in self._provider_cache:
            logger.debug(f"Using cached provider: {cache_key}")
            return self._provider_cache[cache_key]
        
        # Create new provider
        provider = self.create_provider(config)
        
        # Cache it
        self._provider_cache[cache_key] = provider
        
        return provider

    async def chat(
        self,
        config: Dict[str, Any],
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a chat completion using configured provider.
        
        Args:
            config: Provider configuration
            messages: List of message dictionaries
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing response data
        """
        provider = self.get_or_create_provider(config)
        return await provider.chat(messages, **kwargs)

    async def chat_stream(
        self,
        config: Dict[str, Any],
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate a streaming chat completion using configured provider.
        
        Args:
            config: Provider configuration
            messages: List of message dictionaries
            **kwargs: Additional parameters
            
        Yields:
            String chunks of the generated response
        """
        provider = self.get_or_create_provider(config)
        async for chunk in provider.chat_stream(messages, **kwargs):
            yield chunk

    async def vision_chat(
        self,
        config: Dict[str, Any],
        prompt: str,
        image_data: str,
        mime_type: str = "image/jpeg",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a chat completion with image input.
        
        Args:
            config: Provider configuration
            prompt: Text prompt/question
            image_data: Base64 encoded image data or data URL
            mime_type: MIME type of the image
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing the response
        """
        provider = self.get_or_create_provider(config)
        return await provider.vision_chat(prompt, image_data, mime_type, **kwargs)

    def extract_answer_and_cot(
        self,
        response: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Extract answer and chain-of-thought from LLM response.
        
        This is a convenience method that wraps the base provider's
        extraction logic.
        
        Args:
            response: Response dictionary from chat() method
            
        Returns:
            Dictionary with 'answer' and 'cot' keys
        """
        text = response.get("text", "")
        reasoning = response.get("reasoning", "")
        
        # Use a temporary provider instance for extraction
        # (any provider will work since the logic is in the base class)
        temp_provider = BaseLLMProvider({"provider": "temp"})
        return temp_provider._extract_thinking_and_answer(text, reasoning)

    async def get_response(
        self,
        config: Dict[str, Any],
        prompt: str,
        **kwargs
    ) -> str:
        """
        Get a simple text response from the LLM.
        
        Convenience method for single-turn conversations.
        
        Args:
            config: Provider configuration
            prompt: User prompt
            **kwargs: Additional parameters
            
        Returns:
            Generated text response
        """
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat(config, messages, **kwargs)
        return response.get("text", "")

    async def get_response_with_cot(
        self,
        config: Dict[str, Any],
        prompt: str,
        **kwargs
    ) -> Dict[str, str]:
        """
        Get response with chain-of-thought reasoning.
        
        Args:
            config: Provider configuration
            prompt: User prompt
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with 'answer' and 'cot' keys
        """
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat(config, messages, **kwargs)
        return self.extract_answer_and_cot(response)

    def load_config_from_db(
        self,
        model_config_id: str
    ) -> Dict[str, Any]:
        """
        Load provider configuration from database.
        
        Args:
            model_config_id: Model configuration ID
            
        Returns:
            Configuration dictionary
            
        Raises:
            ValueError: If database session is not available
            RuntimeError: If configuration not found
        """
        if not self.db_session:
            raise ValueError("Database session not available")
        
        # Import here to avoid circular dependency
        from easy_dataset.models.config import ModelConfig
        
        # Query configuration
        config = self.db_session.query(ModelConfig).filter(
            ModelConfig.id == model_config_id
        ).first()
        
        if not config:
            raise RuntimeError(f"Model configuration not found: {model_config_id}")
        
        # Convert to dictionary
        return {
            "provider": config.provider_id,
            "endpoint": config.endpoint,
            "api_key": config.api_key,
            "model": config.model_name,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
            "top_k": config.top_k,
        }

    async def chat_with_config_id(
        self,
        model_config_id: str,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion using database configuration.
        
        Args:
            model_config_id: Model configuration ID from database
            messages: List of message dictionaries
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing response data
        """
        config = self.load_config_from_db(model_config_id)
        return await self.chat(config, messages, **kwargs)

    def clear_cache(self):
        """Clear the provider cache."""
        self._provider_cache.clear()
        logger.info("Provider cache cleared")

    def list_supported_providers(self) -> List[str]:
        """
        Get list of supported provider names.
        
        Returns:
            List of provider names
        """
        return list(self.PROVIDER_MAP.keys())
