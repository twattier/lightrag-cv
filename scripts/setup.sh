#!/bin/bash
# Automated setup script for LightRAG-CV development environment
# Run this script after cloning the repository
#
# IMPORTANT: Run with bash, not sh!
#   Correct:   bash ./scripts/setup.sh  OR  ./scripts/setup.sh
#   Wrong:     sh ./scripts/setup.sh

set -e

# Detect if running with sh instead of bash
if [ -z "$BASH_VERSION" ]; then
    echo "ERROR: This script requires bash, but you're running it with sh"
    echo ""
    echo "Please run with one of these commands:"
    echo "  bash ./scripts/setup.sh"
    echo "  ./scripts/setup.sh  (after: chmod +x ./scripts/setup.sh)"
    echo ""
    exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load environment variables from .env if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
fi

# Set defaults for ports (matching docker-compose.yml defaults)
POSTGRES_PORT=${POSTGRES_PORT:-5432}
LIGHTRAG_PORT=${LIGHTRAG_PORT:-9621}
DOCLING_PORT=${DOCLING_PORT:-8000}
MCP_PORT=${MCP_PORT:-3000}
OLLAMA_HOST_PORT=${OLLAMA_HOST_PORT:-11434}

echo -e "${BLUE}"
echo "========================================"
echo "  LightRAG-CV Development Setup"
echo "========================================"
echo -e "${NC}"

# Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found${NC}"
    echo "  Please install Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}✗ Docker daemon is not running${NC}"
    echo "  Please start Docker Desktop"
    exit 1
fi

docker_version=$(docker --version 2>/dev/null | awk '{print $3}' | sed 's/,$//')
if [ -z "$docker_version" ]; then
    docker_version="unknown"
fi
echo -e "${GREEN}✓ Docker found and running${NC} (version $docker_version)"

# Check Docker Compose
if ! docker compose version &> /dev/null; then
    echo -e "${RED}✗ Docker Compose not found${NC}"
    echo "  Please install Docker Compose 2.23+: https://docs.docker.com/compose/install/"
    exit 1
fi

compose_version=$(docker compose version 2>/dev/null | awk '{print $NF}' | sed 's/^v//')
if [ -z "$compose_version" ]; then
    compose_version="unknown"
fi

# Verify Docker Compose can communicate with daemon
if [ -f docker-compose.yml ] && ! docker compose config &> /dev/null; then
    echo -e "${RED}✗ Docker Compose cannot read configuration${NC}"
    echo "  There may be an issue with docker-compose.yml"
    exit 1
fi

echo -e "${GREEN}✓ Docker Compose found${NC} (version $compose_version)"

# Check Ollama
if curl -s --max-time 3 "http://localhost:${OLLAMA_HOST_PORT}/api/tags" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama API accessible${NC} (http://localhost:${OLLAMA_HOST_PORT})"
else
    echo -e "${YELLOW}⚠ Ollama not accessible${NC}"
    echo "  Install: https://ollama.com or docker run -d -p ${OLLAMA_HOST_PORT}:11434 ollama/ollama"
    read -p "Continue without Ollama? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠ Python 3 not found${NC}"
    echo "  Python 3.8+ is recommended for development and validation scripts."
    echo "  Install from: https://www.python.org/downloads/"
else
    python_version=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ Python 3 found${NC} (version $python_version)"
fi

# Check curl (needed for health checks)
if ! command -v curl &> /dev/null; then
    echo -e "${YELLOW}⚠ curl not found${NC}"
    echo "  curl is needed for API health checks."
    echo "  Install: apt-get install curl (Ubuntu/Debian) or brew install curl (macOS)"
else
    echo -e "${GREEN}✓ curl found${NC}"
fi

echo ""

# Validate Ollama models (use comprehensive Python validator)
echo -e "${BLUE}Step 2: Validating Ollama models...${NC}"

if curl -s --max-time 3 "http://localhost:${OLLAMA_HOST_PORT}/api/tags" > /dev/null 2>&1; then
    if command -v python3 &> /dev/null; then
        echo "Running comprehensive Ollama validation..."
        python3 ./scripts/validate-ollama.py || echo -e "${YELLOW}⚠ Validation had issues (continuing anyway)${NC}"
    else
        echo -e "${YELLOW}⚠ Python 3 not found - skipping model validation${NC}"
        echo "  Install Python 3 to run: python3 ./scripts/validate-ollama.py"
    fi
else
    echo -e "${YELLOW}⚠ Ollama not running - skipping model validation${NC}"
fi

echo ""

# Check disk space
echo -e "${BLUE}Step 3: Checking system resources...${NC}"

available_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
if [ -z "$available_space" ]; then
    echo -e "${YELLOW}⚠ Could not determine available disk space${NC}"
else
    if [ "$available_space" -lt 10 ]; then
        echo -e "${RED}✗ Low disk space: ${available_space}GB available${NC}"
        echo "  At least 10GB free space is recommended for Docker images"
        echo "  Consider freeing up space with: docker system prune -a"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo -e "${GREEN}✓ Sufficient disk space${NC} (${available_space}GB available)"
    fi
fi

echo ""

# Build Docker images
echo -e "${BLUE}Step 4: Building Docker images...${NC}"
echo "This may take several minutes on first run..."

if docker compose build; then
    echo -e "${GREEN}✓ Docker images built successfully${NC}"
else
    echo -e "${RED}✗ Docker build failed${NC}"
    echo ""
    echo "  Common solutions:"
    echo "    1. Check Docker daemon is running: docker ps"
    echo "    2. Free up disk space: docker system prune"
    echo "    3. Check network connectivity for base image downloads"
    echo "    4. Review build logs above for specific errors"
    echo ""
    exit 1
fi

echo ""

# Start services
echo -e "${BLUE}Step 5: Starting services...${NC}"
echo "Would you like to start all services now?"
read -p "Start services? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker compose up -d

    echo ""
    echo -e "${BLUE}Waiting for services to start...${NC}"
    sleep 10

    # Run health check
    echo ""
    echo -e "${BLUE}Running health check...${NC}"
    if [ -f ./scripts/health-check.sh ]; then
        ./scripts/health-check.sh || true
    else
        echo -e "${YELLOW}⚠ Health check script not found${NC}"
    fi
else
    echo -e "${BLUE}→ Skipping service startup${NC}"
    echo "  Start services manually with: docker compose up -d"
fi

echo ""
echo -e "${BLUE}"
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo -e "${NC}"
echo ""
echo "Service endpoints:"
echo "  - LightRAG API: http://localhost:${LIGHTRAG_PORT}"
echo "  - Docling API: http://localhost:${DOCLING_PORT}"
echo "  - PostgreSQL: localhost:${POSTGRES_PORT}"
echo "  - MCP Server: http://localhost:${MCP_PORT}"
echo "  - Ollama: http://localhost:${OLLAMA_HOST_PORT}"
echo ""
echo "Documentation: README.md"
echo ""
