"""OpenRouter provider implementation using OpenAI-compatible API."""

import logging
from typing import Any, AsyncIterator, Dict, List

from easy_dataset.llm.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class OpenRouterProvider(OpenAIProvider):
    """
    OpenRouter provider implementation.
    
    OpenRouter provides access to 100+ models through a unified OpenAI-compatible API.
    This implementation extends OpenAIProvider since OpenRouter uses the same API format.
    
    Supports:
    - Multiple models from various providers
    - Streaming and non-streaming completions
    - Vision models (if supported by selected model)
    - Unified interface across all models
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenRouter provider.
        
        Args:
            config: Configuration dictionary
        """
        # Set default endpoint if not provided
        if not config.get("endpoint"):
            config["endpoint"] = "https://openrouter.ai/api/v1"
        
        # Initialize using OpenAI provider (OpenRouter is OpenAI-compatible)
        super().__init__(config)
        
        # Override reasoning model detection for OpenRouter
        # OpenRouter doesn't use the same reasoning model naming
        self.is_reasoning_model = False
        
        logger.info(f"Initialized OpenRouter provider with model: {self.model}")

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a chat completion using OpenRouter API.
        
        OpenRouter uses OpenAI-compatible API, so we can use the parent implementation.
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters to override defaults
            
        Returns:
            Dictionary containing response data
        """
        # Use parent OpenAI implementation
        return await super().chat(messages, **kwargs)

    async def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate a streaming chat completion using OpenRouter API.
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters to override defaults
            
        Yields:
            String chunks of the generated response
        """
        # Use parent OpenAI implementation
        async for chunk in super().chat_stream(messages, **kwargs):
            yield chunk

    async def vision_chat(
        self,
        prompt: str,
        image_data: str,
        mime_type: str = "image/jpeg",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a chat completion with image input using vision models.
        
        Note: Vision support depends on the selected model.
        Make sure to use a vision-capable model (e.g., gpt-4-vision-preview).
        
        Args:
            prompt: Text prompt/question
            image_data: Base64 encoded image data or data URL
            mime_type: MIME type of the image
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing the response
        """
        # Use parent OpenAI implementation
        return await super().vision_chat(prompt, image_data, mime_type, **kwargs)
