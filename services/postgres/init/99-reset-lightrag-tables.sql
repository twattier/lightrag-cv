-- ============================================================================
-- Reset LightRAG Tables for Vector Dimension Change
-- ============================================================================
--
-- This script drops all LightRAG internal tables to allow them to be
-- recreated with a new vector dimension (e.g., changing from 1024 to 1536
-- when switching from bge-m3 to OpenAI embeddings).
--
-- IMPORTANT: This will DELETE all LightRAG data (documents, entities,
-- relations, embeddings). The document_metadata table is preserved.
--
-- Usage:
--   docker exec -i lightrag-cv-postgres psql -U lightrag -d lightrag_cv < services/postgres/init/99-reset-lightrag-tables.sql
-- ============================================================================

\c lightrag_cv

-- Drop all LightRAG tables (order matters due to potential dependencies)
DROP TABLE IF EXISTS lightrag_vdb_chunks CASCADE;
DROP TABLE IF EXISTS lightrag_vdb_entity CASCADE;
DROP TABLE IF EXISTS lightrag_vdb_relation CASCADE;
DROP TABLE IF EXISTS lightrag_doc_chunks CASCADE;
DROP TABLE IF EXISTS lightrag_doc_full CASCADE;
DROP TABLE IF EXISTS lightrag_doc_status CASCADE;
DROP TABLE IF EXISTS lightrag_entity_chunks CASCADE;
DROP TABLE IF EXISTS lightrag_full_entities CASCADE;
DROP TABLE IF EXISTS lightrag_full_relations CASCADE;
DROP TABLE IF EXISTS lightrag_relation_chunks CASCADE;
DROP TABLE IF EXISTS lightrag_llm_cache CASCADE;

-- Verify only document_metadata remains
\dt

-- Show completion message
SELECT 'LightRAG tables dropped successfully. Restart LightRAG service to recreate with new vector dimension.' AS status;
