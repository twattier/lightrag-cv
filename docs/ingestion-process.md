# CIGREF Ingestion Process

## Overview

This document describes the process for ingesting CIGREF IT profile data into the LightRAG knowledge base for hybrid vector-graph retrieval.

## Prerequisites

- CIGREF parsed data ready at `/data/cigref/cigref-parsed.json`
- LightRAG service running at `localhost:9621`
- PostgreSQL database running at `localhost:5434`
- Ollama running with required models:
  - `bge-m3:latest` (embeddings)
  - `qwen3:8b` (generation)

## Ingestion Script

The ingestion script is located at `scripts/ingest-cigref.py`.

### Features

1. **Data Validation**: Validates CIGREF parsed JSON structure
2. **Metadata Insertion**: Inserts document metadata into PostgreSQL `document_metadata` table
3. **Chunk Submission**: Submits 681 chunks to LightRAG ingestion API
4. **Status Monitoring**: Polls LightRAG processing status until completion
5. **Vector Validation**: Verifies vector embeddings in PostgreSQL
6. **Graph Validation**: Verifies knowledge graph entities and relationships
7. **Query Testing**: Tests retrieval with sample query
8. **Validation Report**: Generates comprehensive validation report

### Usage

```bash
# Install dependencies
pip install -r scripts/requirements.txt

# Run ingestion
python3 scripts/ingest-cigref.py
```

### Expected Processing Time

- Embedding generation: ~11-23 minutes (681 chunks × 1-2s each)
- Entity extraction: ~2-5 minutes
- Graph construction: ~1-2 minutes
- **Total**: 15-30 minutes

## Data Structure

### Input: CIGREF Parsed JSON

```json
{
  "document_metadata": {
    "document_id": "fa9b2be6-074e-47a3-8454-85e56f121a56",
    "document_type": "CIGREF_PROFILE",
    "source_filename": "Cigref_Nomenclature_des_profils_metiers_SI_EN_2024.pdf",
    "format": "PDF",
    "page_count": 0,
    "tables_extracted": 253,
    "total_chunks": 681
  },
  "chunks": [
    {
      "chunk_id": "chunk_0",
      "content": "...",
      "chunk_type": "text",
      "metadata": {
        "domain_id": "1",
        "domain": "APPLICATION LIFE CYCLE",
        "job_profile_id": "1.1",
        "job_profile": "APPLICATION ARCHITECT",
        "section": "MISSION",
        "page": 10,
        "token_count": 98
      }
    }
  ]
}
```

### Hierarchical Metadata

Each chunk includes structured metadata for entity recognition:

- `domain_id` + `domain`: IT domain (e.g., "2" = "PROJECT MANAGEMENT")
- `job_profile_id` + `job_profile`: IT profile (e.g., "2.6" = "PRODUCT OWNER")
- `section`: Profile section (MISSION, Skills, etc.)

This enables LightRAG to:
1. Identify domain entities
2. Recognize job profile entities
3. Extract skill/competency entities with context
4. Build relationships (e.g., "PRODUCT OWNER part_of PROJECT MANAGEMENT")

## Database Schema

### document_metadata Table

Created in PostgreSQL for POC tracking:

```sql
CREATE TABLE document_metadata (
    document_id TEXT PRIMARY KEY,
    document_type TEXT NOT NULL CHECK (document_type IN ('CIGREF_PROFILE', 'CV')),
    source_filename TEXT NOT NULL,
    file_format TEXT CHECK (file_format IN ('PDF', 'DOCX')),
    upload_timestamp TIMESTAMP DEFAULT NOW(),
    cigref_profile_name TEXT,
    candidate_label TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);
```

### LightRAG Auto-Created Tables

LightRAG creates the following tables automatically:

- `lightrag_vdb_chunks`: Vector embeddings storage (PGVectorStorage)
- `lightrag_doc_status`: Document processing status (PGDocStatusStorage)
- `lightrag_full_entities`: Entity storage with JSONB arrays (document-centric)
- `lightrag_full_relations`: Relationship storage with JSONB arrays (document-centric)
- `lightrag_vdb_entity`: Entity vector embeddings
- `lightrag_vdb_relation`: Relationship vector embeddings
- Additional KV storage tables (doc_chunks, doc_full, entity_chunks, relation_chunks)

### Understanding LightRAG's Document-Centric Storage

**IMPORTANT**: LightRAG uses a **document-centric JSONB storage model** for entities and relationships, NOT individual entity rows.

#### Entity Storage Structure

The `lightrag_full_entities` table stores entities as JSONB arrays per document:

```sql
CREATE TABLE lightrag_full_entities (
    id VARCHAR(255),              -- Document ID (e.g., doc-abc123...)
    workspace VARCHAR(255),        -- Namespace (default)
    entity_names JSONB,            -- Array: ["Entity1", "Entity2", ...]
    count INTEGER,                 -- Number of entities in this document
    create_time TIMESTAMP,
    update_time TIMESTAMP,
    PRIMARY KEY (workspace, id)
);
```

**Example Record**:
```json
{
  "id": "doc-c02e3c37b8d17c4cdbe4a45ddc862165",
  "entity_names": [
    "Product Owner",
    "Data Architect",
    "DevOps",
    "Product Manager",
    "Agile Projects"
  ],
  "count": 5
}
```

This means:
- ✅ **1 row** = 1 document containing multiple entities
- ❌ **NOT** 1 row per entity
- To get **237 entities** from **18 documents**, you'll see **18 rows** in the table

#### Relationship Storage Structure

The `lightrag_full_relations` table follows the same pattern:

```sql
CREATE TABLE lightrag_full_relations (
    id VARCHAR(255),              -- Document ID
    workspace VARCHAR(255),        -- Namespace
    relation_pairs JSONB,          -- Array of {src, tgt, description} objects
    count INTEGER,                 -- Number of relationships
    create_time TIMESTAMP,
    update_time TIMESTAMP,
    PRIMARY KEY (workspace, id)
);
```

**Example Record**:
```json
{
  "id": "doc-c02e3c37b8d17c4cdbe4a45ddc862165",
  "relation_pairs": [
    {
      "src": "Product Owner",
      "tgt": "Agile Projects",
      "description": "manages"
    },
    {
      "src": "Data Architect",
      "tgt": "Database Systems",
      "description": "designs"
    }
  ],
  "count": 2
}
```

#### How to Query Individual Entities

To expand JSONB arrays into individual entity rows, use `jsonb_array_elements_text()`:

```sql
-- Get all entities as individual rows (not document groups)
SELECT
    id as document_id,
    jsonb_array_elements_text(entity_names) as entity_name,
    workspace
FROM lightrag_full_entities
WHERE workspace = 'default';

-- Count total individual entities (not document groups)
SELECT SUM(count) as total_entities
FROM lightrag_full_entities
WHERE workspace = 'default';
```

#### How to Query Individual Relationships

Similarly, use `jsonb_array_elements()` for relationships:

```sql
-- Get all relationships as individual rows
SELECT
    id as document_id,
    rel_pair->>'src' as source_entity,
    rel_pair->>'tgt' as target_entity,
    rel_pair->>'description' as relationship_type
FROM lightrag_full_relations,
     jsonb_array_elements(relation_pairs) as rel_pair
WHERE workspace = 'default';

-- Count total individual relationships
SELECT SUM(count) as total_relationships
FROM lightrag_full_relations
WHERE workspace = 'default';
```

#### SQL Helper Script

A comprehensive SQL helper script is available at `scripts/query-entities.sql` with pre-built queries for:
- Viewing entities as individual records
- Counting total entities/relationships
- Finding most frequent entities
- Searching for specific entities
- Analyzing document processing status

Run it with:
```bash
docker exec -i lightrag-cv-postgres psql -U lightrag -d lightrag_cv < scripts/query-entities.sql
```

## Validation Queries

### Check Chunk Storage

```sql
-- Count chunks created for CIGREF ingestion
SELECT COUNT(*) FROM lightrag_vdb_chunks
WHERE workspace = 'default'
  AND file_path LIKE 'cigref:%';
```

Expected: 681 chunks (one per source chunk with metadata)

### Check Entity Extraction (Document-Centric View)

```sql
-- Count entity document groups
SELECT COUNT(*) as entity_documents,
       SUM(count) as total_entities
FROM lightrag_full_entities
WHERE workspace = 'default';
```

Expected: Multiple document groups containing 100+ total entities

### Check Entity Extraction (Individual Entity View)

```sql
-- View actual entities as individual rows
SELECT
    jsonb_array_elements_text(entity_names) as entity_name,
    COUNT(*) as document_count
FROM lightrag_full_entities
WHERE workspace = 'default'
GROUP BY entity_name
ORDER BY document_count DESC
LIMIT 20;
```

Expected: IT job profiles (Product Owner, Data Architect, etc.), domains, skills

### Check Relationship Extraction

```sql
-- Count relationships
SELECT COUNT(*) as relationship_documents,
       SUM(count) as total_relationships
FROM lightrag_full_relations
WHERE workspace = 'default';

-- View sample relationships
SELECT
    rel_pair->>'src' as source,
    rel_pair->>'tgt' as target,
    rel_pair->>'description' as relationship_type
FROM lightrag_full_relations,
     jsonb_array_elements(relation_pairs) as rel_pair
WHERE workspace = 'default'
LIMIT 20;
```

Expected: Relationships between profiles, skills, domains (e.g., "requires", "manages", "part_of")

### Check Document Processing Status

```sql
-- Overall status summary
SELECT
    status,
    COUNT(*) as count
FROM lightrag_doc_status
WHERE workspace = 'default'
GROUP BY status;
```

Expected statuses: `processed`, `processing`, or `pending`

## API Endpoints

### POST /documents

Submit document for ingestion:

```bash
curl -X POST http://localhost:9621/documents \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "cigref_2024_en",
    "chunks": [...],
    "metadata": {
      "type": "CIGREF_PROFILE",
      "filename": "cigref-parsed.json"
    }
  }'
```

Response:
```json
{
  "document_id": "cigref_2024_en",
  "status": "completed",
  "message": "Document ingested successfully"
}
```

### GET /documents/{document_id}/status

Check processing status:

```bash
curl http://localhost:9621/documents/cigref_2024_en/status
```

Response:
```json
{
  "document_id": "cigref_2024_en",
  "status": "completed",
  "chunks_created": 681,
  "entities_extracted": 150,
  "error": null
}
```

### POST /query

Query the knowledge base:

```bash
curl -X POST http://localhost:9621/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the skills required for Cloud Architect?",
    "mode": "hybrid",
    "top_k": 5,
    "filters": {"document_type": "CIGREF_PROFILE"}
  }'
```

Response:
```json
{
  "results": [
    {
      "document_id": "cigref_2024_en",
      "content": "...",
      "score": 0.85,
      "metadata": {...},
      "entities": ["AWS", "Azure", "Kubernetes"],
      "graph_paths": [...]
    }
  ],
  "retrieval_mode_used": "hybrid",
  "query_time_ms": 450
}
```

## Troubleshooting

### LightRAG Service Errors

If you encounter 500 errors from LightRAG:

1. Check service logs:
   ```bash
   docker logs lightrag-cv-lightrag --tail 50
   ```

2. Verify PostgreSQL connection:
   ```bash
   curl http://localhost:9621/health
   ```

3. Ensure Ollama models are available:
   ```bash
   curl http://localhost:11434/api/tags
   ```

### PostgreSQL Connection Issues

If ingestion fails with database errors:

1. Verify PostgreSQL is running:
   ```bash
   docker exec lightrag-cv-postgres psql -U lightrag -d lightrag_cv -c "\dt"
   ```

2. Check extensions are installed:
   ```bash
   docker exec lightrag-cv-postgres psql -U lightrag -d lightrag_cv -c "\dx"
   ```

   Expected: `pgvector`, `age`

3. Verify graph exists:
   ```bash
   docker exec lightrag-cv-postgres psql -U lightrag -d lightrag_cv -c \
     "SELECT * FROM ag_catalog.ag_graph;"
   ```

   Expected: `lightrag_graph`

## Implementation Status

### Completed

✅ Task 1: CIGREF ingestion script created (`scripts/ingest-cigref.py`)
✅ Task 2: document_metadata table implemented and tested
✅ Task 9: Ingestion documentation created

### In Progress

⚠️ Tasks 3-8: Pending LightRAG PostgreSQL storage initialization fix

The ingestion script has been fully implemented with all required functionality, including:
- Async HTTP client using httpx
- PostgreSQL integration using psycopg3
- Comprehensive validation logic
- Status monitoring with retry logic
- Graph and vector validation queries
- Automated test query execution
- Validation report generation

However, the LightRAG service requires configuration fixes for proper PostgreSQL storage initialization before ingestion can complete successfully.

### Next Steps

1. Fix LightRAG service PostgreSQL storage configuration
2. Run complete ingestion workflow
3. Validate all acceptance criteria
4. Generate final validation report

## References

- [Story 2.5](../stories/story-2.5.md)
- [LightRAG Documentation](https://github.com/HKUDS/LightRAG)
- [Apache AGE Documentation](https://age.apache.org/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
