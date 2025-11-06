# Application Tests

Part of lightrag-cv application workflows.

## Available Tests

### LLM Client Integration Test

**Location**: `app/tests/test_llm_client.py`

**Purpose**: Validates LLM and embedding client connectivity using `.env` configuration.

**What it tests**:
1. ✅ LLM basic text generation
2. ✅ LLM JSON format generation
3. ✅ LLM longer text generation
4. ✅ Single text embedding generation
5. ✅ Longer text embedding generation
6. ✅ Embedding consistency (same input = similar output)

**Prerequisites**:
1. **Dependencies installed**:
   ```bash
   pip install -r app/requirements.txt
   # OR install individually:
   pip install python-dotenv httpx pydantic
   ```

2. **Services running**: Ollama or configured LLM/embedding providers

3. **Models pulled**:
   ```bash
   ollama pull qwen2.5:7b      # LLM model
   ollama pull bge-m3           # Embedding model
   ```

4. **Valid `.env` configuration** in project root

**Usage**:
```bash
# Method 1: Direct execution (recommended - auto-detects path)
python3 app/tests/test_llm_client.py

# Method 2: Module execution (requires PYTHONPATH)
export PYTHONPATH=/home/ubuntu/dev/lightrag-cv
python -m app.tests.test_llm_client
```

**Example Output**:
```
======================================================================
CONFIGURATION
======================================================================
LLM Provider:       ollama
LLM Host:           http://localhost:11434
LLM Model:          qwen2.5:7b
LLM Timeout:        1200.0s

Embedding Provider: ollama
Embedding Host:     http://localhost:11434
Embedding Model:    bge-m3
Embedding Dim:      1024
======================================================================

======================================================================
RUNNING LLM CLIENT INTEGRATION TESTS
======================================================================

🔍 Testing: LLM Basic Text Generation
   Prompt: 'What is 2+2? Answer in one word.'
   Response: Four
✅ PASS: LLM Basic Text Generation

...

======================================================================
TEST SUMMARY
======================================================================
Total Tests:  6
Passed:       6 ✅
Failed:       0 ❌
Skipped:      0 ⏭️

✅ ALL TESTS PASSED
```

**Troubleshooting**:

If tests fail, check:
1. **Service Status**: Verify Ollama/provider is running
   ```bash
   curl http://localhost:11434/api/tags  # Ollama
   ```

2. **Models Available**: Ensure models are pulled
   ```bash
   ollama list  # Check available models
   ollama pull qwen2.5:7b  # Pull LLM model
   ollama pull bge-m3      # Pull embedding model
   ```

3. **Configuration**: Review `.env` file
   - `LLM_BINDING` (ollama/openai/litellm)
   - `LLM_BINDING_HOST` (provider URL)
   - `LLM_MODEL` (model name)
   - `EMBEDDING_BINDING` (ollama/openai)
   - `EMBEDDING_BINDING_HOST` (provider URL)
   - `EMBEDDING_MODEL` (model name)

4. **Network**: Check connectivity to provider
   ```bash
   curl http://localhost:11434/api/tags
   ```

---

## Adding New Tests

To add new tests:

1. Create test file in `app/tests/`
2. Follow naming convention: `test_*.py`
3. Add module docstring with:
   - Purpose
   - Module path
   - Usage instructions
4. Import from `app.shared` modules
5. Use async/await for I/O operations
6. Follow coding standards in [docs/architecture/coding-standards.md](../../docs/architecture/coding-standards.md)

**Example template**:
```python
#!/usr/bin/env python3
"""
Test Description

Part of lightrag-cv application workflows.
Module: app.tests.test_example

Tests specific functionality.

Usage:
    export PYTHONPATH=/home/ubuntu/dev/lightrag-cv
    python -m app.tests.test_example
"""

import asyncio
from app.shared.config import settings

async def test_something():
    # Your test code here
    pass

if __name__ == "__main__":
    asyncio.run(test_something())
```
