-- ================================================================================
-- LightRAG Entity & Relationship Query Helpers
-- ================================================================================
--
-- LightRAG stores entities and relationships in a document-centric JSONB format.
-- This script provides helper queries to view data as individual records.
--
-- Usage: psql -U lightrag -d lightrag_cv -f scripts/query-entities.sql
-- Or from host: docker exec -i lightrag-cv-postgres psql -U lightrag -d lightrag_cv < scripts/query-entities.sql
--
-- ================================================================================

-- Set output formatting
\pset border 2
\pset format wrapped
\x auto

-- ================================================================================
-- 1. ENTITY QUERIES
-- ================================================================================

-- Show all entities as individual rows (expanding JSONB arrays)
-- This query converts document-centric storage to entity-centric view
\echo ''
\echo '================================================================================'
\echo '1.1 All Entities (Individual Records)'
\echo '================================================================================'
SELECT
    id as document_id,
    jsonb_array_elements_text(entity_names) as entity_name,
    workspace,
    create_time,
    update_time
FROM lightrag_full_entities
WHERE workspace = 'default'
ORDER BY update_time DESC, document_id, entity_name
LIMIT 50;

-- Count total entities (not just document groups)
\echo ''
\echo '================================================================================'
\echo '1.2 Entity Count Summary'
\echo '================================================================================'
SELECT
    COUNT(*) as total_documents,
    SUM(count) as total_entities,
    ROUND(AVG(count), 2) as avg_entities_per_doc,
    MIN(count) as min_entities,
    MAX(count) as max_entities
FROM lightrag_full_entities
WHERE workspace = 'default';

-- Top entities by frequency (how many documents mention them)
\echo ''
\echo '================================================================================'
\echo '1.3 Most Frequent Entities (Across Documents)'
\echo '================================================================================'
SELECT
    entity_name,
    COUNT(*) as document_count,
    array_agg(DISTINCT document_id) as in_documents
FROM (
    SELECT
        id as document_id,
        jsonb_array_elements_text(entity_names) as entity_name
    FROM lightrag_full_entities
    WHERE workspace = 'default'
) entities
GROUP BY entity_name
ORDER BY document_count DESC, entity_name
LIMIT 20;

-- Entities by document (with count)
\echo ''
\echo '================================================================================'
\echo '1.4 Entities Per Document (Summary)'
\echo '================================================================================'
SELECT
    id as document_id,
    count as entity_count,
    LEFT(entity_names::TEXT, 100) || '...' as entity_preview,
    TO_CHAR(update_time, 'YYYY-MM-DD HH24:MI:SS') as updated
FROM lightrag_full_entities
WHERE workspace = 'default'
ORDER BY count DESC, update_time DESC
LIMIT 20;

-- ================================================================================
-- 2. RELATIONSHIP QUERIES
-- ================================================================================

-- Show all relationships as individual rows (expanding JSONB arrays)
\echo ''
\echo '================================================================================'
\echo '2.1 All Relationships (Individual Records)'
\echo '================================================================================'
SELECT
    id as document_id,
    rel_pair->>'src' as source_entity,
    rel_pair->>'tgt' as target_entity,
    rel_pair->>'description' as relationship_description,
    workspace,
    create_time,
    update_time
FROM lightrag_full_relations,
     jsonb_array_elements(relation_pairs) as rel_pair
WHERE workspace = 'default'
ORDER BY update_time DESC, document_id
LIMIT 50;

-- Count total relationships (not just document groups)
\echo ''
\echo '================================================================================'
\echo '2.2 Relationship Count Summary'
\echo '================================================================================'
SELECT
    COUNT(*) as total_documents,
    SUM(count) as total_relationships,
    ROUND(AVG(count), 2) as avg_relationships_per_doc,
    MIN(count) as min_relationships,
    MAX(count) as max_relationships
FROM lightrag_full_relations
WHERE workspace = 'default';

-- Relationships by document (with count)
\echo ''
\echo '================================================================================'
\echo '2.3 Relationships Per Document (Summary)'
\echo '================================================================================'
SELECT
    id as document_id,
    count as relationship_count,
    TO_CHAR(update_time, 'YYYY-MM-DD HH24:MI:SS') as updated
FROM lightrag_full_relations
WHERE workspace = 'default'
ORDER BY count DESC, update_time DESC
LIMIT 20;

-- Most common relationship types (grouped by description keywords)
\echo ''
\echo '================================================================================'
\echo '2.4 Most Common Relationship Types'
\echo '================================================================================'
SELECT
    rel_pair->>'description' as relationship_type,
    COUNT(*) as occurrence_count
FROM lightrag_full_relations,
     jsonb_array_elements(relation_pairs) as rel_pair
WHERE workspace = 'default'
GROUP BY rel_pair->>'description'
ORDER BY occurrence_count DESC
LIMIT 20;

-- ================================================================================
-- 3. CHUNK QUERIES
-- ================================================================================

-- Show all chunks with metadata
\echo ''
\echo '================================================================================'
\echo '3.1 All Chunks (with file_path and content preview)'
\echo '================================================================================'
SELECT
    id,
    workspace,
    file_path,
    chunk_order_index,
    tokens,
    LEFT(content, 100) || '...' as content_preview,
    TO_CHAR(create_time, 'YYYY-MM-DD HH24:MI:SS') as created
FROM lightrag_vdb_chunks
WHERE workspace = 'default'
ORDER BY create_time DESC, chunk_order_index
LIMIT 20;

-- Chunks by file_path (aggregated)
\echo ''
\echo '================================================================================'
\echo '3.2 Chunks Per File Path'
\echo '================================================================================'
SELECT
    file_path,
    COUNT(*) as chunk_count,
    SUM(tokens) as total_tokens,
    MIN(TO_CHAR(create_time, 'YYYY-MM-DD HH24:MI:SS')) as first_created,
    MAX(TO_CHAR(update_time, 'YYYY-MM-DD HH24:MI:SS')) as last_updated
FROM lightrag_vdb_chunks
WHERE workspace = 'default'
GROUP BY file_path
ORDER BY chunk_count DESC, file_path;

-- ================================================================================
-- 4. DOCUMENT STATUS QUERIES
-- ================================================================================

-- Document processing status summary
\echo ''
\echo '================================================================================'
\echo '4.1 Document Processing Status'
\echo '================================================================================'
SELECT
    id as document_id,
    status,
    chunks_count,
    content_length,
    LEFT(content_summary, 80) as summary,
    file_path,
    TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') as created,
    TO_CHAR(updated_at, 'YYYY-MM-DD HH24:MI:SS') as updated,
    CASE
        WHEN error_msg IS NOT NULL THEN LEFT(error_msg, 100)
        ELSE NULL
    END as error_preview
FROM lightrag_doc_status
WHERE workspace = 'default'
ORDER BY updated_at DESC
LIMIT 20;

-- Status counts
\echo ''
\echo '================================================================================'
\echo '4.2 Status Summary'
\echo '================================================================================'
SELECT
    status,
    COUNT(*) as document_count,
    SUM(chunks_count) as total_chunks,
    SUM(content_length) as total_content_length
FROM lightrag_doc_status
WHERE workspace = 'default'
GROUP BY status
ORDER BY document_count DESC;

-- ================================================================================
-- 5. COMBINED VIEWS
-- ================================================================================

-- Documents with entity and relationship counts
\echo ''
\echo '================================================================================'
\echo '5.1 Documents with Entity & Relationship Counts'
\echo '================================================================================'
SELECT
    d.id as document_id,
    d.status,
    d.chunks_count,
    COALESCE(e.count, 0) as entity_count,
    COALESCE(r.count, 0) as relationship_count,
    LEFT(d.file_path, 40) as file_path,
    TO_CHAR(d.updated_at, 'YYYY-MM-DD HH24:MI:SS') as updated
FROM lightrag_doc_status d
LEFT JOIN lightrag_full_entities e ON d.id = e.id AND d.workspace = e.workspace
LEFT JOIN lightrag_full_relations r ON d.id = r.id AND d.workspace = r.workspace
WHERE d.workspace = 'default'
ORDER BY d.updated_at DESC
LIMIT 20;

-- Overall system statistics
\echo ''
\echo '================================================================================'
\echo '5.2 Overall System Statistics'
\echo '================================================================================'
SELECT
    'Documents' as metric,
    COUNT(*)::TEXT as count
FROM lightrag_doc_status
WHERE workspace = 'default'
UNION ALL
SELECT
    'Documents (Processed)' as metric,
    COUNT(*)::TEXT as count
FROM lightrag_doc_status
WHERE workspace = 'default' AND status = 'processed'
UNION ALL
SELECT
    'Chunks' as metric,
    COUNT(*)::TEXT as count
FROM lightrag_vdb_chunks
WHERE workspace = 'default'
UNION ALL
SELECT
    'Entity Groups (Documents)' as metric,
    COUNT(*)::TEXT as count
FROM lightrag_full_entities
WHERE workspace = 'default'
UNION ALL
SELECT
    'Total Entities' as metric,
    SUM(count)::TEXT as count
FROM lightrag_full_entities
WHERE workspace = 'default'
UNION ALL
SELECT
    'Relationship Groups (Documents)' as metric,
    COUNT(*)::TEXT as count
FROM lightrag_full_relations
WHERE workspace = 'default'
UNION ALL
SELECT
    'Total Relationships' as metric,
    SUM(count)::TEXT as count
FROM lightrag_full_relations
WHERE workspace = 'default';

-- ================================================================================
-- 6. SEARCH & FILTER EXAMPLES
-- ================================================================================

-- Search for specific entity
\echo ''
\echo '================================================================================'
\echo '6.1 Search Example: Find Documents Mentioning "Data Scientist"'
\echo '================================================================================'
SELECT
    id as document_id,
    count as total_entities,
    workspace,
    TO_CHAR(update_time, 'YYYY-MM-DD HH24:MI:SS') as updated
FROM lightrag_full_entities
WHERE workspace = 'default'
  AND entity_names @> '["Data Scientist"]'::jsonb
ORDER BY update_time DESC;

-- Find relationships involving a specific entity
\echo ''
\echo '================================================================================'
\echo '6.2 Search Example: Find Relationships Involving "Product Owner"'
\echo '================================================================================'
SELECT
    id as document_id,
    rel_pair->>'src' as source_entity,
    rel_pair->>'tgt' as target_entity,
    rel_pair->>'description' as relationship_description
FROM lightrag_full_relations,
     jsonb_array_elements(relation_pairs) as rel_pair
WHERE workspace = 'default'
  AND (
      rel_pair->>'src' ILIKE '%Product Owner%'
      OR rel_pair->>'tgt' ILIKE '%Product Owner%'
  )
ORDER BY document_id;

\echo ''
\echo '================================================================================'
\echo 'Query Complete!'
\echo '================================================================================'
\echo ''
\echo 'Notes:'
\echo '  - Entity/Relation "count" columns show the number of unique items per document'
\echo '  - JSONB arrays store multiple entities/relations in a single row'
\echo '  - Use jsonb_array_elements() to expand arrays into individual rows'
\echo '  - Modify queries above for your specific analysis needs'
\echo ''
