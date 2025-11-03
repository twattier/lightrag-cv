# External APIs

## Ollama API

**Purpose:** Local LLM inference server providing text generation, embedding generation, and reranking capabilities for LightRAG's RAG operations.

**Documentation:** https://github.com/ollama/ollama/blob/main/docs/api.md

**Base URL(s):**
- From Docker containers: `http://host.docker.internal:11434`
- From host machine: `http://localhost:11434`

**Authentication:** None (local deployment, no authentication required)

**Rate Limits:** None (self-hosted, limited only by hardware resources)

## Key Endpoints Used

### 1. Generate (Text Completion)

**Endpoint:** `POST /api/generate`

**Usage in LightRAG:**
- Entity extraction from document chunks
- Relationship inference between entities
- Query understanding and expansion
- Response generation (combining retrieved chunks)

**Configuration:**
```python
OLLAMA_LLM_MODEL=qwen3:8b
OLLAMA_LLM_NUM_CTX=40960  # 40K context window
OLLAMA_LLM_TEMPERATURE=0.7
```

### 2. Embeddings

**Endpoint:** `POST /api/embeddings`

**Usage in LightRAG:**
- Embedding document chunks during ingestion (PGVectorStorage)
- Embedding user queries for vector similarity search
- All embeddings use same model (bge-m3) for consistency

**Configuration:**
```python
OLLAMA_EMBEDDING_MODEL=bge-m3:latest
EMBEDDING_DIMENSION=1024  # Must match pgvector schema
```

### 3. Required Models

```bash
ollama pull qwen3:8b
ollama pull bge-m3:latest
ollama pull xitao/bge-reranker-v2-m3
```

## Integration Notes

**Connection from Docker Containers:**

```python
# services/lightrag/.env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

**Docker Compose Configuration:**
```yaml
services:
  lightrag:
    environment:
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
    extra_hosts:
      - "host.docker.internal:host-gateway"  # For Linux compatibility
```

**Performance Expectations (approximate, hardware-dependent):**

| Operation | Model | Expected Time | Notes |
|-----------|-------|---------------|-------|
| Embedding generation | bge-m3 | 50-200ms | GPU: ~50ms, CPU: ~200ms |
| Text generation | qwen3:8b | 2-5s | For entity extraction |
| Text generation (40K context) | qwen3:8b | 10-20s | Full context queries |

**NFR1 Validation (<10s query target):**
- Embedding: ~500ms
- Generation: ~5s
- Retrieval + formatting: ~3-4s
- **Total: ~8-10s** (meets POC target)

---
