# LightRAG-CV Development Setup Guide

Complete guide to setting up the LightRAG-CV development environment on Windows WSL2.

## Prerequisites

### Required

- **Docker Desktop**: 4.25+ with WSL2 integration enabled
  - Download: https://www.docker.com/products/docker-desktop
  - Enable WSL2 backend in Docker Desktop settings

- **WSL2**: Ubuntu 22.04 LTS recommended
  - Installation: `wsl --install -d Ubuntu-22.04`

- **Ollama**: 0.3.12+ for local LLM inference
  - Download: https://ollama.com
  - Must be running on host machine

### System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 16GB | 32GB |
| Disk Space | 20GB free | 40GB free |
| CPU | 4 cores | 8+ cores |
| GPU | None (CPU works) | NVIDIA GPU for Docling acceleration |

### Optional

- **NVIDIA GPU + Drivers**: For GPU-accelerated document parsing
  - NVIDIA drivers 515.x or newer
  - CUDA 12.x support
  - nvidia-docker runtime configured

## Quick Start (15 Minutes)

### Automated Setup

```bash
# 1. Clone repository
git clone <repository-url> lightrag-cv
cd lightrag-cv

# 2. Run automated setup
./scripts/setup.sh

# Follow prompts to:
# - Configure PostgreSQL password
# - Pull Ollama models (11GB download)
# - Build Docker images
# - Start services
```

### Manual Setup

```bash
# 1. Clone repository
git clone <repository-url> lightrag-cv
cd lightrag-cv

# 2. Configure environment
cp .env.example .env
nano .env  # Set POSTGRES_PASSWORD and other settings

# 3. Install and configure Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve

# 4. Pull required models (in separate terminal)
ollama pull qwen3:8b          # ~5GB
ollama pull bge-m3:latest     # ~3GB
ollama pull xitao/bge-reranker-v2-m3  # ~3GB

# 5. Validate Ollama setup
python3 scripts/validate-ollama.py

# 6. Build and start services
docker compose build
docker compose up -d

# 7. Verify all services healthy
./scripts/health-check.sh
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Host Machine (WSL2)                    │
│                                                             │
│  ┌──────────────┐                                          │
│  │   Ollama     │ :11434                                   │
│  │  (qwen3:8b,  │                                          │
│  │   bge-m3)    │                                          │
│  └──────┬───────┘                                          │
│         │ host.docker.internal                             │
│         │                                                   │
│  ┌──────▼──────────────────────────────────────────────┐   │
│  │          Docker Compose Network                     │   │
│  │                                                      │   │
│  │  ┌──────────────┐      ┌──────────────┐            │   │
│  │  │  Docling     │      │  LightRAG    │            │   │
│  │  │  :8000       │      │  :9621       │            │   │
│  │  │              │      │              │            │   │
│  │  │  PDF/DOCX    │─────▶│  Hybrid RAG  │            │   │
│  │  │  Parsing     │ chunks│              │            │   │
│  │  └──────────────┘      └──────┬───────┘            │   │
│  │                               │                     │   │
│  │                               │                     │   │
│  │  ┌──────────────┐      ┌──────▼───────┐            │   │
│  │  │  MCP Server  │      │  PostgreSQL  │            │   │
│  │  │  :3000       │◀─────│  :5432       │            │   │
│  │  │              │ query│              │            │   │
│  │  │  OpenWebUI   │      │  pgvector    │            │   │
│  │  │  Integration │      │  Apache AGE  │            │   │
│  │  └──────────────┘      └──────────────┘            │   │
│  │                                                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables

Edit `.env` to configure the system:

```bash
# PostgreSQL (REQUIRED)
POSTGRES_PASSWORD=your_secure_password_here

# Service Ports (optional, defaults shown)
POSTGRES_PORT=5432
LIGHTRAG_PORT=9621
DOCLING_PORT=8000
MCP_PORT=3000

# Ollama Models (optional, defaults shown)
OLLAMA_LLM_MODEL=qwen3:8b
OLLAMA_EMBEDDING_MODEL=bge-m3:latest
OLLAMA_RERANKER_MODEL=xitao/bge-reranker-v2-m3

# Logging
LOG_LEVEL=INFO
```

## Docker Compose Commands

### Starting Services

```bash
# Start all services in background
docker compose up -d

# Start with GPU support for Docling
docker compose --profile gpu up -d

# Start specific service
docker compose up -d lightrag

# Start with logs visible
docker compose up
```

### Monitoring

```bash
# View logs for all services
docker compose logs -f

# View logs for specific service
docker compose logs -f lightrag

# Check service status
docker compose ps

# Check resource usage
docker stats
```

### Stopping and Resetting

```bash
# Stop all services (preserves data)
docker compose down

# Stop and remove volumes (DELETES DATABASE)
docker compose down -v

# Restart specific service
docker compose restart lightrag

# Rebuild and restart after code changes
docker compose up -d --build lightrag
```

## Validation and Health Checks

### Comprehensive Health Check

```bash
# Run health check script
./scripts/health-check.sh

# Or Python version for JSON output
python3 scripts/health-check.py
```

### Manual Service Checks

```bash
# Check PostgreSQL
PGPASSWORD=your_password psql -h localhost -p 5432 -U lightrag -d lightrag_cv -c "\dx"

# Check LightRAG API
curl http://localhost:9621/health

# Check Docling API
curl http://localhost:8000/health

# Check Ollama
curl http://localhost:11434/api/tags
```

## Troubleshooting

### Port Conflicts

**Symptom**: Service fails to start with "address already in use"

**Solution**: Change ports in `.env`

```bash
# Edit .env
POSTGRES_PORT=5433
DOCLING_PORT=8001
LIGHTRAG_PORT=9622
MCP_PORT=3001

# Restart services
docker compose down
docker compose up -d
```

### PostgreSQL Extension Errors

**Symptom**: Extensions not loading, "could not load library" errors

**Solution 1** - Reset database (deletes data):
```bash
docker compose down -v
docker compose up -d postgres
```

**Solution 2** - Rebuild PostgreSQL image:
```bash
docker compose build postgres
docker compose up -d postgres
```

**Verification**:
```bash
PGPASSWORD=your_password psql -h localhost -p 5432 -U lightrag -d lightrag_cv -c "SELECT extname, extversion FROM pg_extension;"
```

### Ollama Connection Issues

**Symptom**: LightRAG cannot reach Ollama, "connection refused"

**Solution 1** - Verify Ollama running:
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# If not running
ollama serve
```

**Solution 2** - Check Docker network:
```bash
# Test from container
docker compose exec lightrag ping host.docker.internal

# Should resolve and respond
# If not, check docker-compose.yml has:
#   extra_hosts:
#     - "host.docker.internal:host-gateway"
```

**Solution 3** - Verify models loaded:
```bash
# List models
ollama list

# Pull missing models
ollama pull qwen3:8b
```

### Slow First Requests

**Symptom**: First API call takes 30-60 seconds

**Expected Behavior**: This is normal! Ollama loads models into memory on first use.

- First request: 30-60 seconds (one-time model loading)
- Subsequent requests: <1 second

**If all requests are slow**:
- Check system memory (need 16GB+)
- Verify Ollama settings: `ollama show qwen3:8b`
- Models should stay loaded between requests

### Docker Build Failures

**Symptom**: `docker compose build` fails

**Solution 1** - Clear Docker cache:
```bash
docker builder prune -a
docker compose build --no-cache
```

**Solution 2** - Check disk space:
```bash
df -h
# Need at least 20GB free
```

**Solution 3** - Check network:
```bash
# Test connectivity to package repos
curl -I https://pypi.org
curl -I https://github.com
```

### GPU Not Detected

**Symptom**: Docling reports `gpu_available: false`

**Solution**:

1. Check NVIDIA drivers on host:
```bash
nvidia-smi
# Should show GPU info
```

2. Check nvidia-docker runtime:
```bash
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
# Should show GPU from container
```

3. Use GPU profile:
```bash
docker compose --profile gpu up -d docling
```

4. Check Docling logs:
```bash
docker compose logs docling | grep -i gpu
```

## First-Run Behavior

### Expected Timeline

| Step | Duration | Notes |
|------|----------|-------|
| Clone repository | 1-2 min | Depends on network |
| Copy .env | <1 min | |
| Pull Ollama models | 5-10 min | 11GB download |
| Build Docker images | 3-5 min | First time only |
| Start services | 1-2 min | |
| PostgreSQL init | 30-60 sec | Extensions install |
| First Ollama request | 30-60 sec | Model loading |
| **Total** | **10-15 min** | With fast network |

### What Happens on First Start

1. **PostgreSQL** (30-60 seconds):
   - Creates `lightrag_cv` database
   - Installs pgvector 0.5.1 extension
   - Installs Apache AGE 1.5.0 extension
   - Creates `document_metadata` table
   - Creates `lightrag_graph` graph

2. **LightRAG** (startup: 5-10 seconds):
   - Connects to PostgreSQL
   - Initializes storage adapters
   - Waits for first Ollama call to load models

3. **Docling** (startup: 5-10 seconds):
   - Loads Docling library
   - Checks for GPU availability
   - Ready to parse documents

4. **Ollama** (first request only: 30-60 seconds):
   - Loads model into memory
   - Subsequent requests are fast

## Development Workflow

### Typical Development Session

```bash
# 1. Start services
docker compose up -d

# 2. Check health
./scripts/health-check.sh

# 3. Make configuration changes (e.g., update environment variables in .env)

# 4. Rebuild and restart changed service
docker compose up -d --build lightrag

# 5. Test changes
curl http://localhost:9621/health

# 6. View logs
docker compose logs -f lightrag

# 7. Stop when done
docker compose down
```

### Testing Individual Services

```bash
# Test only PostgreSQL
docker compose up -d postgres
PGPASSWORD=your_password psql -h localhost -p 5432 -U lightrag -d lightrag_cv

# Test only LightRAG
docker compose up -d postgres lightrag
curl http://localhost:9621/health

# Test only Docling
docker compose up -d docling
curl http://localhost:8000/health
```

## Performance Tuning

### Resource Allocation

Edit Docker Desktop settings:

- **RAM**: 8GB minimum, 16GB recommended
- **CPUs**: 4 minimum, 8 recommended
- **Disk**: 20GB minimum

### PostgreSQL Tuning

For better performance, create `services/postgres/conf/postgresql.conf`:

```
# Memory
shared_buffers = 2GB
effective_cache_size = 6GB

# Performance
max_connections = 100
work_mem = 16MB
maintenance_work_mem = 512MB

# Logging
log_statement = 'none'
```

Then mount in `docker-compose.yml`:
```yaml
volumes:
  - ./services/postgres/conf/postgresql.conf:/etc/postgresql/postgresql.conf:ro
```

## Next Steps

After successful setup:

1. **Verify Health**: Run `./scripts/health-check.sh` - all checks should pass
2. **Explore APIs**: Check service endpoints at http://localhost:9621, http://localhost:8000
3. **Review Documentation**: See `docs/architecture/` for technical details
4. **Start Development**: Begin with Epic 2 (Document Processing Pipeline)

## Support

For issues:
- Check `docker compose logs -f`
- Review this troubleshooting guide
- See [README.md](../README.md) for additional info
- Check [Architecture documentation](architecture/)

## Appendix: Manual PostgreSQL Extension Installation

If automated extension installation fails:

```sql
-- Connect to PostgreSQL
psql -h localhost -p 5432 -U lightrag -d lightrag_cv

-- Install pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Install Apache AGE
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';
SET search_path = ag_catalog, "$user", public;

-- Create graph
SELECT create_graph('lightrag_graph');

-- Verify
\dx
```
