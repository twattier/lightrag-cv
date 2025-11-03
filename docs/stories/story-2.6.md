# Story 2.6: LightRAG Knowledge Base Ingestion - CVs

> 📋 **Epic**: [Epic 2: Document Processing Pipeline](../epics/epic-2.md)
> 📋 **Architecture**: [Components - LightRAG Service](../architecture/components.md#component-2-lightrag-service), [Core Workflows](../architecture/core-workflows.md), [Database Schema](../architecture/database-schema.md)

## User Story

**As a** developer,
**I want** parsed test CVs ingested into LightRAG alongside CIGREF profiles,
**so that** the unified knowledge base contains both profile references and candidate data.

## Acceptance Criteria

1. Batch ingestion script processes all validated parsed CVs from `/data/cvs/parsed/`

2. Each CV ingested with metadata tagging:
   - Filename/ID
   - Document type: "CV"
   - Any manual tags from `cvs-manifest.json` (role, experience level)

3. LightRAG generates embeddings and extracts entities from CVs:
   - Skills mentioned
   - Companies/employers
   - Technologies used
   - Roles/titles held
   - Education and certifications

4. Graph relationships created linking CV entities to CIGREF entities where applicable (e.g., CV mentions "Kubernetes" → links to "container orchestration" competency)

5. PostgreSQL validation confirms CV data persisted:
   - Vector count increased by expected amount
   - Graph contains CV-specific entities (can query for candidate skills)

6. Test query validates CV retrieval:
   - Query: "Find candidates with Python experience"
   - Response returns relevant CVs that mention Python
   - Demonstrates CV content is searchable

7. Ingestion metrics documented: Total CVs ingested, processing time, entity count, any failed ingestions

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 8-12 hours
- **Dependencies**: Story 2.4 (CV Parsing and Quality Validation), Story 2.5 (LightRAG Knowledge Base Ingestion - CIGREF Profiles)
- **Blocks**: Story 2.7

## QA

- **QA Assessment**: [Story 2.6 Assessment](../qa/assessments/story-2.6-assessment.md)
- **QA Gate**: [Story 2.6 Gate](../qa/gates/story-2.6-gate.md)

---

**Navigation:**
- ← Previous: [Story 2.5](story-2.5.md)
- → Next: [Story 2.7](story-2.7.md)
- ↑ Epic: [Epic 2](../epics/epic-2.md)
