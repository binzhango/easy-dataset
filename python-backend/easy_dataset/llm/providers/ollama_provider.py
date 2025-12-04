"""Ollama provider implementation for local LLM models."""

import json
import logging
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx

from easy_dataset.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """
    Ollama provider implementation for local models.
    
    Supports:
    - Connection to local Ollama instance
    - Listing available models
    - Streaming and non-streaming completions
    - Chain-of-thought reasoning (if model supports it)
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Ollama provider.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        
        # Normalize endpoint (handle /v1 and /api variations)
        self.endpoint = self._normalize_endpoint(self.endpoint)
        
        # Initialize HTTP client
        self.http_client = httpx.AsyncClient(timeout=300.0)  # 5 minute timeout

    def _normalize_endpoint(self, endpoint: str) -> str:
        """
        Normalize Ollama endpoint URL.
        
        Converts /v1 to /api for compatibility with older configurations.
        
        Args:
            endpoint: Original endpoint URL
            
        Returns:
            Normalized endpoint URL
        """
        if not endpoint:
            return "http://localhost:11434"
        
        # Remove trailing slash
        endpoint = endpoint.rstrip("/")
        
        # Convert /v1 to /api for Ollama
        if endpoint.endswith("/v1"):
            endpoint = endpoint[:-3] + "/api"
        elif endpoint.endswith("/api"):
            pass  # Already correct
        elif not endpoint.endswith("/api"):
            # Add /api if not present
            endpoint = endpoint
        
        return endpoint

    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models from Ollama instance.
        
        Returns:
            List of model dictionaries with name, modified_at, and size
        """
        try:
            # Ensure endpoint doesn't end with /api for tags endpoint
            base_url = self.endpoint.replace("/api", "")
            response = await self.http_client.get(f"{base_url}/api/tags")
            response.raise_for_status()
            
            data = response.json()
            
            if data and "models" in data:
                return [
                    {
                        "name": model.get("name", ""),
                        "modified_at": model.get("modified_at", ""),
                        "size": model.get("size", 0),
                    }
                    for model in data["models"]
                ]
            
            return []
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a chat completion using Ollama API.
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters to override defaults
            
        Returns:
            Dictionary containing response data
        """
        async def _make_request():
            # Convert messages to Ollama format
            converted_messages = self._convert_messages(messages)
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": converted_messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.temperature),
                    "top_p": kwargs.get("top_p", self.top_p),
                    "num_predict": kwargs.get("max_tokens", self.max_tokens),
                }
            }
            
            # Add top_k if specified
            if self.top_k is not None:
                payload["options"]["top_k"] = self.top_k
            
            # Ensure endpoint has /api
            base_url = self.endpoint.replace("/api", "")
            chat_url = f"{base_url}/api/chat"
            
            # Make API call
            response = await self.http_client.post(
                chat_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            # Extract text and reasoning
            text = data.get("message", {}).get("content", "")
            reasoning = data.get("message", {}).get("thinking", "")
            
            # Extract thinking and answer
            result = self._extract_thinking_and_answer(text, reasoning)
            
            return {
                "text": result["answer"],
                "reasoning": result["cot"],
                "usage": {
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                },
                "response": data
            }
        
        # Execute with retry logic
        return await self._retry_with_backoff(_make_request)

    async def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate a streaming chat completion using Ollama API.
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters to override defaults
            
        Yields:
            String chunks of the generated response
        """
        async def _make_stream_request():
            # Convert messages to Ollama format
            converted_messages = self._convert_messages(messages)
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": converted_messages,
                "stream": True,
                "options": {
                    "temperature": kwargs.get("temperature", self.temperature),
                    "top_p": kwargs.get("top_p", self.top_p),
                    "num_predict": kwargs.get("max_tokens", self.max_tokens),
                }
            }
            
            # Add top_k if specified
            if self.top_k is not None:
                payload["options"]["top_k"] = self.top_k
            
            # Ensure endpoint has /api
            base_url = self.endpoint.replace("/api", "")
            chat_url = f"{base_url}/api/chat"
            
            # Make streaming API call
            async with self.http_client.stream(
                "POST",
                chat_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response.raise_for_status()
                
                return response
        
        # Execute with retry logic
        response = await self._retry_with_backoff(_make_stream_request)
        
        # Track if we're in thinking mode
        is_thinking = False
        
        # Stream the response
        async for line in response.aiter_lines():
            if not line.strip():
                continue
            
            try:
                # Parse JSON line
                data = json.loads(line)
                
                # Extract content
                message = data.get("message", {})
                content = message.get("content", "")
                thinking = message.get("thinking", "")
                
                # Handle thinking/reasoning content
                if thinking:
                    if not is_thinking:
                        yield "<think>"
                        is_thinking = True
                    yield thinking
                
                # Handle regular content
                if content:
                    if is_thinking:
                        yield "</think>"
                        is_thinking = False
                    yield content
                
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON line: {line}")
                continue
        
        # Close thinking tag if still open
        if is_thinking:
            yield "</think>"

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - close HTTP client."""
        await self.http_client.aclose()
