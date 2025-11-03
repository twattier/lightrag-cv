# Data Models

**Critical Context:** This POC leverages **existing frameworks** that handle the heavy lifting:

- **LightRAG** automatically handles: entity extraction, relationship graph construction, vector embeddings, and hybrid retrieval
- **Docling** automatically handles: PDF/DOCX parsing, structure extraction, intelligent chunking

**Our architecture focuses on:**
1. Understanding LightRAG's internal data model (what it creates via PostgreSQL adapters)
2. Feeding properly formatted data TO these frameworks
3. Minimal metadata layer for POC-specific needs (CIGREF vs CV distinction, document tracking)

## LightRAG's Automatic Data Model

LightRAG uses its PostgreSQL storage adapters to create and manage these structures **automatically**:

### PGKVStorage (Key-Value Store)

**Purpose:** LightRAG's internal configuration and state management

**Schema (LightRAG-managed):**
```sql
CREATE TABLE lightrag_kv (
    key TEXT PRIMARY KEY,
    value JSONB,
    namespace TEXT DEFAULT 'default',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**What LightRAG stores here:**
- Configuration settings
- Internal state tracking
- Cached computation results
- System metadata

**Our responsibility:** None - LightRAG manages this entirely

### PGVectorStorage (Vector Embeddings)

**Purpose:** Stores document chunk embeddings for semantic similarity search

**Schema (LightRAG-managed):**
```sql
CREATE TABLE lightrag_vectors (
    id TEXT PRIMARY KEY,
    vector VECTOR(1024),  -- pgvector type, 1024-dim for bge-m3
    content TEXT,         -- Original chunk text
    metadata JSONB,       -- Document ID, chunk index, etc.
    created_at TIMESTAMP DEFAULT NOW()
);

-- HNSW index for fast approximate nearest neighbor search
CREATE INDEX idx_vector_hnsw ON lightrag_vectors
USING hnsw (vector vector_cosine_ops);
```

**What LightRAG stores here:**
- Embeddings of document chunks (created during ingestion)
- Generated via Ollama bge-m3 model automatically
- Metadata links vectors back to source documents

**Our responsibility:**
- Provide document content to LightRAG's ingestion API
- Configure embedding model endpoint (Ollama)
- LightRAG handles chunking, embedding generation, and storage

### PGGraphStorage (Knowledge Graph via Apache AGE)

**Purpose:** Stores automatically extracted entities and relationships for graph-based reasoning

LightRAG uses Apache AGE's graph database within PostgreSQL. AGE creates nodes and edges representing:

- **Entities (graph nodes):** Skills (e.g., "Kubernetes", "Python", "AWS"), Competencies, Concepts, Named entities from documents
- **Relationships (graph edges):** "requires", "relates_to", "part_of", "mentions"

**Cypher query example (how we'll query the graph):**
```cypher
-- Find skills related to "Cloud Architect" within 2 hops
MATCH (profile {name: 'Cloud Architect'})-[r*1..2]-(skill)
WHERE skill.type = 'skill'
RETURN skill.name, type(r), profile.name
```

**What LightRAG does automatically:**
- Extracts entities from ingested documents via LLM (qwen3:8b)
- Identifies relationships between entities
- Builds knowledge graph incrementally as documents are added
- Optimizes graph structure for hybrid retrieval

**Our responsibility:**
- Provide well-structured documents (via Docling parsing)
- Configure LLM endpoint for entity extraction (Ollama qwen3:8b)
- Query the graph via LightRAG's API (we don't write Cypher directly in POC)

### PGDocStatusStorage (Document Tracking)

**Purpose:** Tracks document processing status through LightRAG pipeline

**Schema (LightRAG-managed):**
```sql
CREATE TABLE lightrag_doc_status (
    document_id TEXT PRIMARY KEY,
    status TEXT,  -- 'pending', 'processing', 'completed', 'failed'
    error_message TEXT,
    chunks_created INTEGER,
    entities_extracted INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**What LightRAG tracks:**
- Document processing progress
- Error states if ingestion fails
- Statistics (chunk count, entity count)

**Our responsibility:**
- Provide unique document IDs when calling LightRAG ingestion API
- Monitor status for debugging
- Handle failed ingestions (retry or flag for manual review)

## Our Minimal Metadata Layer

We add **one small custom table** to distinguish CIGREF profiles from CVs:

### document_metadata

**Purpose:** POC-specific metadata not managed by LightRAG

**Schema (our custom table):**
```sql
CREATE TABLE document_metadata (
    document_id TEXT PRIMARY KEY,  -- Matches lightrag_doc_status.document_id
    document_type TEXT NOT NULL,   -- 'CIGREF_PROFILE' | 'CV'
    source_filename TEXT NOT NULL,
    file_format TEXT,              -- 'PDF' | 'DOCX'
    upload_timestamp TIMESTAMP DEFAULT NOW(),
    cigref_profile_name TEXT,      -- Only for CIGREF docs (e.g., "Cloud Architect")
    candidate_label TEXT,          -- Only for CVs (e.g., "candidate_001")
    metadata JSONB                 -- Flexible storage for POC needs
);
```

**Why we need this:**
- Distinguish CIGREF reference documents from candidate CVs
- Track original filenames for debugging
- Enable filtering queries (e.g., "search only CVs", "show CIGREF profiles")
- Store POC-specific metadata that LightRAG doesn't need

**This is the ONLY custom table we create.** Everything else is LightRAG/Docling-managed.

## CV-CIGREF Linking Through Shared Entities

**The link happens automatically through:**

1. ✅ **Shared entity extraction** - LightRAG identifies "AWS" in both CIGREF and CV documents
2. ✅ **Knowledge graph unification** - Same entities across documents create natural connections
3. ✅ **Hybrid retrieval** - Combines semantic search + graph traversal to find matches
4. ✅ **No manual mapping needed** - LightRAG's entity extraction and graph construction handle this

**Example Connection Flow:**

```
CIGREF Document:
  "Cloud Architect profile requires AWS, Kubernetes, Terraform..."
  → LightRAG extracts: Entity(name="AWS", type="SKILL")
  → Graph edge: (Cloud Architect) --[REQUIRES]--> (AWS)

CV Document:
  "Built AWS infrastructure using Terraform..."
  → LightRAG extracts: Entity(name="AWS", type="SKILL") [SAME entity!]
  → Graph edge: (candidate_001) --[HAS_SKILL]--> (AWS)

Query Time:
  User asks: "Find Cloud Architect candidates"
  → Hybrid retrieval finds: Cloud Architect --[REQUIRES]--> AWS <--[HAS_SKILL]-- candidate_001
  → Match detected via shared graph entity!
```

---
