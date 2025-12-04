"""LiteLLM provider implementation for unified access to 100+ LLM providers."""

import logging
from typing import Any, AsyncIterator, Dict, List, Optional

try:
    import litellm
    from litellm import acompletion, acompletion_stream
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(
        "litellm package not installed. Install with: pip install litellm"
    )

from easy_dataset.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class LiteLLMProvider(BaseLLMProvider):
    """
    LiteLLM provider implementation.
    
    LiteLLM provides unified access to 100+ LLM providers through a single interface.
    Supports automatic fallback and load balancing across providers.
    
    Supports:
    - 100+ models from various providers (OpenAI, Anthropic, Cohere, etc.)
    - Automatic fallback to alternative models
    - Load balancing across multiple API keys
    - Streaming and non-streaming completions
    - Vision models (if supported by selected model)
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize LiteLLM provider.
        
        Args:
            config: Configuration dictionary
        """
        if not LITELLM_AVAILABLE:
            raise ImportError(
                "litellm package is required for LiteLLMProvider. "
                "Install with: pip install litellm"
            )
        
        super().__init__(config)
        
        # Configure LiteLLM settings
        if self.endpoint:
            litellm.api_base = self.endpoint
        
        # Set API key if provided
        if self.api_key:
            litellm.api_key = self.api_key
        
        # Configure fallback models if provided
        self.fallback_models = config.get("fallback_models", [])
        
        # Configure load balancing if multiple API keys provided
        self.api_keys = config.get("api_keys", [self.api_key] if self.api_key else [])
        
        logger.info(f"Initialized LiteLLM provider with model: {self.model}")

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a chat completion using LiteLLM.
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters to override defaults
            
        Returns:
            Dictionary containing response data
        """
        async def _make_request():
            # Convert messages to LiteLLM format
            converted_messages = self._convert_messages(messages)
            
            # Prepare request parameters
            params = {
                "model": self.model,
                "messages": converted_messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "top_p": kwargs.get("top_p", self.top_p),
            }
            
            # Add API key if using multiple keys (load balancing)
            if len(self.api_keys) > 1:
                params["api_key"] = self.api_keys
            elif self.api_key:
                params["api_key"] = self.api_key
            
            # Add fallback models if configured
            if self.fallback_models:
                params["fallbacks"] = self.fallback_models
            
            # Make API call
            response = await acompletion(**params)
            
            # Extract response data
            choice = response.choices[0]
            message = choice.message
            
            # Extract text and reasoning
            text = message.content or ""
            reasoning = getattr(message, "reasoning_content", None) or ""
            
            # Extract thinking and answer
            result = self._extract_thinking_and_answer(text, reasoning)
            
            return {
                "text": result["answer"],
                "reasoning": result["cot"],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                "response": response.model_dump() if hasattr(response, "model_dump") else dict(response)
            }
        
        # Execute with retry logic
        return await self._retry_with_backoff(_make_request)

    async def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate a streaming chat completion using LiteLLM.
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters to override defaults
            
        Yields:
            String chunks of the generated response
        """
        async def _make_stream_request():
            # Convert messages to LiteLLM format
            converted_messages = self._convert_messages(messages)
            
            # Prepare request parameters
            params = {
                "model": self.model,
                "messages": converted_messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "top_p": kwargs.get("top_p", self.top_p),
                "stream": True,
            }
            
            # Add API key if using multiple keys (load balancing)
            if len(self.api_keys) > 1:
                params["api_key"] = self.api_keys
            elif self.api_key:
                params["api_key"] = self.api_key
            
            # Add fallback models if configured
            if self.fallback_models:
                params["fallbacks"] = self.fallback_models
            
            # Make streaming API call
            response = await acompletion(**params)
            
            return response
        
        # Execute with retry logic
        stream = await self._retry_with_backoff(_make_stream_request)
        
        # Track if we're in thinking mode
        is_thinking = False
        
        # Stream the response
        async for chunk in stream:
            if not chunk.choices:
                continue
            
            delta = chunk.choices[0].delta
            
            # Handle reasoning content (chain-of-thought)
            reasoning_content = getattr(delta, "reasoning_content", None)
            if reasoning_content:
                if not is_thinking:
                    yield "<think>"
                    is_thinking = True
                yield reasoning_content
            
            # Handle regular content
            if hasattr(delta, "content") and delta.content:
                if is_thinking:
                    yield "</think>"
                    is_thinking = False
                yield delta.content
        
        # Close thinking tag if still open
        if is_thinking:
            yield "</think>"

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
        Make sure to use a vision-capable model.
        
        Args:
            prompt: Text prompt/question
            image_data: Base64 encoded image data or data URL
            mime_type: MIME type of the image
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing the response
        """
        # Build vision messages
        messages = self._build_vision_messages(prompt, image_data, mime_type)
        
        # Use regular chat method with vision messages
        return await self.chat(messages, **kwargs)
