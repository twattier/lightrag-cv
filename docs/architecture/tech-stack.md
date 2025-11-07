# Tech Stack

⚠️ **CRITICAL SECTION** ⚠️
This is the **DEFINITIVE technology selection** for LightRAG-CV. All development, testing, and deployment MUST use these exact versions. This table is the **single source of truth** - no deviations without architecture revision.

> 📋 **Requirements Context**: See [PRD Requirements](../prd/requirements.md) for the functional and non-functional requirements this tech stack addresses.

## Cloud Infrastructure

**Platform:** Local Development (No Cloud Provider)
**Deployment Host:** Windows WSL2 (Ubuntu 22.04 LTS recommended) with Docker Desktop
**Orchestration:** Docker Compose v2.x
**Networking:** Single Docker bridge network (`lightrag-cv-network`)

**Rationale:** POC scope requires local-only processing for CV data privacy (no cloud APIs per NFR9). WSL2 provides Linux container support on Windows development machines. Docker Compose sufficient for single-user POC; Kubernetes migration path available for Phase 2.

## Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|-----------|---------|---------|-----------|
| **Container Runtime** | Docker Desktop | 4.25+ | Container orchestration on WSL2 | Native Windows WSL2 integration; GPU support via nvidia-docker runtime; team familiarity |
| **Orchestration** | Docker Compose | 2.23+ | Multi-container application definition | Sufficient for POC scope; declarative configuration; profile support for GPU/CPU modes |
| **Primary Language** | Python | 3.11.x | Service implementation language | LightRAG and Docling ecosystem compatibility; strong AI/ML library support; type hints for maintainability |
| **Database** | PostgreSQL | 16.1 | Unified persistence layer | Required for pgvector 0.5.0+ compatibility; stable LTS; Apache AGE extension support |
| **Vector Extension** | pgvector | 0.5.1 | Vector similarity search | Native PostgreSQL vector operations; 1024-dim embedding support for bge-m3; LightRAG PGVectorStorage requirement |
| **Graph Extension** | Apache AGE | 1.5.0 | Graph database capabilities | Cypher query support; LightRAG PGGraphStorage requirement; OpenCypher compatibility |
| **RAG Engine** | LightRAG (HKUDS) | 0.0.0.post8 | Hybrid vector-graph retrieval | Core POC technology; PostgreSQL storage adapter support; hybrid mode selection; proven architecture |
| **Document Processing** | Docling | 1.16.2 | PDF/DOCX parsing with structure | HybridChunker for intelligent segmentation; table/list extraction; optional GPU acceleration |
| **MCP Server Language** | Python | 3.11.x | MCP protocol implementation | Ecosystem consistency with other services; Python MCP SDK availability |
| **MCP SDK** | mcp (Python) | 0.9.0 | Model Context Protocol library | Official Python SDK; OpenWebUI compatibility (validate in Week 1 spike); simpler than TypeScript for POC |
| **LLM Inference** | Ollama | 0.3.12 | Local LLM serving | Multi-model support; efficient quantization; host.docker.internal access from containers |
| **Generation Model** | qwen3:8b | latest | Query response generation | 40K context window (OLLAMA_LLM_NUM_CTX=40960); multilingual but English-optimized; 8B param balances quality/speed |
| **Embedding Model** | bge-m3 | latest | 1024-dim vector embeddings | Multilingual (English-optimized); 1024-dim matches pgvector config; SOTA semantic similarity |
| **Reranking Model** | bge-reranker-v2-m3 | latest (xitao/bge-reranker-v2-m3) | Result reranking | Improves precision@5 (NFR4 target: 70%); cross-encoder architecture; compatible with bge-m3 |
| **Python Package Manager** | pip | 23.3+ | Dependency management | Standard Python tooling; requirements.txt per service; virtual environments in containers |
| **Web Framework (Docling)** | FastAPI | 0.109.0 | REST API framework | Async support; auto OpenAPI docs; type validation via Pydantic; modern Python standard |
| **Web Framework (LightRAG)** | FastAPI | 0.109.0 | REST API framework | Consistency with Docling; LightRAG API module compatibility; excellent async I/O for embeddings |
| **HTTP Client** | httpx | 0.26.0 | Async HTTP requests | MCP→LightRAG, LightRAG→Ollama communication; async/await support; connection pooling |
| **PostgreSQL Client** | psycopg3 | 3.1.16 | Database driver | PostgreSQL 16 compatibility; async support; native prepared statements |
| **Logging** | Python logging (stdlib) | 3.11.x | Service logging | Sufficient for POC; Docker Compose log aggregation; structured JSON logs optional |
| **Environment Config** | python-dotenv | 1.0.0 | .env file loading | Centralized configuration; prevents hardcoded credentials; Docker Compose variable substitution |
| **Testing Framework** | pytest | 7.4.3 | Manual test scripts | Industry standard; fixture support; minimal for POC (manual testing primary per PRD) |
| **Code Quality** | ruff | 0.1.9 | Linting and formatting | Fast Python linter/formatter; replaces Black+Flake8+isort; minimal config |
| **Type Checking** | mypy | 1.8.0 | Static type analysis | Catches type errors early; enforces type hints; optional for POC |
| **GPU Runtime** | nvidia-docker | latest | GPU acceleration (optional) | Enables Docling GPU mode via --profile gpu; requires NVIDIA drivers on host |
| **IaC Tool** | Docker Compose files | 2.23+ | Infrastructure as code | Declarative service definitions; version controlled; sufficient for POC |
| **CI/CD** | N/A | N/A | Continuous integration | **POC Scope:** Manual deployment via docker compose up; GitHub Actions deferred to Phase 2 |
| **Monitoring** | Docker Compose logs | N/A | Container log aggregation | `docker compose logs -f` sufficient for POC; Prometheus/Grafana deferred to Phase 2 |
| **Secret Management** | .env files | N/A | Local secrets | .env for development; acceptable for single-user POC; Vault/SOPS for Phase 2 |

## Multi-Provider LLM Support (Epic 2.5+)

**Abstraction Layer**: `app/shared/llm_client.py` provides unified OpenAI-compatible interface for multiple LLM providers.

### Supported Providers

| Provider | Type | Use Case | Configuration |
|----------|------|----------|---------------|
| **Ollama** | Local | Development, privacy-sensitive workloads | `LLM_PROVIDER=ollama` |
| **OpenAI-compatible APIs** | Remote | Production, cloud deployment | `LLM_PROVIDER=openai` or `LLM_PROVIDER=litellm` |

### Configuration Variables

All application scripts use these environment variables (configured in `.env`):

| Variable | Default | Purpose | Example |
|----------|---------|---------|---------|
| `LLM_PROVIDER` | `ollama` | Provider selection (ollama, openai, litellm) | `ollama` |
| `LLM_BASE_URL` | `http://localhost:11434/v1` | Provider API endpoint | `http://localhost:11434/v1` |
| `LLM_MODEL` | `qwen2.5:7b` | Model identifier | `qwen2.5:7b` |
| `LLM_API_KEY` | `ollama` | API key (ignored for Ollama) | `sk-...` for OpenAI |
| `LLM_TEMPERATURE` | `0.0` | Generation temperature | `0.0` (deterministic) |

### Backward Compatibility

Legacy `OLLAMA_*` environment variables are still supported for backward compatibility:

```bash
# Legacy (still works)
OLLAMA_HOST=http://localhost:11434
OLLAMA_LLM_MODEL=qwen2.5:7b

# Modern (Epic 2.5+, preferred)
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen2.5:7b
```

**Migration Strategy**: New scripts use `LLM_*` variables. Legacy scripts continue to work with `OLLAMA_*` variables until deprecated in Phase 2.

**Usage**: See [Coding Standards](coding-standards.md) for LLM client usage patterns and [app/README.md](../../app/README.md) for detailed configuration examples.

---
