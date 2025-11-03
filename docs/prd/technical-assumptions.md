# Technical Assumptions

## Repository Structure: Monorepo

**Decision**: Single repository containing all services (Docling, LightRAG, MCP Server, PostgreSQL configuration), documentation, and deployment artifacts.

**Rationale**: POC scope benefits from simplified coordination and versioning. All components are tightly coupled for this specific use case, making a monorepo more efficient for rapid iteration. The brief's repository structure diagram shows all services under a single `lightrag-cv/` root.

**Structure**:
```
lightrag-cv/
├── docker-compose.yml
├── .env.example
├── services/
│   ├── docling/          # Docling service container
│   ├── lightrag/         # LightRAG server config
│   ├── mcp-server/       # MCP server implementation
│   └── postgres/         # PostgreSQL configuration
├── data/
│   ├── cigref/           # CIGREF reference PDF
│   └── cvs/              # Test CV files
├── docs/                 # Documentation
└── scripts/              # Setup and utility scripts
```

## Service Architecture

**Microservices architecture within containerized environment**

**Core Services**:
- **Docling Service**: Standalone Python service exposing REST API for document processing with optional GPU acceleration
- **LightRAG Server**: Python-based RAG engine from HKUDS/LightRAG with API support
- **MCP Server**: Protocol server (Python or TypeScript) exposing LightRAG-CV tools to OpenWebUI
- **PostgreSQL Database**: Unified persistence with pgvector (0.5.0+) and Apache AGE extensions

**External Dependencies**:
- **Ollama**: External LLM inference server (host or separate container) providing:
  - `qwen3:8b` for generation
  - `bge-m3:latest` for embeddings (1024-dimensional)
  - `xitao/bge-reranker-v2-m3` for reranking
- **OpenWebUI**: External service providing user interface

**Communication Flow**:
1. User queries OpenWebUI in natural language
2. OpenWebUI invokes MCP Server tools via MCP protocol
3. MCP Server translates to LightRAG API calls
4. LightRAG queries PostgreSQL (vectors + graphs) and generates response via Ollama
5. MCP Server formats results and returns to OpenWebUI
6. OpenWebUI renders conversational response with candidate recommendations

**Container Orchestration**: Docker Compose with internal networking, configurable ports via .env, and named volumes for PostgreSQL persistence.

## Testing Requirements

**POC-appropriate testing strategy**:

- **Manual Testing Primary**: Manual evaluation of 20 natural language test queries with recruiter/hiring manager validation
- **Integration Testing**: End-to-end workflow testing (CV upload → processing → query → results) to validate MCP-OpenWebUI-LightRAG integration
- **Data Quality Validation**: Manual inspection of parsed CIGREF content and sample CVs to verify extraction accuracy
- **Performance Baseline**: Manual timing of query response times (target <10s for POC)
- **Stability Testing**: 48+ hour run test to validate container stability

**No automated test harness for MVP**—focus on working functionality over test infrastructure. Phase 2 would add:
- Unit tests for MCP server tool logic
- Integration tests for LightRAG PostgreSQL storage
- Automated query quality metrics

**Rationale**: POC timeline (8-12 weeks) and single-developer assumption make automated testing infrastructure a poor ROI. Manual validation with test users provides sufficient quality signal for go/no-go decision.

## Additional Technical Assumptions and Requests

### Programming Languages & Frameworks

> 📋 **Complete tech stack details**: See [Architecture Tech Stack](../architecture/tech-stack.md) for the definitive technology selection with exact versions.

**Summary for PRD context:**

- **MCP Server**: Python (using `mcp` library) OR TypeScript (using `@modelcontextprotocol/sdk`)
  - **Preference**: Python for consistency with LightRAG and Docling ecosystems
  - **Decision point**: Confirm OpenWebUI MCP transport compatibility (stdio vs SSE) during Week 1 spike

- **LightRAG Integration**: Python client for LightRAG REST API (documented in `lightrag/api/README.md`)

- **Docling Service**: Python service wrapping Docling library with REST endpoints

### Database Configuration

> 📋 **Database schema details**: See [Architecture Database Schema](../architecture/database-schema.md) for complete schema definitions.

- **PostgreSQL 16+** with required extensions:
  - `pgvector` 0.5.0+ for vector similarity search
  - `Apache AGE` for graph database capabilities

- **LightRAG Storage Adapters**: Use PostgreSQL-based storage implementations:
  - `PGKVStorage` (key-value store)
  - `PGVectorStorage` (embeddings)
  - `PGGraphStorage` (entity relationships)
  - `PGDocStatusStorage` (document tracking)

- **Connection Management**: Direct connections for POC; consider pgBouncer for Phase 2 if concurrent load requires pooling

### Deployment & Infrastructure

> 📋 **Deployment details**: See [Architecture Infrastructure and Deployment](../architecture/infrastructure-and-deployment.md) for complete Docker Compose configuration.

- **Target Platform**: Docker Desktop on Windows WSL2 (Ubuntu or compatible distro)
- **Container Runtime**: Docker Compose v2.x
- **GPU Support**: Optional NVIDIA GPU acceleration via Docker Compose profiles (requires nvidia-docker runtime)
  ```bash
  # Run with GPU
  docker compose --profile gpu up

  # Run CPU-only
  docker compose up
  ```

- **Port Configuration**: All ports configurable via .env to avoid conflicts:
  ```env
  MCP_SERVER_PORT=3000
  LIGHTRAG_API_PORT=9621
  DOCLING_API_PORT=8000
  POSTGRES_PORT=5432
  ```

- **Networking**: Single Docker network for inter-service communication; only MCP server port exposed to host

- **Volumes**:
  - Named volumes for PostgreSQL data persistence
  - Bind mounts for configuration files and data directories

### Security & Privacy

- **Local-Only Processing**: All LLM inference, embedding generation, and data processing performed locally—no cloud API calls (critical for CV PII handling)
- **Network Isolation**: Services communicate via internal Docker network
- **Credential Management**: Database passwords and API keys in `.env` file (NOT committed to repo; use `.env.example` template)
- **No Authentication for POC**: Single-user assumption; authentication deferred to Phase 2 via OpenWebUI's existing auth

### Data Processing

- **Document Formats Supported**: PDF and DOCX for CVs; PDF for CIGREF reference
- **Chunking Strategy**: Docling HybridChunker for intelligent content segmentation
- **Embedding Dimensionality**: 1024-dimensional vectors (bge-m3)
- **Graph Entity Types**: Skills, experiences, certifications, CIGREF missions, activities, deliverables, performance indicators
- **Language Support**: English only for POC

### LLM Configuration

- **Context Window**: `OLLAMA_LLM_NUM_CTX=40960` (40K tokens for qwen3:8b)
- **Model Quantization**: Use default Ollama quantization (likely Q4_K_M for 8B models)
- **Inference Mode**: External Ollama service accessed via `http://host.docker.internal:11434`
- **Reranking**: bge-reranker-v2-m3 for result reranking to improve top-k precision

### MCP Protocol

- **Protocol Version**: Latest stable MCP specification from modelcontextprotocol.io
- **Transport**: TBD based on OpenWebUI compatibility testing (Week 1 spike)—likely stdio or SSE
- **Tool Discovery**: MCP server must implement tool discovery for OpenWebUI to enumerate available capabilities
- **Resource Serving**: Structured match explanations exposed as MCP resources

### Logging & Observability

- **POC Logging**: Docker Compose logs (`docker compose logs -f`) sufficient for debugging
- **Error Handling**: Basic error messages returned via MCP protocol; no centralized logging infrastructure
- **Monitoring**: Manual observation during test sessions; no metrics dashboard for POC
- **Phase 2**: Would add structured logging (ELK stack or similar), metrics (Prometheus/Grafana), and distributed tracing

### Performance Considerations

- **Query Timeout**: 10 second target for POC (acceptable for validation; production target <3s)
- **Batch Processing**: One CV at a time for POC; no batch ingestion pipeline
- **Index Updates**: Assume full knowledge base rebuild for POC; incremental updates deferred to Phase 2
- **Concurrent Users**: Single user for POC; architecture should support 5-10 concurrent for Phase 2

### Development Workflow

- **Environment Setup**: Scripted setup via `scripts/setup.sh` or similar
- **Configuration Management**: `.env` file for all configurable parameters with `.env.example` template
- **Documentation**: Focus on setup instructions, architecture overview, and usage examples—minimal API documentation for POC
- **Version Control**: Git repository with standard `.gitignore` (exclude `.env`, data files, PostgreSQL volumes)

---
