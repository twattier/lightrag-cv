FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create data directories
RUN mkdir -p /app/data/lightrag /app/data/inputs

# Expose LightRAG API port
EXPOSE 9621

# Run official LightRAG server with WebUI and 600s timeout
CMD ["lightrag-server", "--host", "0.0.0.0", "--port", "9621"]
