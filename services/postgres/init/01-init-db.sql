-- ============================================================================
-- LightRAG-CV Database Initialization
-- ============================================================================

-- Create database only if it doesn't exist
SELECT 'CREATE DATABASE lightrag_cv
    ENCODING ''UTF8''
    TEMPLATE template0
    LC_COLLATE ''en_US.utf8''
    LC_CTYPE ''en_US.utf8'''
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'lightrag_cv')\gexec

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
CREATE INDEX IF NOT EXISTS idx_document_type ON document_metadata(document_type);
CREATE INDEX IF NOT EXISTS idx_cigref_profile_name ON document_metadata(cigref_profile_name)
    WHERE cigref_profile_name IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_candidate_label ON document_metadata(candidate_label)
    WHERE candidate_label IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_upload_timestamp ON document_metadata(upload_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_metadata_gin ON document_metadata USING gin(metadata);

-- ============================================================================
-- Apache AGE Graph Setup
-- ============================================================================

-- Create graph only if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'lightrag_graph'
    ) THEN
        PERFORM create_graph('lightrag_graph');
    END IF;
END
$$;
