# Story 2.9.6: Local Reranker Service with Jina-Reranker-v3

## Status

**Cancelled**

---

## Story

**As a** developer deploying LightRAG-CV,
**I want** a local reranker service using the Hugging Face jina-reranker-v3 model,
**so that** I can enable LightRAG's reranking feature without external API dependencies or rate limits.

---

## Background

### Current Problem

LightRAG supports reranking to improve retrieval quality, but:
- The `RERANK_BINDING=ollama` configuration is **not supported** by LightRAG
- Supported bindings are: `jina`, `cohere`, `aliyun`, or empty (disabled)
- External APIs (Jina, Cohere) have rate limits and require API keys
- Local inference allows privacy-sensitive deployments

### Solution

Deploy a local FastAPI service that:
1. Loads `jinaai/jina-reranker-v3` from Hugging Face
2. Exposes a Jina-compatible `/v1/rerank` endpoint
3. Runs as a Docker container alongside existing services
4. Integrates with LightRAG using `RERANK_BINDING=jina`

### Target Architecture

```
+---------------------------------------------+
|           reranker container                |
|  +---------------------------------------+  |
|  |  FastAPI server (port 8182)           |  |
|  |    - POST /v1/rerank                  |  |
|  |    - GET /health                      |  |
|  |                                       |  |
|  |  jinaai/jina-reranker-v3 model        |  |
|  |    (HuggingFace Transformers)         |  |
|  +---------------------------------------+  |
+---------------------------------------------+
              |
              v
+---------------------------------------------+
|           lightrag container                |
|  RERANK_BINDING=jina                        |
|  RERANK_BINDING_HOST=http://reranker:8182   |
+---------------------------------------------+
```

---

## Acceptance Criteria

### AC1: Reranker Service Created

1. Service directory created at `services/reranker/`
2. FastAPI application with Jina-compatible API
3. Model loaded at startup (not per-request)
4. Supports `query`, `documents`, and `top_n` parameters
5. Returns results in Jina API format

### AC2: Dockerfile Created

1. Based on Python 3.11-slim
2. Installs transformers, torch, fastapi, uvicorn
3. Pre-downloads model during build (reduces startup time)
4. Supports both CPU and GPU modes
5. Exposes port 8182

### AC3: Docker Compose Integration

1. New `reranker` service added to docker-compose.yml
2. Connected to `lightrag-cv-network`
3. Health check endpoint configured
4. Optional GPU profile support
5. Depends on nothing (standalone service)

### AC4: Environment Configuration Updated

1. `.env.example` updated with correct reranker config
2. Comments explain supported bindings (not ollama)
3. Default configuration works out-of-box
4. GPU/CPU mode configurable

### AC5: LightRAG Integration Verified

1. LightRAG connects to reranker service
2. Reranking works during query operations
3. No errors in lightrag container logs
4. Performance is acceptable (< 2s per rerank call)

### AC6: Documentation Updated

1. README updated with reranker setup
2. Architecture docs reference reranker service
3. Troubleshooting guide for common issues

---

## Tasks / Subtasks

### Task 1: Create Reranker Service (AC: 1, 2)

- [ ] **Subtask 1.1: Create service directory structure**
  - [ ] Create `services/reranker/` directory
  - [ ] Create `services/reranker/src/` for source code
  - [ ] Create `services/reranker/requirements.txt`

- [ ] **Subtask 1.2: Implement FastAPI application**
  - [ ] Create `services/reranker/src/main.py`
  - [ ] Implement `/v1/rerank` POST endpoint
  - [ ] Implement `/health` GET endpoint
  - [ ] Add Pydantic models for request/response
  - [ ] Load model at startup with lifespan handler

- [ ] **Subtask 1.3: Create Dockerfile**
  - [ ] Create `services/reranker/Dockerfile`
  - [ ] Install dependencies
  - [ ] Pre-download model during build
  - [ ] Configure uvicorn CMD

### Task 2: Docker Compose Integration (AC: 3)

- [ ] **Subtask 2.1: Add reranker service**
  - [ ] Add service definition to docker-compose.yml
  - [ ] Configure network and ports
  - [ ] Add health check
  - [ ] Set resource limits (memory)

- [ ] **Subtask 2.2: Optional GPU support**
  - [ ] Create docker-compose.gpu.yml override (if needed)
  - [ ] Document GPU requirements

### Task 3: Environment Configuration (AC: 4)

- [ ] **Subtask 3.1: Update .env.example**
  - [ ] Fix RERANK_BINDING (remove ollama, use jina)
  - [ ] Update RERANK_BINDING_HOST to reranker service
  - [ ] Add comments explaining supported bindings
  - [ ] Add RERANKER_MODEL variable

### Task 4: Integration Testing (AC: 5)

- [ ] **Subtask 4.1: Build and start services**
  - [ ] Build reranker container
  - [ ] Start all services
  - [ ] Verify reranker health endpoint

- [ ] **Subtask 4.2: Test reranker directly**
  - [ ] Test `/v1/rerank` endpoint with curl
  - [ ] Verify response format matches Jina API
  - [ ] Measure response time

- [ ] **Subtask 4.3: Test LightRAG integration**
  - [ ] Query LightRAG with reranking enabled
  - [ ] Verify no errors in logs
  - [ ] Compare results with/without reranking

### Task 5: Documentation (AC: 6)

- [ ] **Subtask 5.1: Update project documentation**
  - [ ] Update README with reranker setup
  - [ ] Add reranker to architecture diagram
  - [ ] Document troubleshooting steps

---

## Dev Notes

### Jina Reranker API Format

The local service must match Jina's API format for LightRAG compatibility:

**Request:**
```json
POST /v1/rerank
{
  "query": "What are the benefits of...",
  "documents": ["doc1 text", "doc2 text", "doc3 text"],
  "top_n": 3
}
```

**Response:**
```json
{
  "results": [
    {
      "index": 2,
      "relevance_score": 0.95,
      "document": {"text": "doc3 text"}
    },
    {
      "index": 0,
      "relevance_score": 0.82,
      "document": {"text": "doc1 text"}
    }
  ]
}
```

### Model Details

- **Model**: `jinaai/jina-reranker-v3`
- **Source**: https://huggingface.co/jinaai/jina-reranker-v3
- **Size**: ~1.5GB (downloads on first build)
- **Context**: Supports long documents
- **Languages**: Multilingual

### FastAPI Implementation Pattern

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModel
import torch

# Pydantic models
class RerankRequest(BaseModel):
    query: str
    documents: list[str]
    top_n: int | None = None

class DocumentResult(BaseModel):
    text: str

class RerankResult(BaseModel):
    index: int
    relevance_score: float
    document: DocumentResult

class RerankResponse(BaseModel):
    results: list[RerankResult]

# Global model reference
model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    # Load model at startup
    model = AutoModel.from_pretrained(
        'jinaai/jina-reranker-v3',
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        trust_remote_code=True,
    )
    model.eval()
    yield
    # Cleanup (if needed)

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/v1/rerank", response_model=RerankResponse)
async def rerank(request: RerankRequest):
    results = model.rerank(
        request.query,
        request.documents,
        top_n=request.top_n
    )

    return RerankResponse(
        results=[
            RerankResult(
                index=r["index"],
                relevance_score=r["relevance_score"],
                document=DocumentResult(text=r["document"])
            )
            for r in results
        ]
    )
```

### Dockerfile Pattern

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download model during build (faster startup)
RUN python -c "from transformers import AutoModel; AutoModel.from_pretrained('jinaai/jina-reranker-v3', trust_remote_code=True)"

# Copy application
COPY src/ ./src/

EXPOSE 8182

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8182"]
```

### Docker Compose Service

```yaml
reranker:
  build:
    context: .
    dockerfile: services/reranker/Dockerfile
  container_name: lightrag-cv-reranker
  ports:
    - "8182:8182"
  networks:
    - lightrag-cv-network
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8182/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 60s  # Model loading takes time
  deploy:
    resources:
      limits:
        memory: 4G  # Model requires ~2-3GB
  restart: unless-stopped
```

### Environment Variables

```bash
# Reranking Configuration
# Supported bindings: jina, cohere, aliyun (NOT ollama)
# Leave empty to disable reranking
RERANK_BINDING=jina
RERANK_BINDING_HOST=http://reranker:8182
RERANK_BINDING_API_KEY=dummy
RERANK_MODEL=jina-reranker-v3
```

### Resource Requirements

| Mode | RAM | GPU VRAM | Notes |
|------|-----|----------|-------|
| CPU | 4GB | N/A | Slower inference (~2-5s per call) |
| GPU | 2GB | 2GB | Fast inference (~0.2-0.5s per call) |

### Testing Commands

```bash
# Build reranker
docker compose build reranker

# Start reranker
docker compose up -d reranker

# Check health
curl http://localhost:8182/health

# Test rerank endpoint
curl -X POST http://localhost:8182/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python developer with cloud experience",
    "documents": [
      "Senior Java developer with 10 years experience",
      "Python engineer specializing in AWS and GCP",
      "Frontend developer with React expertise"
    ],
    "top_n": 2
  }'

# Check LightRAG logs for reranking
docker compose logs lightrag | grep -i rerank
```

### Rollback Plan

If issues arise:
1. Set `RERANK_BINDING=` (empty) in `.env` to disable reranking
2. Restart lightrag service
3. Remove reranker service from docker-compose.yml if needed

---

## Definition of Done

- [ ] Reranker service created with Jina-compatible API
- [ ] Dockerfile builds successfully
- [ ] Container starts and loads model
- [ ] Health endpoint returns healthy status
- [ ] `/v1/rerank` endpoint works correctly
- [ ] Docker Compose integration complete
- [ ] LightRAG connects to reranker without errors
- [ ] `.env.example` updated with correct configuration
- [ ] Documentation updated

---

## Risk and Compatibility Check

### Risk Assessment

**Primary Risk:** Model loading time and memory usage

**Mitigation:**
- Pre-download model during Docker build
- Set appropriate memory limits
- Add health check with long start_period
- Document resource requirements

**Secondary Risk:** API format mismatch with LightRAG expectations

**Mitigation:**
- Test with actual LightRAG rerank calls
- Review LightRAG source code for expected format
- Add response format logging for debugging

### Compatibility Verification

- [ ] No breaking changes to existing services
- [ ] LightRAG configuration uses supported binding type
- [ ] Docker network connectivity verified
- [ ] Resource limits don't impact other services

---

## References

- Epic 2.9: [docs/epics/epic-2.9.md](../epics/epic-2.9.md)
- Jina Reranker Model: https://huggingface.co/jinaai/jina-reranker-v3
- LightRAG Reranking: https://github.com/HKUDS/LightRAG
- Docker Compose: [docker-compose.yml](../../docker-compose.yml)

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-11-24 | 1.0 | Story created | Sarah (Product Owner) |

---

## Dev Agent Record

### Agent Model Used

**Primary Model:** (To be filled by dev agent)

### File List

**New Files:**
- (To be filled during implementation)

**Modified Files:**
- (To be filled during implementation)

**Deleted Files:**
- None expected

### Completion Notes

(To be filled by dev agent upon completion)

### Debug Log References

(To be filled if debugging required)

### Change Log

| Date | Change | Files Affected |
|------|--------|----------------|
| | | |

---

**Document Version:** 1.0
**Created:** 2025-11-24
**Author:** Sarah (Product Owner)
**Status:** Draft
