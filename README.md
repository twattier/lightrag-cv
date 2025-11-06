# LightRAG-CV: CV Candidate Search with Hybrid Vector-Graph RAG

A proof-of-concept system for intelligent CV candidate search using LightRAG (hybrid vector-graph retrieval), Docling (document parsing), and local LLM processing via Ollama.

## Overview

LightRAG-CV enables recruiters to find qualified candidates by matching CV profiles against job requirements using advanced RAG techniques. The system processes CVs and reference profiles (CIGREF), stores them in a PostgreSQL database with vector and graph capabilities, and provides intelligent search via an MCP server compatible with OpenWebUI.

## Architecture

- **LightRAG Service**: Hybrid vector-graph retrieval engine (port 9621)
- **Docling Service**: PDF/DOCX document parsing with intelligent chunking (port 8000)
- **MCP Server**: Model Context Protocol server for OpenWebUI integration (port 3000)
- **PostgreSQL**: Database with pgvector (vector search) and Apache AGE (graph storage) (port 5432)
- **Ollama**: Local LLM inference (host machine, port 11434)

## Tech Stack

- **Python**: 3.11.x
- **PostgreSQL**: 16.1 with pgvector 0.5.1 and Apache AGE 1.5.0
- **LightRAG**: v0.0.0.post8 (HKUDS)
- **Docling**: v1.16.2
- **Ollama Models**: qwen3:8b (generation), bge-m3 (embeddings), bge-reranker-v2-m3 (reranking)
- **FastAPI**: 0.109.0
- **Docker Compose**: 2.23+

## Prerequisites

- **Docker Desktop**: 4.25+ with WSL2 integration
- **WSL2**: Ubuntu 22.04 LTS recommended (Windows users)
- **Ollama**: 0.3.12+ installed on host machine
- **RAM**: 16GB minimum (32GB recommended for GPU mode)
- **Disk**: 20GB free space

## Quick Start

### 1. Clone Repository

```bash
git clone <repository-url> lightrag-cv
cd lightrag-cv
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (REQUIRED: set POSTGRES_PASSWORD)
nano .env
```

### 3. Install and Configure Ollama

#### Install Ollama (if not already installed)

```bash
# Download and install Ollama from https://ollama.com
# Or on Linux:
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve
```

#### Pull Required Models

```bash
# On host machine (not in Docker)
# Generation model (40K context window, ~5GB download)
ollama pull qwen3:8b

# Embedding model (1024 dimensions, ~3GB download)
ollama pull bge-m3:latest

# Reranking model (~3GB download)
ollama pull xitao/bge-reranker-v2-m3
```

**Note**: First model pull will download several GB of data. Subsequent pulls are faster.

#### Validate Ollama Setup

```bash
# Run validation script to verify connectivity and models
python3 scripts/validate-ollama.py
```

Expected output:
```
✅ Ollama service is running
✅ qwen3:8b is available
✅ bge-m3:latest is available
✅ xitao/bge-reranker-v2-m3 is available
✅ Generation successful
✅ Embeddings successful (dimension: 1024)
```

**Important Notes**:
- First request to each model may take 30-60 seconds (model loading)
- Subsequent requests typically complete in <1 second
- Ollama must be accessible at `http://localhost:11434` from host
- Containers access Ollama via `http://host.docker.internal:11434`

### 4. Build and Start Services

```bash
# Build Docker images
docker compose build

# Start all services
docker compose up -d

# View logs
docker compose logs -f
```

### 5. Verify Health

```bash
# Run comprehensive health check
./scripts/health-check.sh

# Or use Python version for JSON output
python3 scripts/health-check.py
```

Expected output:
```
========================================
LightRAG-CV Infrastructure Health Check
========================================

Checking PostgreSQL... ✓ OK (connected)
  Checking pgvector extension... ✓ OK
  Checking Apache AGE extension... ✓ OK
Checking LightRAG API... ✓ OK (HTTP 200)
Checking Docling API... ✓ OK (HTTP 200)
Checking Ollama... ✓ OK (HTTP 200)
  Checking qwen3:8b model... ✓ AVAILABLE
  Checking bge-m3 model... ✓ AVAILABLE
  Checking reranker model... ✓ AVAILABLE

========================================
✓ ALL CRITICAL SERVICES HEALTHY
========================================
```

## Docker Compose Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs for specific service
docker compose logs -f lightrag

# Rebuild after code changes
docker compose up -d --build <service-name>

# Reset database (removes volumes)
docker compose down -v
docker compose up -d

# GPU mode (optional, requires nvidia-docker)
docker compose --profile gpu up -d
```

## GPU Acceleration (Optional)

GPU acceleration is **optional** for the Docling service. The system works fully in CPU-only mode.

### Prerequisites for GPU Mode

- **NVIDIA GPU** with CUDA support
- **NVIDIA drivers** installed on host (515.x or newer)
- **nvidia-docker runtime** configured in Docker Desktop

### Enable GPU Profile

```bash
# Start Docling with GPU acceleration
docker compose -f docker-compose.yml -f docker-compose.gpu.yml --profile gpu up -d

# Or use shorthand
docker compose --profile gpu up -d
```

### Verify GPU Access

```bash
# Check GPU is detected inside container
docker compose exec docling nvidia-smi

# Check Docling health endpoint reports GPU
curl http://localhost:8000/health
# Expected: {"status":"healthy","gpu_available":true}
```

### Performance Notes

- **CPU Mode**: Fully functional, ~2-5 seconds per page
- **GPU Mode**: ~10x faster, ~200-500ms per page
- **First Parse**: May be slower due to model loading

**Recommendation**: Use CPU mode for POC. GPU optional for production scale.

## Project Structure

```
lightrag-cv/
├── docker-compose.yml          # Main orchestration file
├── .env.example                # Environment template
├── .env                        # Your config (DO NOT COMMIT)
├── .gitignore                  # Git exclusions
├── README.md                   # This file
│
├── app/                        # Application workflows (NEW)
│   ├── README.md               # App structure & LLM provider docs
│   ├── shared/                 # Shared configuration and utilities
│   │   ├── config.py           # Centralized environment config
│   │   └── llm_client.py       # LLM provider abstraction layer
│   ├── cigref_ingest/          # CIGREF ingestion workflows
│   ├── cv_ingest/              # CV processing workflows
│   └── artifacts/              # SQL queries and dev artifacts
│
├── services/                   # Microservices
│   ├── docling/                # Document parsing service
│   ├── lightrag/               # LightRAG retrieval service
│   ├── mcp-server/             # MCP protocol server
│   └── postgres/               # PostgreSQL with extensions
│
├── data/                       # Data files (not committed)
│   ├── cigref/                 # CIGREF reference profiles
│   ├── cvs/                    # Candidate CVs
│   └── lightrag/               # LightRAG storage
│
├── docs/                       # Documentation
│   ├── prd/                    # Product requirements
│   ├── architecture/           # Technical architecture
│   └── stories/                # User stories
│
└── scripts/                    # Infrastructure scripts
    ├── validate-ollama.py      # Ollama connectivity validation
    ├── health-check.sh         # Comprehensive health check (bash)
    ├── health-check.py         # Comprehensive health check (Python/JSON)
    ├── ingest-cigref.py        # CIGREF profile ingestion (legacy)
    └── ingest-cvs.py           # CV ingestion (legacy)
```

See [app/README.md](app/README.md) for application structure details and LLM provider configuration guide.

## Service Endpoints

- **MCP Server**: http://localhost:3000
- **LightRAG API**: http://localhost:9621
- **Docling API**: http://localhost:8000
- **PostgreSQL**: localhost:5432

## Development Status

This is a **Proof of Concept (POC)** in active development. See [docs/stories/](docs/stories/) for implementation progress.

**Current Epic**: Epic 1 - Foundation & Core Infrastructure

## Documentation

- [Product Requirements](docs/prd/)
- [Architecture](docs/architecture/)
- [User Stories](docs/stories/)
- [Setup Guide](docs/setup.md) - Complete development setup guide

## Troubleshooting

### Port Conflicts
If ports are already in use, configure alternatives in `.env`:
```bash
POSTGRES_PORT=5433
DOCLING_PORT=8001
LIGHTRAG_PORT=9622
MCP_PORT=3001
```

### Ollama Connection Issues

**Symptom**: LightRAG service cannot reach Ollama

**Solution 1** - Verify Ollama is running:
```bash
# Check Ollama is accessible
curl http://localhost:11434/api/tags

# If not running, start Ollama
ollama serve
```

**Solution 2** - Verify models are pulled:
```bash
# Run validation script
python3 scripts/validate-ollama.py

# Or manually check models
ollama list
```

**Solution 3** - Check Docker network connectivity:
```bash
# Ensure host.docker.internal resolves from containers
docker compose exec lightrag ping host.docker.internal

# If ping fails, verify docker-compose.yml includes:
# extra_hosts:
#   - "host.docker.internal:host-gateway"
```

**Expected Behavior**:
- **First request**: 30-60 seconds (model loading into memory)
- **Subsequent requests**: <1 second
- If every request is slow, the model is not staying loaded (check Ollama memory settings)

### PostgreSQL Extension Errors
Extensions are installed during first initialization. To reset:
```bash
docker compose down -v
docker compose up -d postgres
```

## License

TBD

## Support

For issues and questions, see [docs/](docs/) or contact the development team.
