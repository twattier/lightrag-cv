#!/bin/bash
# Script to rebuild and start Docling service with GPU support
# This script stops the existing Docling container, rebuilds it with GPU support,
# and starts it with NVIDIA GPU access.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the script's directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${GREEN}=== Docling GPU Server Setup ===${NC}"
echo ""

# Check if NVIDIA Docker runtime is available
echo -e "${YELLOW}Checking NVIDIA Docker runtime...${NC}"
if ! docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi &>/dev/null; then
    echo -e "${RED}Error: NVIDIA Docker runtime not available or no GPU detected${NC}"
    echo "Please ensure:"
    echo "  1. NVIDIA drivers are installed"
    echo "  2. NVIDIA Container Toolkit is installed"
    echo "  3. Docker is configured to use NVIDIA runtime"
    echo ""
    echo "Installation guide: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    exit 1
fi
echo -e "${GREEN}✓ NVIDIA runtime available${NC}"
echo ""

# Navigate to project root
cd "$PROJECT_ROOT"

# Stop existing Docling container (both regular and GPU)
echo -e "${YELLOW}Stopping existing Docling containers...${NC}"
docker compose -f docker-compose.yml stop docling 2>/dev/null || true
docker compose -f docker-compose.yml -f docker-compose.gpu.yml --profile gpu stop docling 2>/dev/null || true
docker compose -f docker-compose.yml rm -f docling 2>/dev/null || true
echo -e "${GREEN}✓ Existing containers stopped${NC}"
echo ""

# Rebuild Docling with GPU support
echo -e "${YELLOW}Building Docling Docker image with GPU support...${NC}"
docker compose -f docker-compose.yml -f docker-compose.gpu.yml --profile gpu build docling
echo -e "${GREEN}✓ GPU image built successfully${NC}"
echo ""

# Start Docling with GPU support
echo -e "${YELLOW}Starting Docling service with GPU support...${NC}"
docker compose -f docker-compose.yml -f docker-compose.gpu.yml --profile gpu up -d docling
echo -e "${GREEN}✓ Docling GPU service started${NC}"
echo ""

# Wait for service to be ready
echo -e "${YELLOW}Waiting for Docling service to be healthy...${NC}"
RETRIES=30
COUNT=0
while [ $COUNT -lt $RETRIES ]; do
    if docker compose -f docker-compose.yml ps docling | grep -q "healthy"; then
        echo -e "${GREEN}✓ Docling service is healthy and ready!${NC}"
        break
    fi
    COUNT=$((COUNT + 1))
    if [ $COUNT -eq $RETRIES ]; then
        echo -e "${RED}Warning: Service did not become healthy within expected time${NC}"
        echo "Check logs with: docker compose logs docling"
        break
    fi
    echo -n "."
    sleep 2
done
echo ""

# Show GPU info
echo -e "${YELLOW}GPU Information:${NC}"
docker exec lightrag-cv-docling nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || echo "Could not retrieve GPU info"
echo ""

# Show container info
echo -e "${GREEN}=== Docling GPU Service Info ===${NC}"
docker compose -f docker-compose.yml ps docling
echo ""

echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo "Service endpoint: http://localhost:\${DOCLING_PORT:-8000}"
echo ""
echo "Useful commands:"
echo "  View logs:        docker compose logs -f docling"
echo "  Stop service:     docker compose stop docling"
echo "  Restart service:  docker compose restart docling"
echo "  Check health:     curl http://localhost:\${DOCLING_PORT:-8000}/health"
