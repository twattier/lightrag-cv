FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Node.js for npx-based MCP servers
RUN apt-get update -qq && \
    apt-get install -y -qq curl gnupg gettext-base && \
    # Install Node.js 20.x LTS for npx support
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y -qq nodejs && \
    # Install uv package manager for uvx-based MCP servers
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Add uv to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy application requirements and install
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install mcpo (MCP-to-OpenAPI proxy)
RUN pip install --no-cache-dir mcpo

# Copy application code
COPY app/ ./app/

# Copy MCPO configuration template and entrypoint
COPY services/mcp-server/mcpo-config.template.json ./mcpo-config.template.json
COPY services/mcp-server/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Set Python path
ENV PYTHONPATH=/app

# Expose port for mcpo HTTP/OpenAPI endpoint
EXPOSE 3000

# Run entrypoint which substitutes env vars and starts MCPO
ENTRYPOINT ["./entrypoint.sh"]
