# Epic 2: Document Processing Pipeline

> 📋 **Architecture References**:
> - [Components - Docling Service](../architecture/components.md#component-1-docling-service) - REST API design
> - [Components - LightRAG Service](../architecture/components.md#component-2-lightrag-service) - Ingestion API
> - [Core Workflows](../architecture/core-workflows.md) - Ingestion workflows
> - [Data Models](../architecture/data-models.md) - Document metadata

**Epic Goal**: Implement Docling service REST API for parsing CIGREF profiles and CVs, validate extraction quality on test documents, integrate with LightRAG for knowledge base ingestion, and successfully load the CIGREF English 2024 nomenclature plus a test set of 20-30 IT CVs with verified content quality.

## Stories

1. ✅ [Story 2.1: Docling REST API Implementation](../stories/story-2.1.md) - **Done** (2025-11-03)
2. ✅ [Story 2.2: CIGREF English PDF Parsing and Quality Validation](../stories/story-2.2.md) - **Done** (2025-11-04)
3. [Story 2.3: CV Dataset Acquisition and Preprocessing](../stories/story-2.3.md)
4. [Story 2.4: CV Parsing and Quality Validation](../stories/story-2.4.md)
5. 🔄 [Story 2.5: LightRAG Knowledge Base Ingestion - CIGREF Profiles](../stories/story-2.5.md) - **Developed - Ready for QA Review** (Batch Processing Running)
6. [Story 2.6: LightRAG Knowledge Base Ingestion - CVs](../stories/story-2.6.md)
7. [Story 2.7: Document Processing Performance Baseline](../stories/story-2.7.md)

## Epic Status

- **Status**: In Progress
- **Story Count**: 7
- **Completed**: 2/7 (29%)
- **In QA Review**: 1/7 (14%)
- **Current Story**: Story 2.5 (CIGREF Ingestion - Batch Processing Running), Story 2.3 (CV Dataset Acquisition)
- **Dependencies**: Epic 1 (Foundation & Core Infrastructure) ✅ Complete
- **Blocked By**: None

## Progress Summary

- ✅ **Story 2.1 Complete** - Docling REST API fully implemented with:
  - FastAPI service with `/parse` and `/health` endpoints
  - HybridChunker integration with BAAI/bge-m3 tokenizer
  - Comprehensive error handling and validation
  - 6 comprehensive integration tests
  - 100% standards compliance
  - QA Gate: PASS (100/100)
  - Manual validation confirmed

- ✅ **Story 2.2 Complete** - CIGREF PDF parsing with hierarchical metadata enrichment:
  - 681 chunks extracted from CIGREF English 2024 edition (4.8 MB PDF)
  - 100/100 quality score (exceeds 85% NFR3 threshold)
  - 253 tables and 41 job profiles successfully extracted
  - **NEW:** Hierarchical metadata enrichment via pdfplumber
  - 93.69% chunk coverage with domain/profile context tree
  - 9 unique domains and 41 unique job profiles identified
  - Complete metadata structure: domain_id, domain, job_profile_id, job_profile, section
  - LightRAG-ready JSON output (750 KB) prepared for Story 2.5 ingestion
  - GPU processing: 142 seconds (vs. 12-14 min CPU) = 5-6x speedup

- 🔄 **Story 2.5 Developed - Ready for QA Review** - CIGREF ingestion with batch processing:
  - Phase 1: 92 chunks ingested with vector embeddings (1024-dim using bge-m3)
  - PostgreSQL storage operational: All backends initialized
  - HNSW index created for fast vector similarity search
  - Phase 2: Implemented batch processing to overcome LLM timeout issue
  - Created `scripts/ingest-cigref-batched.py` for processing in smaller batches
  - **Batch processing currently running** - Entity and relationship extraction in progress
  - Pending validation post-batch completion: Entity count, relationship count, graph queries, retrieval tests

---

**Related Documentation:**
- [PRD Epic 2 (Full)](../prd/epic-2-document-processing-pipeline.md)
- [Epic List](../prd/epic-list.md)
