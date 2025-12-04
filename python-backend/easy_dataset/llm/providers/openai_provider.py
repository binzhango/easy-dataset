"""OpenAI provider implementation using official OpenAI Python SDK."""

import logging
from typing import Any, AsyncIterator, Dict, List, Optional

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from easy_dataset.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI provider implementation.
    
    Supports:
    - GPT-3.5-turbo, GPT-4, GPT-4-turbo, GPT-4o models
    - Streaming and non-streaming completions
    - Vision models (GPT-4V, GPT-4o)
    - Chain-of-thought reasoning (o1 models)
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenAI provider.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        
        # Initialize OpenAI client
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.endpoint if self.endpoint else None
        )
        
        # Check if this is an o1 or reasoning model
        self.is_reasoning_model = any(
            self.model.startswith(prefix)
            for prefix in ["o1", "gpt-5", "gpt-4"]
        )

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a chat completion using OpenAI API.
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters to override defaults
            
        Returns:
            Dictionary containing response data
        """
        async def _make_request():
            # Convert messages to OpenAI format
            converted_messages = self._convert_messages(messages)
            
            # Prepare request parameters
            params = {
                "model": self.model,
                "messages": converted_messages,
            }
            
            # Add parameters based on model type
            if self.is_reasoning_model and self.endpoint and "api.openai.com" in self.endpoint:
                # For o1 and reasoning models, use max_completion_tokens
                params["max_completion_tokens"] = kwargs.get(
                    "max_tokens",
                    self.max_tokens
                )
                params["temperature"] = 1  # Fixed for reasoning models
            else:
                # For regular models
                params["max_tokens"] = kwargs.get("max_tokens", self.max_tokens)
                params["temperature"] = kwargs.get("temperature", self.temperature)
                params["top_p"] = kwargs.get("top_p", self.top_p)
            
            # Make API call
            response: ChatCompletion = await self.client.chat.completions.create(
                **params
            )
            
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
                "response": response.model_dump()
            }
        
        # Execute with retry logic
        return await self._retry_with_backoff(_make_request)

    async def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate a streaming chat completion using OpenAI API.
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters to override defaults
            
        Yields:
            String chunks of the generated response
        """
        async def _make_stream_request():
            # Convert messages to OpenAI format
            converted_messages = self._convert_messages(messages)
            
            # Prepare request parameters
            params = {
                "model": self.model,
                "messages": converted_messages,
                "stream": True,
            }
            
            # Add parameters based on model type
            if self.is_reasoning_model and self.endpoint and "api.openai.com" in self.endpoint:
                params["max_completion_tokens"] = kwargs.get(
                    "max_tokens",
                    self.max_tokens
                )
                params["temperature"] = 1
            else:
                params["max_tokens"] = kwargs.get("max_tokens", self.max_tokens)
                params["temperature"] = kwargs.get("temperature", self.temperature)
                params["top_p"] = kwargs.get("top_p", self.top_p)
            
            # Make streaming API call
            stream = await self.client.chat.completions.create(**params)
            
            return stream
        
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
            if delta.content:
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
