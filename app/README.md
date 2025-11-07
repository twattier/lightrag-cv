# LightRAG-CV Application Structure

This directory contains the application workflows and shared services for the LightRAG-CV project.

## Directory Structure

```
app/
├── shared/              # Shared configuration and utilities
│   ├── config.py        # Centralized environment configuration
│   └── llm_client.py    # LLM provider abstraction layer
├── cigref_ingest/       # CIGREF nomenclature ingestion workflows (numbered: cigref_1_parse.py, cigref_2_import.py)
├── cv_ingest/           # CV processing workflows (numbered: cv1_download.py, cv2_parse.py, cv3_classify.py, cv4_import.py)
└── tests/               # SQL queries, tests, and development artifacts
```

### Numbered Workflow Naming Convention

Scripts within workflow directories follow a numbered naming pattern `{domain}{step}_{action}.py`:
- **CIGREF workflows**: `cigref_1_parse.py` (parse documents), `cigref_2_import.py` (import to LightRAG)
- **CV workflows**: `cv1_download.py` (download dataset), `cv2_parse.py` (parse CVs), `cv3_classify.py` (classify with LLM), `cv4_import.py` (import to LightRAG)

Numbers indicate execution order within the workflow.

## LLM Provider Configuration

The application supports multiple LLM providers through a unified abstraction layer. This allows flexible switching between Ollama (local), OpenAI, and LiteLLM without code changes.

### Quick Start (Ollama - Default)

No configuration required! The application defaults to Ollama running on localhost:

```python
from app.shared.llm_client import get_llm_client

# Uses Ollama by default
client = get_llm_client()
response = await client.generate("What is Python?")
```

### Environment Variables

Configure LLM providers via environment variables in `.env`:

#### LLM Provider Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LLM_BINDING` | Provider type: `ollama`, `openai`, `litellm` | `ollama` | No |
| `LLM_BINDING_HOST` | Provider base URL | `http://localhost:11434` | No |
| `LLM_MODEL` | Model name | `qwen2.5:7b-instruct-q4_K_M` | No |
| `LLM_BINDING_API_KEY` | API key (required for OpenAI/LiteLLM) | - | Conditional |
| `LLM_TIMEOUT` | Request timeout in seconds | `1200` | No |

#### Embedding Provider Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `EMBEDDING_BINDING` | Provider type: `ollama`, `openai` | `ollama` | No |
| `EMBEDDING_BINDING_HOST` | Provider base URL | `http://localhost:11434` | No |
| `EMBEDDING_MODEL` | Model name | `bge-m3:latest` | No |
| `EMBEDDING_BINDING_API_KEY` | API key (required for OpenAI) | - | Conditional |
| `EMBEDDING_DIM` | Embedding dimensions | `1024` | No |
| `EMBEDDING_TIMEOUT` | Request timeout in seconds | `600` | No |

### Provider Configuration Examples

#### Example 1: Ollama (Local - Default)

```bash
# .env
LLM_BINDING=ollama
LLM_BINDING_HOST=http://localhost:11434
LLM_MODEL=qwen2.5:7b-instruct-q4_K_M

EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://localhost:11434
EMBEDDING_MODEL=bge-m3:latest
```

From Docker containers, use `host.docker.internal`:
```bash
LLM_BINDING_HOST=http://host.docker.internal:11434
EMBEDDING_BINDING_HOST=http://host.docker.internal:11434
```

#### Example 2: OpenAI API

```bash
# .env
LLM_BINDING=openai
LLM_BINDING_HOST=https://api.openai.com
LLM_MODEL=gpt-4
LLM_BINDING_API_KEY=sk-your-api-key-here

EMBEDDING_BINDING=openai
EMBEDDING_BINDING_HOST=https://api.openai.com
EMBEDDING_MODEL=text-embedding-ada-002
EMBEDDING_BINDING_API_KEY=sk-your-api-key-here
```

#### Example 3: LiteLLM Proxy

```bash
# .env
LLM_BINDING=litellm
LLM_BINDING_HOST=http://localhost:4000
LLM_MODEL=gpt-4
LLM_BINDING_API_KEY=your-litellm-api-key

EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://localhost:11434
EMBEDDING_MODEL=bge-m3:latest
```

### Usage Examples

#### Basic Usage

```python
from app.shared.llm_client import get_llm_client

# Get client (provider determined by LLM_BINDING env var)
client = get_llm_client()

# Generate text
response = await client.generate("What is Python?")
print(response)
```

#### JSON Output Mode

```python
client = get_llm_client()

# Request structured JSON output
response = await client.generate(
    "List 3 programming languages in JSON format",
    format="json"
)
print(response)  # {"languages": ["Python", "JavaScript", "Go"]}
```

#### Custom Parameters

```python
client = get_llm_client()

response = await client.generate(
    prompt="Write a haiku about coding",
    temperature=0.9,      # Higher creativity
    max_tokens=100        # Limit output length
)
```

#### Override Model at Runtime

```python
client = get_llm_client()

# Use different model for this request
response = await client.generate(
    prompt="Complex reasoning task",
    model="qwen3:8b"  # Override default model
)
```

### Error Handling

The LLM client provides custom exceptions for robust error handling:

```python
from app.shared.llm_client import (
    get_llm_client,
    LLMTimeoutError,
    LLMProviderError,
    LLMResponseError
)

client = get_llm_client()

try:
    response = await client.generate("Hello")
except LLMTimeoutError:
    print("Request timed out - check provider availability")
except LLMProviderError as e:
    print(f"Provider error: {e.status_code} - {e}")
except LLMResponseError as e:
    print(f"Failed to parse response: {e}")
```

### Retry Logic

The client automatically retries failed requests with exponential backoff:
- **Max retries**: 3 attempts
- **Backoff**: 1s, 2s, 4s
- **Retries on**: Timeouts, HTTP 5xx errors
- **Fails fast on**: HTTP 4xx errors (bad request, auth failure)

### Migration from OLLAMA_* Variables

The new unified configuration maintains backward compatibility with legacy `OLLAMA_*` variables:

#### Old Pattern (Still Supported)
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=qwen2.5:7b-instruct-q4_K_M
```

#### New Pattern (Recommended)
```bash
LLM_BINDING=ollama
LLM_BINDING_HOST=http://localhost:11434
LLM_MODEL=qwen2.5:7b-instruct-q4_K_M
```

**Migration Steps**:
1. Add new `LLM_BINDING_*` variables to `.env`
2. Test with both old and new variables present
3. Remove old `OLLAMA_*` variables once confirmed working
4. Update scripts to use `from app.shared.config import settings`

## Configuration Module

The `app/shared/config.py` module provides centralized configuration management:

```python
from app.shared.config import settings

# Access configuration
print(settings.LLM_BINDING)        # ollama
print(settings.LLM_MODEL)          # qwen2.5:7b-instruct-q4_K_M
print(settings.llm_url)            # http://localhost:11434

# Database configuration
print(settings.postgres_dsn)       # postgresql://...

# LightRAG service
print(settings.lightrag_url)       # http://localhost:9621
```

### Property Methods

The config provides convenience properties for provider-agnostic access:

```python
settings.llm_url          # Returns LLM_BINDING_HOST
settings.embedding_url    # Returns EMBEDDING_BINDING_HOST
settings.lightrag_url     # Returns LightRAG service URL
settings.postgres_dsn     # Returns PostgreSQL connection string
```

## Development Guidelines

### Coding Standards

Follow project coding standards defined in [docs/architecture/coding-standards.md](../docs/architecture/coding-standards.md):

- **RULE 2**: All environment variables via `config.py`
  ```python
  # ✅ CORRECT
  from app.shared.config import settings
  llm_host = settings.LLM_BINDING_HOST

  # ❌ WRONG
  llm_host = os.getenv("LLM_BINDING_HOST")
  ```

- **RULE 9**: Async functions for all I/O
  ```python
  # ✅ CORRECT
  async def generate_text(prompt: str):
      client = get_llm_client()
      return await client.generate(prompt)
  ```

### Testing

Test LLM abstraction:
```bash
# Static validation (no dependencies)
python3 -m py_compile app/shared/llm_client.py

# Runtime test (requires httpx and running Ollama)
python -c "
import asyncio
from app.shared.llm_client import get_llm_client
print(asyncio.run(get_llm_client().generate('Hello')))
"
```

### Adding New Providers

To add a new provider:

1. Create provider class inheriting from `LLMProvider`
2. Implement `async def generate()` method
3. Add provider to `get_llm_client()` factory
4. Update documentation

Example:
```python
class CustomProvider(LLMProvider):
    async def generate(self, prompt, model=None, temperature=0.7,
                      max_tokens=None, format=None):
        # Implementation here
        pass

def get_llm_client():
    if settings.LLM_BINDING == "custom":
        return CustomProvider(...)
    # ... existing providers
```

## Related Documentation

- [Architecture Documentation](../docs/architecture.md)
- [Coding Standards](../docs/architecture/coding-standards.md)
- [Tech Stack](../docs/architecture/tech-stack.md)
- [Epic 2.5: Script Refactoring](../docs/epics/epic-2.5.md)

## Support

For issues or questions:
- Check existing scripts in `/scripts` for usage examples
- Review [PRD](../docs/prd.md) for requirements context
- Consult architecture documentation for design decisions
