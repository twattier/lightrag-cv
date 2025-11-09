FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update -qq && \
    apt-get install -y -qq curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy application requirements and install
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install mcpo (MCP-to-OpenAPI proxy)
RUN pip install --no-cache-dir mcpo

# Copy application code
COPY app/ ./app/

# Set Python path
ENV PYTHONPATH=/app

# Expose port for mcpo HTTP/OpenAPI endpoint
EXPOSE 3000

# Run MCP server via mcpo proxy
# mcpo wraps the stdio MCP server and exposes it as HTTP/OpenAPI
CMD ["mcpo", "--host", "0.0.0.0", "--port", "3000", "--", "python3", "-m", "app.mcp_server.server"]
