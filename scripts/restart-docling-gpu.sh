#!/bin/bash
# Quick restart script for Docling GPU service (without rebuild)

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the script's directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo -e "${YELLOW}Restarting Docling GPU service...${NC}"
docker compose -f docker-compose.yml -f docker-compose.gpu.yml --profile gpu restart docling

echo -e "${GREEN}✓ Service restarted${NC}"
echo ""
echo "View logs with: docker compose logs -f docling"
