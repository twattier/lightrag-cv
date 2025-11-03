# Database Schema

**Database:** PostgreSQL 16.1 with pgvector 0.5.1 and Apache AGE 1.5.0 extensions

## Database Initialization Script

**File:** `services/postgres/init/01-init-db.sql`

```sql
-- ============================================================================
-- LightRAG-CV Database Initialization
-- ============================================================================

CREATE DATABASE lightrag_cv
    ENCODING 'UTF8'
    LC_COLLATE 'en_US.UTF-8'
    LC_CTYPE 'en_US.UTF-8';

\c lightrag_cv

-- ============================================================================
-- Extension Setup
-- ============================================================================

-- Enable pgvector for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable Apache AGE for graph database
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';
SET search_path = ag_catalog, "$user", public;

-- ============================================================================
-- Custom Schema: document_metadata
-- ============================================================================

CREATE TABLE IF NOT EXISTS document_metadata (
    document_id TEXT PRIMARY KEY,
    document_type TEXT NOT NULL
        CHECK (document_type IN ('CIGREF_PROFILE', 'CV')),
    source_filename TEXT NOT NULL,
    file_format TEXT
        CHECK (file_format IN ('PDF', 'DOCX')),
    upload_timestamp TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    cigref_profile_name TEXT,
    candidate_label TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,

    CONSTRAINT chk_cigref_has_profile_name
        CHECK (
            (document_type = 'CIGREF_PROFILE' AND cigref_profile_name IS NOT NULL)
            OR document_type != 'CIGREF_PROFILE'
        ),
    CONSTRAINT chk_cv_has_candidate_label
        CHECK (
            (document_type = 'CV' AND candidate_label IS NOT NULL)
            OR document_type != 'CV'
        )
);

-- Indexes for performance
CREATE INDEX idx_document_type ON document_metadata(document_type);
CREATE INDEX idx_cigref_profile_name ON document_metadata(cigref_profile_name)
    WHERE cigref_profile_name IS NOT NULL;
CREATE INDEX idx_candidate_label ON document_metadata(candidate_label)
    WHERE candidate_label IS NOT NULL;
CREATE INDEX idx_upload_timestamp ON document_metadata(upload_timestamp DESC);
CREATE INDEX idx_metadata_gin ON document_metadata USING gin(metadata);

-- ============================================================================
-- Apache AGE Graph Setup
-- ============================================================================

SELECT create_graph('lightrag_graph');
```

## LightRAG Auto-Created Tables (Reference Only)

These tables are created automatically by LightRAG storage adapters:

```sql
-- PGKVStorage
CREATE TABLE lightrag_kv (
    key TEXT PRIMARY KEY,
    value JSONB,
    namespace TEXT DEFAULT 'default',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- PGVectorStorage
CREATE TABLE lightrag_vectors (
    id TEXT PRIMARY KEY,
    vector VECTOR(1024) NOT NULL,
    content TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_vector_hnsw ON lightrag_vectors
    USING hnsw (vector vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- PGDocStatusStorage
CREATE TABLE lightrag_doc_status (
    document_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    error_message TEXT,
    chunks_created INTEGER DEFAULT 0,
    entities_extracted INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---
