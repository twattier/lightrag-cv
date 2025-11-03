# Infrastructure and Deployment

**Deployment Platform:** Windows WSL2 + Docker Desktop
**Orchestration:** Docker Compose v2.23+
**Target Environment:** Local development and POC demonstration

## Docker Compose Configuration

**Main file:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    build:
      context: ./services/postgres
      dockerfile: Dockerfile
    container_name: lightrag-cv-postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-lightrag_cv}
      POSTGRES_USER: ${POSTGRES_USER:-lightrag}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?error}
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./services/postgres/init:/docker-entrypoint-initdb.d:ro
    networks:
      - lightrag-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-lightrag}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  docling:
    build:
      context: ./services/docling
      dockerfile: Dockerfile
    container_name: lightrag-cv-docling
    environment:
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
    ports:
      - "${DOCLING_PORT:-8000}:8000"
    networks:
      - lightrag-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  lightrag:
    build:
      context: ./services/lightrag
      dockerfile: Dockerfile
    container_name: lightrag-cv-lightrag
    environment:
      POSTGRES_HOST: postgres
      POSTGRES_PORT: 5432
      POSTGRES_DB: ${POSTGRES_DB:-lightrag_cv}
      POSTGRES_USER: ${POSTGRES_USER:-lightrag}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?error}
      OLLAMA_BASE_URL: ${OLLAMA_BASE_URL:-http://host.docker.internal:11434}
      OLLAMA_LLM_MODEL: ${OLLAMA_LLM_MODEL:-qwen3:8b}
      OLLAMA_EMBEDDING_MODEL: ${OLLAMA_EMBEDDING_MODEL:-bge-m3:latest}
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
    ports:
      - "${LIGHTRAG_PORT:-9621}:9621"
    volumes:
      - ./data/lightrag:/app/data/lightrag
    networks:
      - lightrag-network
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9621/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  mcp-server:
    build:
      context: ./services/mcp-server
      dockerfile: Dockerfile
    container_name: lightrag-cv-mcp
    environment:
      LIGHTRAG_API_URL: http://lightrag:9621
      POSTGRES_HOST: postgres
      POSTGRES_PORT: 5432
      POSTGRES_DB: ${POSTGRES_DB:-lightrag_cv}
      POSTGRES_USER: ${POSTGRES_USER:-lightrag}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?error}
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
    ports:
      - "${MCP_PORT:-3000}:3000"
    networks:
      - lightrag-network
    depends_on:
      lightrag:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

networks:
  lightrag-network:
    driver: bridge
    name: lightrag-cv-network

volumes:
  postgres_data:
    name: lightrag-cv-postgres-data
```

## Development Workflow

**Initial Setup:**

```bash
# 1. Clone repository
cd /home/wsluser/dev
git clone <repository-url> lightrag-cv
cd lightrag-cv

# 2. Configure environment
cp .env.example .env
nano .env  # Edit with your settings

# 3. Pull Ollama models
ollama pull qwen3:8b
ollama pull bge-m3:latest
ollama pull xitao/bge-reranker-v2-m3

# 4. Build Docker images
docker-compose build

# 5. Start services
docker-compose up -d

# 6. Verify health
./scripts/health-check.sh
```

**Common Operations:**

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f lightrag

# Rebuild after code changes
docker-compose up -d --build lightrag

# Reset database
docker-compose down -v
docker-compose up -d
```

---
