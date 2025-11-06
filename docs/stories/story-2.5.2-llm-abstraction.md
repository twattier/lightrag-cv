# Story 2.5.2: LLM Provider Abstraction & Multi-Provider Support

> 📋 **Epic**: [Epic 2.5: Script Refactoring & Application Structure](../epics/epic-2.5-revised.md)
> 📋 **Architecture**: [Tech Stack](../architecture/tech-stack.md), [Coding Standards](../architecture/coding-standards.md)

## User Story

**As a** developer,
**I want** an LLM provider abstraction layer supporting multiple providers,
**so that** scripts can work with Ollama, OpenAI, or LiteLLM without code changes.

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 3-4 hours
- **Dependencies**: Story 2.5.1 ✅
- **Blocks**: Story 2.5.3

## Acceptance Criteria

1. ✅ **Multi-Provider Configuration**:
   - `app/shared/config.py` supports:
     - `LLM_BINDING` (default: `ollama`)
     - `LLM_BINDING_HOST` (replaces `OLLAMA_BASE_URL`)
     - `LLM_MODEL` (replaces `OLLAMA_LLM_MODEL`)
     - `EMBEDDING_BINDING` (default: `ollama`)
     - `EMBEDDING_BINDING_HOST`
     - `EMBEDDING_MODEL` (replaces `OLLAMA_EMBEDDING_MODEL`)
     - `EMBEDDING_DIM` (default: `1024`)
   - Backward compatibility: Falls back to `OLLAMA_*` vars if new vars not set

2. ✅ **LLM Client Abstraction**:
   - `app/shared/llm_client.py` created with:
     - `get_llm_client()` factory function
     - Ollama provider implementation
     - OpenAI-compatible provider implementation (LiteLLM)
     - Unified interface: `generate(prompt, model, temperature, max_tokens, format='json')`
     - Timeout and retry logic

3. ✅ **`.env.example` Updated**:
   - New variables documented with examples
   - Backward compatibility variables marked as deprecated
   - Provider configuration examples included

4. ✅ **Abstraction Validated**:
   - Test with simple one-liner:
     ```bash
     python -c "from app.shared.llm_client import get_llm_client; print(get_llm_client().generate('Hello'))"
     ```
   - Returns valid response from Ollama

5. ✅ **Service Integration Verified**:
   - LightRAG service health check passes: `curl http://localhost:9621/health`
   - Existing Ollama workflows work without `.env` changes (backward compatibility)

6. ✅ **Documentation Updated**:
   - LLM provider configuration guide added to documentation
   - Examples for Ollama and LiteLLM included

## Tasks

- [ ] **Task 1: Update `app/shared/config.py` for Multi-Provider**
  - Add new LLM configuration variables (including `LLM_BINDING_API_KEY`)
  - Add new embedding configuration variables (including `EMBEDDING_BINDING_API_KEY`)
  - Implement backward compatibility logic
  - Add validation for provider selection
  - Test environment variable loading

- [ ] **Task 2: Create `app/shared/llm_client.py`**
  - Implement `get_llm_client()` factory function
  - Create `OllamaClient` class with:
    - `generate()` method using `/api/generate` endpoint
    - Request/response formatting for Ollama
    - Timeout handling
  - Create `OpenAIClient` class with:
    - `generate()` method using `/v1/chat/completions` endpoint
    - Request/response formatting for OpenAI-compatible APIs
    - Timeout handling
  - Add error handling and retry logic

- [ ] **Task 3: Update `.env.example`**
  - Add new LLM provider configuration section
  - Document all new variables with descriptions
  - Add examples for Ollama configuration
  - Add examples for LiteLLM configuration
  - Mark `OLLAMA_*` variables as deprecated

- [ ] **Task 4: Test LLM Abstraction**
  - Test one-liner with Ollama provider
  - Verify response formatting
  - Test backward compatibility (only `OLLAMA_*` vars set)
  - Verify error handling for invalid provider

- [ ] **Task 5: Verify LightRAG Service Integration**
  - Check LightRAG health endpoint
  - Verify LightRAG service uses unified config pattern
  - Confirm no breaking changes to existing workflows

- [ ] **Task 6: Create Documentation**
  - Add LLM provider configuration guide to `/app/README.md`
  - Document provider selection process
  - Provide Ollama and LiteLLM setup examples
  - Add troubleshooting section

## Dev Notes

### LLM Client Interface

Unified interface for all providers:

```python
# app/shared/llm_client.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
from app.shared.config import settings

class LLMClient(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        format: str = 'json'
    ) -> Dict[str, Any]:
        """Generate text using LLM provider"""
        pass

class OllamaClient(LLMClient):
    def __init__(self, base_url: str, model: str, timeout: int = 120):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout

    async def generate(self, prompt, model=None, temperature=0.7, max_tokens=2000, format='json'):
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model or self.model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "options": {"num_predict": max_tokens},
                    "format": format
                }
            )
            return response.json()

class OpenAIClient(LLMClient):
    def __init__(self, base_url: str, model: str, api_key: Optional[str] = None, timeout: int = 120):
        self.base_url = base_url
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    async def generate(self, prompt, model=None, temperature=0.7, max_tokens=2000, format='json'):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json={
                    "model": model or self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "response_format": {"type": "json_object"} if format == 'json' else None
                }
            )
            return response.json()

def get_llm_client() -> LLMClient:
    """Factory function to get appropriate LLM client"""
    binding = settings.LLM_BINDING.lower()

    if binding == "ollama":
        return OllamaClient(
            base_url=settings.LLM_BINDING_HOST,
            model=settings.LLM_MODEL,
            timeout=settings.LLM_TIMEOUT
        )
    elif binding in ["openai", "litellm"]:
        # Validate API key is set for OpenAI-compatible providers
        api_key = getattr(settings, 'LLM_BINDING_API_KEY', None)
        if not api_key:
            raise ValueError(f"LLM_BINDING_API_KEY is required when LLM_BINDING={binding}")

        return OpenAIClient(
            base_url=settings.LLM_BINDING_HOST,
            model=settings.LLM_MODEL,
            api_key=api_key,
            timeout=settings.LLM_TIMEOUT
        )
    else:
        raise ValueError(f"Unsupported LLM binding: {binding}")
```

### Configuration Updates

Update `app/shared/config.py`:

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # New unified LLM configuration
    LLM_BINDING: str = "ollama"
    LLM_BINDING_HOST: Optional[str] = None
    LLM_MODEL: Optional[str] = None
    LLM_BINDING_API_KEY: Optional[str] = None  # Required for openai/litellm
    LLM_TIMEOUT: int = 1200

    # Embedding configuration
    EMBEDDING_BINDING: str = "ollama"
    EMBEDDING_BINDING_HOST: Optional[str] = None
    EMBEDDING_MODEL: Optional[str] = None
    EMBEDDING_BINDING_API_KEY: Optional[str] = None  # Required for openai
    EMBEDDING_DIM: int = 1024
    EMBEDDING_TIMEOUT: int = 600

    # Backward compatibility (deprecated)
    OLLAMA_BASE_URL: Optional[str] = None
    OLLAMA_LLM_MODEL: Optional[str] = None
    OLLAMA_EMBEDDING_MODEL: Optional[str] = None

    @property
    def llm_host(self) -> str:
        """Get LLM host with backward compatibility"""
        return self.LLM_BINDING_HOST or self.OLLAMA_BASE_URL or "http://localhost:11434"

    @property
    def llm_model(self) -> str:
        """Get LLM model with backward compatibility"""
        return self.LLM_MODEL or self.OLLAMA_LLM_MODEL or "qwen2.5:7b-instruct-q4_K_M"

    @property
    def embedding_host(self) -> str:
        """Get embedding host with backward compatibility"""
        return self.EMBEDDING_BINDING_HOST or self.OLLAMA_BASE_URL or "http://localhost:11434"

    @property
    def embedding_model(self) -> str:
        """Get embedding model with backward compatibility"""
        return self.EMBEDDING_MODEL or self.OLLAMA_EMBEDDING_MODEL or "bge-m3:latest"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### Testing One-Liner

After implementation, test with:

```bash
# Set PYTHONPATH
export PYTHONPATH=/home/ubuntu/dev/lightrag-cv

# Test LLM abstraction
python -c "
from app.shared.llm_client import get_llm_client
import asyncio

async def test():
    client = get_llm_client()
    result = await client.generate('Say hello', format='text')
    print(result)

asyncio.run(test())
"
```

### Success Criteria

- ✅ One-liner returns valid Ollama response
- ✅ LightRAG health check passes
- ✅ Backward compatibility works (test with only `OLLAMA_*` vars)
- ✅ Ready for Story 2.5.3 to migrate scripts using abstraction

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-11-06 | 1.0 | Story created from Epic 2.5 validation with pragmatic fixes | Sarah (PO) |
