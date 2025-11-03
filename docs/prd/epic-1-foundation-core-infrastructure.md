# Epic 1: Foundation & Core Infrastructure

> 🎯 **Development Artifacts**: [Epic 1 Card](../epics/epic-1.md) | [Stories 1.1-1.7](../stories/README.md#epic-1-foundation--core-infrastructure-7-stories)
>

> 📋 **Architecture References**:
> - [Infrastructure and Deployment](../architecture/infrastructure-and-deployment.md) - Docker Compose configuration
> - [Source Tree](../architecture/source-tree.md) - Repository structure
> - [Database Schema](../architecture/database-schema.md) - PostgreSQL setup
> - [Components](../architecture/components.md) - Service definitions

**Epic Goal**: Establish containerized development environment with PostgreSQL storage (pgvector + Apache AGE), basic LightRAG integration, Ollama connectivity validation, and project scaffolding that enables subsequent feature development while delivering a working health-check endpoint to verify all services are operational.

## Story 1.1: Project Repository Setup and Docker Compose Scaffold

**As a** developer,
**I want** a structured repository with Docker Compose configuration scaffolding,
**so that** I have a foundation for organizing services and can begin local development.

### Acceptance Criteria

1. Repository structure created matching the architecture specification:
   - `/services/docling/`, `/services/lightrag/`, `/services/mcp-server/`, `/services/postgres/`
   - `/data/cigref/`, `/data/cvs/`
   - `/docs/`, `/scripts/`
   - Root-level `docker-compose.yml`, `.env.example`, `.gitignore`, `README.md`

2. `.env.example` template includes all required configuration variables:
   - LLM configuration (Ollama binding, model names, context size)
   - Embedding configuration (model, dimensions)
   - Reranking configuration
   - PostgreSQL connection details
   - Service ports (MCP, LightRAG, Docling, PostgreSQL)

3. `.gitignore` properly excludes `.env`, data files, PostgreSQL volumes, Python `__pycache__`, and other generated artifacts

4. `README.md` includes setup instructions for copying `.env.example` to `.env` and basic Docker Compose usage

5. `docker-compose.yml` scaffold created with service definitions (empty/placeholder initially) for: `postgres`, `lightrag`, `docling`, `mcp-server`

## Story 1.2: PostgreSQL with pgvector and Apache AGE Setup

**As a** developer,
**I want** PostgreSQL 16+ running in Docker with pgvector and Apache AGE extensions installed,
**so that** LightRAG can store vectors and graphs in a unified database.

### Acceptance Criteria

1. PostgreSQL 16+ service defined in `docker-compose.yml` with:
   - Named volume for data persistence (`postgres_data`)
   - Port mapping configurable via `.env` (default 5432)
   - Health check configured to verify database readiness

2. Custom Dockerfile or init scripts in `/services/postgres/` that:
   - Install `pgvector` extension (0.5.0+)
   - Install `Apache AGE` extension
   - Create `lightrag_cv` database
   - Enable both extensions on the database

3. PostgreSQL service starts successfully with `docker compose up postgres`

4. Can connect to PostgreSQL from host using credentials from `.env` and verify extensions:
   ```sql
   \dx  -- Shows pgvector and age extensions
   SELECT extname, extversion FROM pg_extension;
   ```

5. PostgreSQL service persists data across container restarts (data volume working correctly)

## Story 1.3: LightRAG Server Integration with PostgreSQL Storage

**As a** developer,
**I want** LightRAG server running with PostgreSQL storage adapters configured,
**so that** I can ingest documents and perform basic retrieval operations.

### Acceptance Criteria

1. LightRAG service defined in `docker-compose.yml` with:
   - Python runtime environment
   - Dependencies installed (LightRAG from HKUDS/LightRAG, PostgreSQL drivers)
   - Port mapping for REST API (configurable via `.env`, default 9621)
   - Environment variables for PostgreSQL connection and Ollama endpoints
   - Depends on `postgres` service

2. LightRAG configured to use PostgreSQL storage adapters:
   - `PGKVStorage` for key-value store
   - `PGVectorStorage` for embeddings
   - `PGGraphStorage` for graph relationships
   - `PGDocStatusStorage` for document tracking

3. LightRAG service starts successfully and connects to PostgreSQL (no connection errors in logs)

4. LightRAG REST API is accessible from host at configured port

5. Basic health check endpoint returns success status indicating LightRAG is operational

## Story 1.4: Ollama Integration Validation

**As a** developer,
**I want** to validate connectivity to external Ollama service with required models,
**so that** I confirm LLM generation, embeddings, and reranking will work for subsequent epics.

### Acceptance Criteria

1. Documentation in `README.md` or `/docs/setup.md` instructs users to:
   - Install Ollama on host or separate container
   - Pull required models: `qwen3:8b`, `bge-m3:latest`, `xitao/bge-reranker-v2-m3`
   - Verify Ollama is accessible at `http://host.docker.internal:11434` from containers

2. Simple validation script or manual test procedure that:
   - Calls Ollama API to generate text with `qwen3:8b`
   - Calls Ollama API to generate embeddings with `bge-m3` (verify 1024 dimensions)
   - Confirms models are loaded and responding

3. LightRAG service configuration includes Ollama endpoints:
   - `LLM_BINDING_HOST=http://host.docker.internal:11434`
   - `EMBEDDING_BINDING_HOST=http://host.docker.internal:11434`
   - `RERANK_BINDING_HOST=http://host.docker.internal:11434`

4. LightRAG can successfully call Ollama for test generation and embedding (verified via logs or test request)

5. Documentation notes expected response times and model loading behavior (first request may be slow)

## Story 1.5: Docling Service Scaffold with GPU Profile Support

**As a** developer,
**I want** Docling service defined in Docker Compose with optional GPU acceleration profile,
**so that** subsequent epics can integrate document parsing with flexible performance options.

### Acceptance Criteria

1. Docling service defined in `docker-compose.yml` with:
   - Python runtime environment
   - Docling library dependencies installed
   - Port mapping for REST API (configurable via `.env`, default 8000)
   - CPU-only configuration as default

2. Docker Compose GPU profile defined that:
   - Adds NVIDIA GPU runtime configuration to Docling service
   - Can be activated with `docker compose --profile gpu up`
   - Includes documentation in `README.md` about GPU requirements (nvidia-docker runtime)

3. Docling service starts successfully in CPU-only mode with `docker compose up docling`

4. If GPU available, Docling service starts successfully with `docker compose --profile gpu up docling`

5. Basic health check endpoint on Docling service returns success status

6. Documentation includes note that GPU acceleration is optional and CPU fallback is fully functional

## Story 1.6: Infrastructure Health Check Endpoint

**As a** developer or operator,
**I want** a consolidated health check endpoint that reports status of all services,
**so that** I can quickly verify the entire stack is operational.

### Acceptance Criteria

1. Simple health check script or minimal web endpoint (can be part of MCP server scaffold or standalone) that:
   - Checks PostgreSQL connectivity and extension availability
   - Checks LightRAG API responsiveness
   - Checks Docling API responsiveness
   - Checks Ollama connectivity
   - Returns JSON status report with each service's health

2. Health check accessible via HTTP request (e.g., `http://localhost:3000/health`) or via script execution

3. Health check returns success when all services are up and returns partial status with error details when services are down

4. Documentation in `README.md` includes instructions for running health check to verify setup

5. Health check validates that PostgreSQL extensions (pgvector, AGE) are properly installed

## Story 1.7: Development Setup Documentation and Scripts

**As a** developer,
**I want** clear setup documentation and automated setup scripts,
**so that** I can quickly provision the development environment on Windows WSL2.

### Acceptance Criteria

1. `/docs/setup.md` or expanded `README.md` includes:
   - Prerequisites (Docker Desktop, WSL2, minimum RAM/disk, optional GPU requirements)
   - Step-by-step setup instructions (clone repo, copy `.env.example`, configure `.env`, start services)
   - Troubleshooting section for common issues (port conflicts, PostgreSQL extension errors, Ollama connectivity)
   - Architecture diagram showing service relationships

2. Optional setup script `/scripts/setup.sh` that:
   - Checks prerequisites (Docker, Docker Compose versions)
   - Prompts for `.env` configuration or copies `.env.example` to `.env`
   - Validates required Ollama models are pulled
   - Runs initial `docker compose up` or validation

3. Documentation includes instructions for:
   - Starting all services: `docker compose up -d`
   - Starting with GPU: `docker compose --profile gpu up -d`
   - Viewing logs: `docker compose logs -f [service]`
   - Stopping services: `docker compose down`
   - Resetting database: `docker compose down -v` (removes volumes)

4. Documentation includes expected startup time and first-run behavior (Ollama model loading, PostgreSQL initialization)

5. Quick-start section gets a developer from zero to health check passing in under 15 minutes (assuming prerequisites installed)

---
