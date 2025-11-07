# Epic 2: Document Processing Pipeline

> 🎯 **Status**: ✅ **COMPLETE**
>
> 🎯 **Development Artifacts**: [Epic 2 Card](../epics/epic-2.md) | [Stories 2.1-2.6](../stories/README.md#epic-2-document-processing-pipeline-6-stories)
>

> 📋 **Architecture References**:
> - [Components - Docling Service](../architecture/components.md#component-1-docling-service) - REST API design
> - [Components - LightRAG Service](../architecture/components.md#component-2-lightrag-service) - Ingestion API
> - [Core Workflows](../architecture/core-workflows.md) - Ingestion workflows
> - [Data Models](../architecture/data-models.md) - Document metadata

**Epic Goal**: Implement Docling service REST API for parsing CIGREF profiles and CVs, validate extraction quality on test documents, integrate with LightRAG for knowledge base ingestion, and successfully load the CIGREF English 2024 nomenclature plus a test set of 20-30 IT CVs with verified content quality.

## Story 2.1: Docling REST API Implementation

**As a** developer,
**I want** Docling service exposing REST endpoints for document parsing,
**so that** other services can submit PDFs/DOCX files and receive structured parsed content.

### Acceptance Criteria

1. Docling service implements REST API with endpoints:
   - `POST /parse` - accepts multipart file upload (PDF or DOCX), returns parsed JSON
   - `GET /health` - returns service health status
   - `GET /status/{job_id}` - optional async processing status (if needed for large docs)

2. `/parse` endpoint uses Docling's `HybridChunker` for intelligent content segmentation

3. Response format includes:
   - Parsed text content organized by document structure (sections, paragraphs)
   - Metadata (document type, page count, processing time)
   - Extracted entities if available (tables, lists, headings)
   - Chunk boundaries and metadata for downstream embedding

4. Error handling returns appropriate HTTP status codes:
   - 400 for invalid file format
   - 413 for file too large
   - 500 for parsing failures with error details

5. Service handles both CPU and GPU modes based on Docker Compose profile (GPU accelerates processing, CPU is functional fallback)

6. API documentation added to `/docs/docling-api.md` with example requests/responses

## Story 2.2: CIGREF English PDF Parsing and Quality Validation

**As a** product manager,
**I want** the CIGREF IT profile nomenclature PDF parsed with validated extraction quality,
**so that** I can confirm structured profile data (missions, skills, deliverables) is accurately captured.

### Acceptance Criteria

1. CIGREF English 2024 edition PDF downloaded and placed in `/data/cigref/` directory

2. Test script or manual process submits CIGREF PDF to Docling `/parse` endpoint

3. Parsed output is manually inspected and validated for:
   - All IT profile domains identified (e.g., Business, Development, Production, Support)
   - Individual profiles extracted (e.g., Cloud Architect, DevOps Engineer, Data Scientist)
   - Structured sections recognized: Missions, Activities, Deliverables, Performance Indicators, Skills
   - Tables and lists properly parsed (not mangled)
   - French/English mixed content handled appropriately (English edition focus)

4. Quality validation results documented in `/docs/cigref-parsing-validation.md`:
   - Sample profile showing successful extraction
   - Known issues or limitations
   - Assessment: "Meets 85%+ extraction quality threshold" (NFR3) or notes gaps

5. If quality is below threshold, document remediation approach (manual pre-processing, Docling parameter tuning, or supplemental manual data entry)

6. Parsed CIGREF content saved to `/data/cigref/cigref-parsed.json` or similar format for LightRAG ingestion

## Story 2.3: CV Dataset Acquisition and Preprocessing

**As a** developer,
**I want** a curated test set of 20-30 English IT resumes from Hugging Face datasets,
**so that** I have representative data for knowledge base population and testing.

### Acceptance Criteria

1. Download and sample CVs from specified Hugging Face datasets:
   - `gigswar/cv_files`
   - `d4rk3r/resumes-raw-pdf`

2. Filter for English language IT/technical resumes (software, infrastructure, data, security roles)

3. Curate final test set of 20-30 CVs with diverse characteristics:
   - Multiple experience levels (junior, mid, senior)
   - Various IT domains (development, infrastructure, data, security, management)
   - Different formats (PDF, DOCX if available)
   - Different lengths (1-3 pages typical)

4. CVs organized in `/data/cvs/test-set/` with basic metadata file (`cvs-manifest.json`) listing:
   - Filename
   - Inferred role/domain (manual tagging)
   - Experience level estimate
   - File format

5. Sample of 3-5 CVs manually reviewed for quality and relevance (not gibberish, contains actual technical content)

6. Documentation in `/docs/test-data.md` describes dataset composition and filtering criteria

## Story 2.4: CV Parsing and Quality Validation

**As a** product manager,
**I want** test CVs parsed through Docling with validated extraction quality,
**so that** I can confirm critical resume information (skills, experience, education) is accurately captured.

### Acceptance Criteria

1. Test script processes all CVs in `/data/cvs/test-set/` through Docling `/parse` endpoint

2. Parsed CV outputs saved to `/data/cvs/parsed/` directory (one JSON per CV)

3. Sample of 5 CVs manually inspected for extraction quality:
   - Skills/technologies identified (e.g., "Python", "Kubernetes", "AWS")
   - Work experience sections recognized (companies, roles, dates, descriptions)
   - Education extracted
   - Projects/accomplishments captured
   - Contact info and personal data handled appropriately

4. Quality metrics documented in `/docs/cv-parsing-validation.md`:
   - Percentage of CVs successfully parsed (target: 90%+ per NFR2)
   - Common extraction issues (e.g., multi-column layouts, graphics-heavy resumes)
   - Assessment of readiness for LightRAG ingestion

5. If quality below threshold (90%), document mitigation:
   - Remove problematic CVs from test set
   - Adjust Docling parameters
   - Note as limitation in POC findings

6. Validated parsed CVs ready for LightRAG ingestion (Story 2.5)

## Story 2.5: LightRAG Knowledge Base Ingestion - CIGREF Profiles

**As a** developer,
**I want** parsed CIGREF profile data ingested into LightRAG with vector embeddings and graph relationships,
**so that** the system understands IT profile structure and competencies.

### Acceptance Criteria

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

## Story 2.6: LightRAG Knowledge Base Ingestion - CVs

**As a** developer,
**I want** parsed test CVs ingested into LightRAG alongside CIGREF profiles,
**so that** the unified knowledge base contains both profile references and candidate data.

### Acceptance Criteria

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

---

## Epic Completion

**Epic 2 is now complete.** All stories (2.1-2.6) have been successfully delivered:
- ✅ Docling REST API implemented and validated
- ✅ CIGREF profiles parsed and quality validated
- ✅ CV dataset acquired and preprocessed
- ✅ CV parsing quality validated
- ✅ CIGREF profiles ingested into LightRAG
- ✅ CV dataset ingested into LightRAG and validated

**Note**: Story 2.7 (Performance Baseline) was cancelled and will be addressed separately if needed in future phases.
