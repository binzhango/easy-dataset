"""Google Gemini provider implementation using google-generativeai SDK."""

import logging
from typing import Any, AsyncIterator, Dict, List, Optional
import base64

try:
    import google.generativeai as genai
    from google.generativeai.types import GenerateContentResponse
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(
        "google-generativeai package not installed. "
        "Install with: pip install google-generativeai"
    )

from easy_dataset.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini provider implementation.
    
    Supports:
    - Gemini Pro and Gemini Pro Vision models
    - Streaming and non-streaming completions
    - Multimodal inputs (text + images)
    - Google-specific authentication
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Gemini provider.
        
        Args:
            config: Configuration dictionary
        """
        if not GENAI_AVAILABLE:
            raise ImportError(
                "google-generativeai package is required for GeminiProvider. "
                "Install with: pip install google-generativeai"
            )
        
        super().__init__(config)
        
        # Configure Gemini API
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        self.genai_model = genai.GenerativeModel(self.model)
        
        # Configure generation parameters
        self.generation_config = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_output_tokens": self.max_tokens,
        }
        
        # Add top_k if specified
        if self.top_k is not None:
            self.generation_config["top_k"] = self.top_k
        
        logger.info(f"Initialized Gemini provider with model: {self.model}")

    def _convert_messages_to_gemini(
        self,
        messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Convert messages to Gemini format.
        
        Gemini uses a different message format than OpenAI.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Converted messages for Gemini
        """
        gemini_messages = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Map roles (Gemini uses 'user' and 'model' instead of 'assistant')
            gemini_role = "model" if role == "assistant" else "user"
            
            # Handle string content
            if isinstance(content, str):
                gemini_messages.append({
                    "role": gemini_role,
                    "parts": [{"text": content}]
                })
            # Handle array content (multimodal)
            elif isinstance(content, list):
                parts = []
                
                for item in content:
                    if item.get("type") == "text":
                        parts.append({"text": item.get("text", "")})
                    elif item.get("type") == "image_url":
                        # Extract image data
                        image_url = item.get("image_url", {}).get("url", "")
                        
                        # Handle base64 images
                        if image_url.startswith("data:"):
                            # Extract base64 data
                            parts_split = image_url.split(",", 1)
                            if len(parts_split) == 2:
                                image_data = parts_split[1]
                                # Decode base64
                                image_bytes = base64.b64decode(image_data)
                                parts.append({
                                    "inline_data": {
                                        "mime_type": "image/jpeg",
                                        "data": image_data
                                    }
                                })
                
                if parts:
                    gemini_messages.append({
                        "role": gemini_role,
                        "parts": parts
                    })
        
        return gemini_messages

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a chat completion using Gemini API.
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters to override defaults
            
        Returns:
            Dictionary containing response data
        """
        async def _make_request():
            # Convert messages to Gemini format
            gemini_messages = self._convert_messages_to_gemini(messages)
            
            # Update generation config with kwargs
            generation_config = self.generation_config.copy()
            if "temperature" in kwargs:
                generation_config["temperature"] = kwargs["temperature"]
            if "max_tokens" in kwargs:
                generation_config["max_output_tokens"] = kwargs["max_tokens"]
            if "top_p" in kwargs:
                generation_config["top_p"] = kwargs["top_p"]
            
            # Build conversation history
            # Gemini expects alternating user/model messages
            history = gemini_messages[:-1] if len(gemini_messages) > 1 else []
            last_message = gemini_messages[-1] if gemini_messages else {"parts": [{"text": ""}]}
            
            # Start chat session
            chat = self.genai_model.start_chat(history=history)
            
            # Generate response
            response = await chat.send_message_async(
                last_message["parts"],
                generation_config=generation_config
            )
            
            # Extract text
            text = response.text if hasattr(response, "text") else ""
            
            # Extract thinking and answer
            result = self._extract_thinking_and_answer(text)
            
            # Calculate token usage (Gemini provides this in usage_metadata)
            usage = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            }
            
            if hasattr(response, "usage_metadata"):
                usage["prompt_tokens"] = response.usage_metadata.prompt_token_count
                usage["completion_tokens"] = response.usage_metadata.candidates_token_count
                usage["total_tokens"] = response.usage_metadata.total_token_count
            
            return {
                "text": result["answer"],
                "reasoning": result["cot"],
                "usage": usage,
                "response": {
                    "text": text,
                    "candidates": [
                        {
                            "content": {
                                "parts": [{"text": text}]
                            }
                        }
                    ]
                }
            }
        
        # Execute with retry logic
        return await self._retry_with_backoff(_make_request)

    async def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate a streaming chat completion using Gemini API.
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters to override defaults
            
        Yields:
            String chunks of the generated response
        """
        async def _make_stream_request():
            # Convert messages to Gemini format
            gemini_messages = self._convert_messages_to_gemini(messages)
            
            # Update generation config with kwargs
            generation_config = self.generation_config.copy()
            if "temperature" in kwargs:
                generation_config["temperature"] = kwargs["temperature"]
            if "max_tokens" in kwargs:
                generation_config["max_output_tokens"] = kwargs["max_tokens"]
            if "top_p" in kwargs:
                generation_config["top_p"] = kwargs["top_p"]
            
            # Build conversation history
            history = gemini_messages[:-1] if len(gemini_messages) > 1 else []
            last_message = gemini_messages[-1] if gemini_messages else {"parts": [{"text": ""}]}
            
            # Start chat session
            chat = self.genai_model.start_chat(history=history)
            
            # Generate streaming response
            response = await chat.send_message_async(
                last_message["parts"],
                generation_config=generation_config,
                stream=True
            )
            
            return response
        
        # Execute with retry logic
        stream = await self._retry_with_backoff(_make_stream_request)
        
        # Track if we're in thinking mode
        is_thinking = False
        
        # Stream the response
        async for chunk in stream:
            if not hasattr(chunk, "text") or not chunk.text:
                continue
            
            text = chunk.text
            
            # Check for thinking tags in the text
            if "<think>" in text or "<thinking>" in text:
                if not is_thinking:
                    is_thinking = True
                yield text
            elif "</think>" in text or "</thinking>" in text:
                yield text
                is_thinking = False
            else:
                yield text

    async def vision_chat(
        self,
        prompt: str,
        image_data: str,
        mime_type: str = "image/jpeg",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a chat completion with image input using Gemini Pro Vision.
        
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
