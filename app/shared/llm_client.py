"""
LLM and Embedding Provider Abstraction Layer

This module provides unified interfaces for multiple LLM and embedding providers (Ollama, OpenAI-compatible).
Follows RULE 9: Async Functions for All I/O and RULE 2: All Environment Variables via config.py

Usage Examples:
    # LLM Generation
    from app.shared.llm_client import get_llm_client

    llm_client = get_llm_client()
    response = await llm_client.generate("What is Python?")

    # JSON output mode
    response = await llm_client.generate(
        "List 3 colors in JSON",
        format="json"
    )

    # Embeddings
    from app.shared.llm_client import get_embedding_client

    embedding_client = get_embedding_client()
    vector = await embedding_client.embed("Hello world")
    # Returns: List[float] with length EMBEDDING_DIM (default 1024)
"""

import asyncio
import httpx
from abc import ABC, abstractmethod
from typing import Optional, List

from app.shared.config import settings


# Custom Exception Classes (RULE 6: All Exceptions Must Use Custom Classes)
class LLMTimeoutError(Exception):
    """Raised when LLM/embedding request times out."""
    pass


class LLMProviderError(Exception):
    """Raised when LLM/embedding provider returns an error."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)


class LLMResponseError(Exception):
    """Raised when LLM/embedding response cannot be parsed."""
    pass


# Abstract Base Class for LLM Providers
class LLMProvider(ABC):
    """Abstract base class for LLM provider implementations."""

    def __init__(self, base_url: str, timeout: float, api_key: Optional[str] = None):
        self.base_url = base_url
        self.timeout = timeout
        self.api_key = api_key
        self.max_retries = 3

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        format: Optional[str] = None
    ) -> str:
        """
        Generate text response from prompt.

        Args:
            prompt: Input text prompt
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens to generate (provider-specific default if None)
            format: Output format, "json" for structured output (optional)

        Returns:
            Generated text response as string

        Raises:
            LLMTimeoutError: Request timed out
            LLMProviderError: Provider returned an error
            LLMResponseError: Response parsing failed
        """
        pass

    async def _retry_request(self, request_func):
        """
        Execute request with exponential backoff retry logic.

        Args:
            request_func: Async function to execute

        Returns:
            Response from request_func

        Raises:
            LLMTimeoutError: All retries timed out
            LLMProviderError: HTTP error after all retries
        """
        for attempt in range(self.max_retries):
            try:
                return await request_func()
            except httpx.TimeoutException as e:
                if attempt == self.max_retries - 1:
                    raise LLMTimeoutError(f"Request timed out after {self.max_retries} attempts") from e
                # Exponential backoff: 1s, 2s, 4s
                await asyncio.sleep(2 ** attempt)
            except httpx.HTTPStatusError as e:
                # Retry on 5xx errors, fail fast on 4xx
                if e.response.status_code >= 500:
                    if attempt == self.max_retries - 1:
                        raise LLMProviderError(
                            f"Provider error: {e.response.status_code} - {e.response.text}",
                            status_code=e.response.status_code
                        ) from e
                    await asyncio.sleep(2 ** attempt)
                else:
                    # 4xx errors (auth, bad request) - fail immediately
                    raise LLMProviderError(
                        f"Provider error: {e.response.status_code} - {e.response.text}",
                        status_code=e.response.status_code
                    ) from e


class OllamaProvider(LLMProvider):
    """
    Ollama LLM provider implementation.

    Ollama API Documentation:
        - Endpoint: POST /api/generate
        - Request: {"model": "...", "prompt": "...", "stream": false, "format": "json"}
        - Response: {"response": "..."}

    Usage Example:
        provider = OllamaProvider(
            base_url="http://localhost:11434",
            timeout=1200.0
        )
        response = await provider.generate("What is Python?")
    """

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        format: Optional[str] = None
    ) -> str:
        """Generate text using Ollama API."""
        model = settings.LLM_MODEL

        async def _make_request():
            async with httpx.AsyncClient() as client:
                # Build request payload
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                    }
                }

                # Add optional parameters
                if max_tokens:
                    payload["options"]["num_predict"] = max_tokens
                if format:
                    payload["format"] = format

                # Make request
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()

                # Parse response
                try:
                    result = response.json()
                    return result.get("response", "")
                except (KeyError, ValueError) as e:
                    raise LLMResponseError(f"Failed to parse Ollama response: {e}") from e

        return await self._retry_request(_make_request)


class OpenAICompatibleProvider(LLMProvider):
    """
    OpenAI-compatible LLM provider implementation (LiteLLM, OpenAI API).

    OpenAI API Documentation:
        - Endpoint: POST /v1/chat/completions
        - Request: {"model": "...", "messages": [{"role": "user", "content": "..."}], "temperature": ..., "max_tokens": ...}
        - Response: {"choices": [{"message": {"content": "..."}}]}
        - Authentication: Authorization: Bearer {API_KEY}

    Usage Example:
        provider = OpenAICompatibleProvider(
            base_url="https://api.openai.com",
            timeout=1200.0,
            api_key="sk-..."
        )
        response = await provider.generate("What is Python?")
    """

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        format: Optional[str] = None
    ) -> str:
        """Generate text using OpenAI-compatible API."""
        if not self.api_key:
            raise LLMProviderError("API key required for OpenAI-compatible provider")

        model = settings.LLM_MODEL

        async def _make_request():
            async with httpx.AsyncClient() as client:
                # Build request payload
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                }

                # Add optional parameters
                if max_tokens:
                    payload["max_tokens"] = max_tokens
                if format == "json":
                    payload["response_format"] = {"type": "json_object"}

                # Make request with authentication
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()

                # Parse response
                try:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                except (KeyError, IndexError, ValueError) as e:
                    raise LLMResponseError(f"Failed to parse OpenAI-compatible response: {e}") from e

        return await self._retry_request(_make_request)


def get_llm_client() -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider based on configuration.

    Returns:
        LLMProvider instance configured based on settings.LLM_BINDING

    Raises:
        ValueError: Unsupported LLM_BINDING value

    Usage Examples:
        # Use default provider (Ollama)
        client = get_llm_client()
        response = await client.generate("Hello, world!")

        # Provider determined by LLM_BINDING environment variable
        # LLM_BINDING=ollama -> OllamaProvider
        # LLM_BINDING=openai -> OpenAICompatibleProvider
        # LLM_BINDING=litellm -> OpenAICompatibleProvider
    """
    binding = settings.LLM_BINDING.lower()

    if binding == "ollama":
        return OllamaProvider(
            base_url=settings.LLM_BINDING_HOST,
            timeout=settings.LLM_TIMEOUT
        )
    elif binding in ["openai", "litellm"]:
        return OpenAICompatibleProvider(
            base_url=settings.LLM_BINDING_HOST,
            timeout=settings.LLM_TIMEOUT,
            api_key=settings.LLM_BINDING_API_KEY
        )
    else:
        raise ValueError(
            f"Unsupported LLM_BINDING: {settings.LLM_BINDING}. "
            f"Supported values: ollama, openai, litellm"
        )


# ============================================================================
# Embedding Provider Abstraction
# ============================================================================


class EmbeddingProvider(ABC):
    """Abstract base class for embedding provider implementations."""

    def __init__(self, base_url: str, timeout: float, api_key: Optional[str] = None):
        self.base_url = base_url
        self.timeout = timeout
        self.api_key = api_key
        self.max_retries = 3

    @abstractmethod
    async def embed(
        self,
        text: str
    ) -> List[float]:
        """
        Generate embedding vector for input text.

        Args:
            text: Input text to embed

        Returns:
            Embedding vector as list of floats (length = EMBEDDING_DIM)

        Raises:
            LLMTimeoutError: Request timed out
            LLMProviderError: Provider returned an error
            LLMResponseError: Response parsing failed
        """
        pass

    async def _retry_request(self, request_func):
        """
        Execute request with exponential backoff retry logic.

        Args:
            request_func: Async function to execute

        Returns:
            Response from request_func

        Raises:
            LLMTimeoutError: All retries timed out
            LLMProviderError: HTTP error after all retries
        """
        for attempt in range(self.max_retries):
            try:
                return await request_func()
            except httpx.TimeoutException as e:
                if attempt == self.max_retries - 1:
                    raise LLMTimeoutError(f"Embedding request timed out after {self.max_retries} attempts") from e
                await asyncio.sleep(2 ** attempt)
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500:
                    if attempt == self.max_retries - 1:
                        raise LLMProviderError(
                            f"Embedding provider error: {e.response.status_code} - {e.response.text}",
                            status_code=e.response.status_code
                        ) from e
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise LLMProviderError(
                        f"Embedding provider error: {e.response.status_code} - {e.response.text}",
                        status_code=e.response.status_code
                    ) from e


class OllamaEmbeddingProvider(EmbeddingProvider):
    """
    Ollama embedding provider implementation.

    Ollama Embedding API:
        - Endpoint: POST /api/embeddings
        - Request: {"model": "...", "prompt": "..."}
        - Response: {"embedding": [0.1, 0.2, ...]}

    Usage Example:
        provider = OllamaEmbeddingProvider(
            base_url="http://localhost:11434",
            timeout=600.0
        )
        vector = await provider.embed("Hello world")
    """

    async def embed(
        self,
        text: str
    ) -> List[float]:
        """Generate embedding using Ollama API."""
        model = settings.EMBEDDING_MODEL

        async def _make_request():
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": model,
                        "prompt": text
                    },
                    timeout=self.timeout
                )
                response.raise_for_status()

                try:
                    result = response.json()
                    return result.get("embedding", [])
                except (KeyError, ValueError) as e:
                    raise LLMResponseError(f"Failed to parse Ollama embedding response: {e}") from e

        return await self._retry_request(_make_request)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    OpenAI-compatible embedding provider implementation.

    OpenAI Embedding API:
        - Endpoint: POST /v1/embeddings
        - Request: {"model": "...", "input": "..."}
        - Response: {"data": [{"embedding": [0.1, 0.2, ...]}]}
        - Authentication: Authorization: Bearer {API_KEY}

    Usage Example:
        provider = OpenAIEmbeddingProvider(
            base_url="https://api.openai.com",
            timeout=600.0,
            api_key="sk-..."
        )
        vector = await provider.embed("Hello world")
    """

    async def embed(
        self,
        text: str
    ) -> List[float]:
        """Generate embedding using OpenAI-compatible API."""
        if not self.api_key:
            raise LLMProviderError("API key required for OpenAI-compatible embedding provider")

        model = settings.EMBEDDING_MODEL

        async def _make_request():
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = await client.post(
                    f"{self.base_url}/v1/embeddings",
                    json={
                        "model": model,
                        "input": text
                    },
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()

                try:
                    result = response.json()
                    return result["data"][0]["embedding"]
                except (KeyError, IndexError, ValueError) as e:
                    raise LLMResponseError(f"Failed to parse OpenAI embedding response: {e}") from e

        return await self._retry_request(_make_request)


def get_embedding_client() -> EmbeddingProvider:
    """
    Factory function to get the appropriate embedding provider based on configuration.

    Returns:
        EmbeddingProvider instance configured based on settings.EMBEDDING_BINDING

    Raises:
        ValueError: Unsupported EMBEDDING_BINDING value

    Usage Examples:
        # Use default provider (Ollama)
        client = get_embedding_client()
        vector = await client.embed("Hello, world!")

        # Provider determined by EMBEDDING_BINDING environment variable
        # EMBEDDING_BINDING=ollama -> OllamaEmbeddingProvider
        # EMBEDDING_BINDING=openai -> OpenAIEmbeddingProvider
    """
    binding = settings.EMBEDDING_BINDING.lower()

    if binding == "ollama":
        return OllamaEmbeddingProvider(
            base_url=settings.EMBEDDING_BINDING_HOST,
            timeout=settings.EMBEDDING_TIMEOUT
        )
    elif binding == "openai":
        return OpenAIEmbeddingProvider(
            base_url=settings.EMBEDDING_BINDING_HOST,
            timeout=settings.EMBEDDING_TIMEOUT,
            api_key=settings.EMBEDDING_BINDING_API_KEY
        )
    else:
        raise ValueError(
            f"Unsupported EMBEDDING_BINDING: {settings.EMBEDDING_BINDING}. "
            f"Supported values: ollama, openai"
        )
