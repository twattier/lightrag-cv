#!/bin/bash
# Health check script for LightRAG-CV infrastructure
# Verifies all services are running and operational

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
fi

# Default ports (matching docker-compose.yml defaults)
# NOTE: If .env is loaded above, these will be overridden by .env values
POSTGRES_PORT=${POSTGRES_PORT:-5432}
LIGHTRAG_PORT=${LIGHTRAG_PORT:-9621}
DOCLING_PORT=${DOCLING_PORT:-8000}
MCP_PORT=${MCP_PORT:-3000}
OLLAMA_HOST_PORT=${OLLAMA_HOST_PORT:-11434}
OLLAMA_LLM_MODEL=${OLLAMA_LLM_MODEL:-qwen3:8b}
OLLAMA_EMBEDDING_MODEL=${OLLAMA_EMBEDDING_MODEL:-bge-m3:latest}
OLLAMA_RERANKER_MODEL=${OLLAMA_RERANKER_MODEL:-xitao/bge-reranker-v2-m3}

# Status tracking
ALL_HEALTHY=true

echo "========================================"
echo "LightRAG-CV Infrastructure Health Check"
echo "========================================"
echo ""

# Function to check HTTP endpoint
check_http() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}

    echo -n "Checking $name... "

    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✓ OK${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $response)"
        ALL_HEALTHY=false
        return 1
    fi
}

# Function to check PostgreSQL
check_postgres() {
    echo -n "Checking PostgreSQL... "

    # Try to connect using psql
    if command -v psql &> /dev/null; then
        result=$(PGPASSWORD=${POSTGRES_PASSWORD} psql -h localhost -p ${POSTGRES_PORT} -U ${POSTGRES_USER:-lightrag} -d ${POSTGRES_DB:-lightrag_cv} -t -c "SELECT 1" 2>/dev/null || echo "")

        if [ -n "$result" ]; then
            echo -e "${GREEN}✓ OK${NC} (connected)"

            # Check extensions
            echo -n "  Checking pgvector extension... "
            ext_vector=$(PGPASSWORD=${POSTGRES_PASSWORD} psql -h localhost -p ${POSTGRES_PORT} -U ${POSTGRES_USER:-lightrag} -d ${POSTGRES_DB:-lightrag_cv} -t -c "SELECT 1 FROM pg_extension WHERE extname='vector'" 2>/dev/null | tr -d ' ')
            if [ "$ext_vector" = "1" ]; then
                echo -e "${GREEN}✓ OK${NC}"
            else
                echo -e "${RED}✗ NOT INSTALLED${NC}"
                ALL_HEALTHY=false
            fi

            echo -n "  Checking Apache AGE extension... "
            ext_age=$(PGPASSWORD=${POSTGRES_PASSWORD} psql -h localhost -p ${POSTGRES_PORT} -U ${POSTGRES_USER:-lightrag} -d ${POSTGRES_DB:-lightrag_cv} -t -c "SELECT 1 FROM pg_extension WHERE extname='age'" 2>/dev/null | tr -d ' ')
            if [ "$ext_age" = "1" ]; then
                echo -e "${GREEN}✓ OK${NC}"
            else
                echo -e "${RED}✗ NOT INSTALLED${NC}"
                ALL_HEALTHY=false
            fi

            return 0
        fi
    fi

    # Fallback: check if port is listening
    if nc -z localhost ${POSTGRES_PORT} 2>/dev/null; then
        echo -e "${YELLOW}⚠ LISTENING${NC} (psql not available to verify)"
        return 0
    else
        echo -e "${RED}✗ NOT REACHABLE${NC}"
        ALL_HEALTHY=false
        return 1
    fi
}

# Check PostgreSQL
check_postgres

# Check LightRAG API
check_http "LightRAG API" "http://localhost:${LIGHTRAG_PORT}/health"

# Check Docling API
check_http "Docling API" "http://localhost:${DOCLING_PORT}/health"

# Check Ollama
echo -n "Checking Ollama... "
if curl -s --max-time 3 "http://localhost:${OLLAMA_HOST_PORT}/api/tags" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"

    # Quick model check
    models=$(curl -s "http://localhost:${OLLAMA_HOST_PORT}/api/tags" 2>/dev/null)

    for model in "$OLLAMA_LLM_MODEL" "$OLLAMA_EMBEDDING_MODEL" "$OLLAMA_RERANKER_MODEL"; do
        model_base="${model%%:*}"
        echo -n "  Checking ${model}... "
        if echo "$models" | grep -q "\"name\":\"$model_base"; then
            echo -e "${GREEN}✓ AVAILABLE${NC}"
        else
            echo -e "${YELLOW}⚠ NOT FOUND${NC}"
        fi
    done
else
    echo -e "${RED}✗ NOT REACHABLE${NC}"
    ALL_HEALTHY=false
fi

# Check MCP Server (optional - may not be implemented yet)
echo -n "Checking MCP Server... "
mcp_response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${MCP_PORT}/health" 2>/dev/null || echo "000")
if [ "$mcp_response" = "200" ]; then
    echo -e "${GREEN}✓ OK${NC} (HTTP $mcp_response)"
elif [ "$mcp_response" = "000" ]; then
    echo -e "${YELLOW}⚠ NOT RUNNING${NC} (optional for Epic 1)"
else
    echo -e "${YELLOW}⚠ UNEXPECTED${NC} (HTTP $mcp_response)"
fi

echo ""
echo "========================================"

if [ "$ALL_HEALTHY" = true ]; then
    echo -e "${GREEN}✓ ALL CRITICAL SERVICES HEALTHY${NC}"
    echo "========================================"
    exit 0
else
    echo -e "${RED}✗ SOME SERVICES UNHEALTHY${NC}"
    echo "========================================"
    echo ""
    echo "Troubleshooting:"
    echo "  - Check service logs: docker compose logs -f"
    echo "  - Restart services: docker compose restart"
    echo "  - Check .env configuration"
    echo "  - Ensure Ollama is running: ollama serve"
    exit 1
fi
