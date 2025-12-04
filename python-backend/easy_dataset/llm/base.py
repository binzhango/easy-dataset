"""Base LLM provider interface with retry logic and exponential backoff."""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    Provides unified interface for chat completions with support for:
    - Regular chat completions
    - Streaming chat completions
    - Vision/multimodal inputs
    - Retry logic with exponential backoff
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the LLM provider.
        
        Args:
            config: Configuration dictionary containing:
                - endpoint: API endpoint URL
                - api_key: API key for authentication
                - model: Model name to use
                - temperature: Temperature parameter (default: 0.7)
                - max_tokens: Maximum tokens to generate (default: 8192)
                - top_p: Top-p sampling parameter (default: 0.9)
                - top_k: Top-k sampling parameter (optional)
        """
        self.endpoint = config.get("endpoint", "")
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "")
        self.provider = config.get("provider", "")
        
        # Model configuration parameters
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 8192)
        self.top_p = config.get("top_p", 0.9)
        self.top_k = config.get("top_k")
        
        # Retry configuration
        self.max_retries = config.get("max_retries", 3)
        self.initial_retry_delay = config.get("initial_retry_delay", 1.0)
        self.max_retry_delay = config.get("max_retry_delay", 60.0)
        self.retry_multiplier = config.get("retry_multiplier", 2.0)

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a chat completion.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters to override defaults
            
        Returns:
            Dictionary containing:
                - text: Generated text response
                - reasoning: Chain-of-thought reasoning (if available)
                - usage: Token usage information
                - response: Raw response from provider
        """
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate a streaming chat completion.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters to override defaults
            
        Yields:
            String chunks of the generated response
        """
        pass

    async def vision_chat(
        self,
        prompt: str,
        image_data: str,
        mime_type: str = "image/jpeg",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a chat completion with image input (vision models).
        
        Args:
            prompt: Text prompt/question
            image_data: Base64 encoded image data or data URL
            mime_type: MIME type of the image (default: image/jpeg)
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing the response (same format as chat())
            
        Raises:
            NotImplementedError: If vision is not supported by this provider
        """
        raise NotImplementedError(
            f"Vision chat not supported by {self.__class__.__name__}"
        )

    async def _retry_with_backoff(
        self,
        func,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a function with exponential backoff retry logic.
        
        Implements retry logic for transient failures:
        - Retries up to max_retries times
        - Uses exponential backoff between retries
        - Logs retry attempts
        
        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result from successful function execution
            
        Raises:
            Exception: The last exception if all retries fail
        """
        last_exception = None
        retry_delay = self.initial_retry_delay
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                # Don't retry on the last attempt
                if attempt == self.max_retries - 1:
                    logger.error(
                        f"All {self.max_retries} retry attempts failed for "
                        f"{func.__name__}: {str(e)}"
                    )
                    raise
                
                # Log retry attempt
                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries} failed for "
                    f"{func.__name__}: {str(e)}. Retrying in {retry_delay}s..."
                )
                
                # Wait before retrying
                await asyncio.sleep(retry_delay)
                
                # Calculate next retry delay with exponential backoff
                retry_delay = min(
                    retry_delay * self.retry_multiplier,
                    self.max_retry_delay
                )
        
        # This should never be reached, but just in case
        raise last_exception

    def _convert_messages(
        self,
        messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Convert messages to provider-specific format.
        
        Handles conversion of:
        - Text content
        - Image attachments
        - Multi-part messages
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Converted messages in provider-specific format
        """
        converted = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Handle string content
            if isinstance(content, str):
                converted.append({
                    "role": role,
                    "content": content
                })
            # Handle array content (multimodal)
            elif isinstance(content, list):
                converted_content = []
                
                for item in content:
                    if item.get("type") == "text":
                        converted_content.append({
                            "type": "text",
                            "text": item.get("text", "")
                        })
                    elif item.get("type") == "image_url":
                        image_url = item.get("image_url", {}).get("url", "")
                        converted_content.append({
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        })
                
                converted.append({
                    "role": role,
                    "content": converted_content
                })
            else:
                # Fallback for unknown content types
                converted.append(msg)
        
        return converted

    def _extract_thinking_and_answer(
        self,
        text: str,
        reasoning: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Extract thinking chain and answer from response text.
        
        Handles various formats:
        - <think>...</think> tags
        - <thinking>...</thinking> tags
        - Separate reasoning field
        
        Args:
            text: Response text that may contain thinking tags
            reasoning: Separate reasoning content (if provided by API)
            
        Returns:
            Dictionary with 'answer' and 'cot' (chain-of-thought) keys
        """
        answer = text
        cot = reasoning or ""
        
        # Check for <think> or <thinking> tags
        if "<think>" in text or "<thinking>" in text:
            # Extract thinking chain
            if "<think>" in text:
                start_tag = "<think>"
                end_tag = "</think>"
            else:
                start_tag = "<thinking>"
                end_tag = "</thinking>"
            
            start_idx = text.find(start_tag)
            end_idx = text.find(end_tag)
            
            if start_idx != -1 and end_idx != -1:
                cot = text[start_idx + len(start_tag):end_idx].strip()
                # Remove thinking tags from answer
                answer = text[:start_idx] + text[end_idx + len(end_tag):]
                answer = answer.strip()
        
        # Clean up whitespace
        if answer.startswith("\n\n"):
            answer = answer[2:]
        if cot.endswith("\n\n"):
            cot = cot[:-2]
        
        return {
            "answer": answer,
            "cot": cot
        }

    def _build_vision_messages(
        self,
        prompt: str,
        image_data: str,
        mime_type: str = "image/jpeg"
    ) -> List[Dict[str, Any]]:
        """
        Build messages for vision/multimodal requests.
        
        Args:
            prompt: Text prompt
            image_data: Base64 image data or data URL
            mime_type: MIME type of the image
            
        Returns:
            List of messages with text and image content
        """
        # Ensure image data is in data URL format
        if not image_data.startswith("data:"):
            image_data = f"data:{mime_type};base64,{image_data}"
        
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data
                        }
                    }
                ]
            }
        ]
