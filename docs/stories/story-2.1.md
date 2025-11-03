# Story 2.1: Docling REST API Implementation

> 📋 **Epic**: [Epic 2: Document Processing Pipeline](../epics/epic-2.md)
> 📋 **Architecture**: [Components - Docling Service](../architecture/components.md#component-1-docling-service), [Infrastructure and Deployment](../architecture/infrastructure-and-deployment.md)

## User Story

**As a** developer,
**I want** Docling service exposing REST endpoints for document parsing,
**so that** other services can submit PDFs/DOCX files and receive structured parsed content.

## Acceptance Criteria

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

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 8-12 hours
- **Dependencies**: Story 1.5 (Docling Service Scaffold)
- **Blocks**: Story 2.2, Story 2.3

## QA

- **QA Assessment**: [Story 2.1 Assessment](../qa/assessments/story-2.1-assessment.md)
- **QA Gate**: [Story 2.1 Gate](../qa/gates/story-2.1-gate.md)

---

**Navigation:**
- ← Previous: [Story 1.7](story-1.7.md)
- → Next: [Story 2.2](story-2.2.md)
- ↑ Epic: [Epic 2](../epics/epic-2.md)
