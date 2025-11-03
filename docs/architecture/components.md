# Components

This section details the **services we build** to orchestrate LightRAG and Docling frameworks. Each component focuses on integration, configuration, and API exposure rather than reimplementing framework functionality.

## Component 1: Docling Service

**Responsibility:** Expose Docling's document parsing and chunking capabilities via REST API, wrapping the Docling library with optional GPU acceleration for PDF/DOCX processing.

**Key Interfaces:**

**REST API (FastAPI, Port 8000):**
```python
POST /parse
  Request: multipart/form-data
    - file: PDF or DOCX binary
    - options: JSON (optional GPU mode, chunk size hints)
  Response: 200 OK
    {
      "document_id": "uuid",
      "chunks": [
        {
          "chunk_id": "chunk_0",
          "content": "...",
          "chunk_type": "paragraph",
          "metadata": {"section": "...", "page": 1}
        }
      ],
      "metadata": {
        "page_count": 10,
        "format": "PDF",
        "tables_extracted": 3,
        "processing_time_ms": 1500
      }
    }

GET /health
  Response: 200 OK {"status": "healthy", "gpu_available": true/false}
```

**Dependencies:**
- **Docling library** (v1.16.2) - Core parsing engine with HybridChunker
- **Python 3.11** runtime environment
- **Optional: NVIDIA GPU** via Docker nvidia runtime (--profile gpu)

**Technology Stack:**
- **Language:** Python 3.11
- **Framework:** FastAPI 0.109.0
- **Parsing Engine:** Docling 1.16.2 with HybridChunker
- **Containerization:** Dockerfile with CPU/GPU variants

**What We Build:**
- ✅ FastAPI REST wrapper
- ✅ Request/response serialization
- ✅ Error handling and validation
- ✅ Dockerfile with GPU profile support
- ❌ NOT building custom parsing logic (Docling handles this)

## Component 2: LightRAG Service

**Responsibility:** Configure and expose LightRAG hybrid RAG engine with PostgreSQL storage adapters, providing document ingestion and retrieval APIs.

**Key Interfaces:**

**REST API (FastAPI, Port 9621):**
```python
POST /documents
  Request:
    {
      "document_id": "uuid",
      "chunks": [...],  # From Docling
      "metadata": {"type": "CIGREF_PROFILE" | "CV", "filename": "..."}
    }
  Response: 202 Accepted
    {
      "document_id": "uuid",
      "status": "processing",
      "message": "Document ingestion started"
    }

GET /documents/{document_id}/status
  Response: 200 OK
    {
      "document_id": "uuid",
      "status": "completed" | "processing" | "failed",
      "chunks_created": 45,
      "entities_extracted": 23,
      "error": null
    }

POST /query
  Request:
    {
      "query": "Find candidates with Kubernetes experience",
      "mode": "hybrid" | "local" | "global" | "naive",
      "top_k": 5,
      "filters": {"document_type": "CV"}
    }
  Response: 200 OK
    {
      "results": [
        {
          "document_id": "uuid",
          "content": "...",
          "score": 0.85,
          "metadata": {...},
          "entities": ["Kubernetes", "Docker", "AWS"],
          "graph_paths": [...]
        }
      ],
      "retrieval_mode_used": "hybrid",
      "query_time_ms": 450
    }

GET /health
  Response: 200 OK
    {
      "status": "healthy",
      "postgres_connected": true,
      "ollama_connected": true,
      "documents_indexed": 150
    }
```

**Dependencies:**
- **LightRAG library** (v0.0.0.post8) - Core RAG engine
- **PostgreSQL** with pgvector + Apache AGE - Storage layer
- **Ollama** - LLM inference (qwen3:8b, bge-m3, bge-reranker-v2-m3)

**Technology Stack:**
- **Language:** Python 3.11
- **Framework:** FastAPI 0.109.0
- **RAG Engine:** LightRAG with PostgreSQL adapters (PGKVStorage, PGVectorStorage, PGGraphStorage, PGDocStatusStorage)
- **Database Client:** psycopg3 3.1.16
- **HTTP Client:** httpx 0.26.0 (for Ollama calls)

**What We Build:**
- ✅ FastAPI REST wrapper around LightRAG
- ✅ PostgreSQL storage adapter configuration
- ✅ Ollama integration configuration
- ✅ API endpoint definitions
- ✅ Document metadata integration (join with custom table)
- ❌ NOT building custom RAG logic (LightRAG handles retrieval, embeddings, graph)

## Component 3: MCP Server

**Responsibility:** Implement Model Context Protocol (MCP) specification to expose LightRAG-CV capabilities as tools consumable by OpenWebUI, providing intelligent retrieval mode selection and response formatting.

**Exposed MCP Tools:**

```typescript
// Tool 1: Profile-based candidate search
{
  name: "search_by_profile",
  description: "Find candidates matching a CIGREF IT profile",
  parameters: {
    profile_name: {type: "string", required: true},
    experience_years: {type: "number", required: false},
    top_k: {type: "number", required: false, default: 5}
  }
}

// Tool 2: Skill-based candidate search
{
  name: "search_by_skills",
  description: "Find candidates with specific technical skills",
  parameters: {
    required_skills: {type: "array", items: "string", required: true},
    preferred_skills: {type: "array", items: "string", required: false},
    experience_level: {type: "string", enum: ["junior", "mid", "senior"]},
    top_k: {type: "number", required: false, default: 5}
  }
}

// Tool 3: Candidate detail retrieval
{
  name: "get_candidate_details",
  description: "Retrieve full details for a specific candidate",
  parameters: {
    candidate_id: {type: "string", required: true}
  }
}
```

**MCP Tool Invocation Flow:**
1. OpenWebUI sends MCP tool invocation request
2. MCP Server receives request, validates parameters
3. Intelligent retrieval mode selection:
   - Single skill, simple query → `naive` mode
   - Profile match → `local` mode
   - Multi-criteria (3+ skills, experience level) → `hybrid` mode
   - Broad domain query → `global` mode
4. MCP Server calls LightRAG API with selected mode
5. LightRAG returns results with scores, entities, graph paths
6. MCP Server formats response with match explanations
7. Returns formatted markdown to OpenWebUI for display

**Dependencies:**
- **LightRAG Service API** - Retrieval operations
- **PostgreSQL** - Direct queries to `document_metadata` for filtering
- **OpenWebUI** - MCP protocol client

**Technology Stack:**
- **Language:** Python 3.11
- **MCP SDK:** mcp (Python) v0.9.0
- **HTTP Client:** httpx 0.26.0 (for LightRAG API calls)
- **Database Client:** psycopg3 3.1.16 (for metadata queries)

**What We Build:**
- ✅ MCP protocol implementation (tool discovery, invocation handling)
- ✅ Tool definitions (3 tools for MVP)
- ✅ Retrieval mode selection logic
- ✅ Response formatting and explanation generation
- ✅ Integration with LightRAG API
- ❌ NOT building custom retrieval (LightRAG handles this)

## Component 4: PostgreSQL Database

**Responsibility:** Unified persistence layer with pgvector and Apache AGE extensions, serving as storage backend for LightRAG's adapters and custom metadata.

**Database Schema:**
```sql
-- Extension enablement (init script)
CREATE EXTENSION IF NOT EXISTS vector;  -- pgvector 0.5.1
CREATE EXTENSION IF NOT EXISTS age;     -- Apache AGE 1.5.0

-- LightRAG-managed tables (auto-created by storage adapters)
-- - lightrag_kv (PGKVStorage)
-- - lightrag_vectors (PGVectorStorage)
-- - lightrag_doc_status (PGDocStatusStorage)
-- - AGE graph: lightrag_graph (PGGraphStorage)

-- Our custom metadata table
CREATE TABLE document_metadata (
    document_id TEXT PRIMARY KEY,
    document_type TEXT NOT NULL CHECK (document_type IN ('CIGREF_PROFILE', 'CV')),
    source_filename TEXT NOT NULL,
    file_format TEXT CHECK (file_format IN ('PDF', 'DOCX')),
    upload_timestamp TIMESTAMP DEFAULT NOW(),
    cigref_profile_name TEXT,
    candidate_label TEXT,
    metadata JSONB
);

-- Index for filtering queries
CREATE INDEX idx_document_type ON document_metadata(document_type);
```

**Dependencies:**
- **pgvector extension** (v0.5.1) - Vector similarity search
- **Apache AGE extension** (v1.5.0) - Graph database via Cypher
- **PostgreSQL 16.1** - Base RDBMS

**What We Build:**
- ✅ Dockerfile with extension installation
- ✅ init.sql for database and extension setup
- ✅ `document_metadata` table schema
- ✅ Docker Compose service definition with volume
- ❌ NOT managing LightRAG's tables (auto-created by adapters)

---
