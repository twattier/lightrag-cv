# Story 2.5: LightRAG Knowledge Base Ingestion - CIGREF Profiles

> 📋 **Epic**: [Epic 2: Document Processing Pipeline](../epics/epic-2.md)
> 📋 **Architecture**: [Components - LightRAG Service](../architecture/components.md#component-2-lightrag-service), [Core Workflows](../architecture/core-workflows.md), [Database Schema](../architecture/database-schema.md)

## User Story

**As a** developer,
**I want** parsed CIGREF profile data ingested into LightRAG with vector embeddings and graph relationships,
**so that** the system understands IT profile structure and competencies.

## Acceptance Criteria

1. Ingestion script or process that:
   - Reads parsed CIGREF data (`/data/cigref/cigref-parsed.json`)
   - Submits to LightRAG API for document ingestion
   - Handles chunking if CIGREF content exceeds context limits
   - Waits for embedding generation completion

2. LightRAG successfully generates:
   - Vector embeddings for CIGREF content chunks (stored in PGVectorStorage)
   - Knowledge graph entities (profiles, missions, skills, deliverables, domains)
   - Relationships between entities (e.g., "Cloud Architect" → "requires" → "AWS expertise")

3. PostgreSQL validation queries confirm data storage:
   ```sql
   -- Check vector storage
   SELECT COUNT(*) FROM [vector_table];

   -- Check graph storage (AGE)
   SELECT * FROM cypher('[graph_name]', $$
     MATCH (n) RETURN n LIMIT 10
   $$) as (n agtype);
   ```

4. Graph coverage assessed: Can manually identify at least 5 profiles, 10 skills, 5 missions in stored graph

5. Simple LightRAG query test (via API or CLI):
   - Query: "What are the skills required for Cloud Architect?"
   - Response includes relevant CIGREF profile information
   - Demonstrates retrieval is working

6. Ingestion process documented in `/docs/ingestion-process.md` with runtime metrics (time taken, number of entities created)

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 8-12 hours
- **Dependencies**: Story 2.2 (CIGREF English PDF Parsing and Quality Validation), Story 1.3 (LightRAG Server Integration)
- **Blocks**: Story 2.6, Story 2.7

## QA

- **QA Assessment**: [Story 2.5 Assessment](../qa/assessments/story-2.5-assessment.md)
- **QA Gate**: [Story 2.5 Gate](../qa/gates/story-2.5-gate.md)

---

**Navigation:**
- ← Previous: [Story 2.4](story-2.4.md)
- → Next: [Story 2.6](story-2.6.md)
- ↑ Epic: [Epic 2](../epics/epic-2.md)
