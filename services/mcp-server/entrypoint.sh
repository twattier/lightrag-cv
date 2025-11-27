#!/bin/bash
# Entrypoint script for MCP server container
# Substitutes environment variables in config template and starts MCPO

set -e

# Substitute environment variables in config template
envsubst < /app/mcpo-config.template.json > /app/mcpo-config.json

# Start MCPO with the generated config
exec mcpo --host 0.0.0.0 --port 3000 --config /app/mcpo-config.json
