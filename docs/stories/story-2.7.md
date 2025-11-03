# Story 2.7: Document Processing Performance Baseline

> 📋 **Epic**: [Epic 2: Document Processing Pipeline](../epics/epic-2.md)
> 📋 **Architecture**: [Components - Docling Service](../architecture/components.md#component-1-docling-service), [Components - LightRAG Service](../architecture/components.md#component-2-lightrag-service)

## User Story

**As a** product manager,
**I want** baseline performance metrics for document processing,
**so that** I can assess whether throughput meets POC requirements and understand GPU acceleration impact.

## Acceptance Criteria

1. Performance test measures:
   - Docling parsing time per CV (average, min, max) in CPU-only mode
   - Docling parsing time per CV with GPU acceleration (if available)
   - LightRAG ingestion time per document (parsing → embedding → storage)
   - End-to-end time: Upload CV → Available for search

2. Test conducted on sample of 10 CVs with varied characteristics (1-page, 2-page, 3-page resumes)

3. Results documented in `/docs/performance-baseline.md`:
   - CPU-only throughput: X CVs per minute
   - GPU-accelerated throughput: Y CVs per minute (if tested)
   - LightRAG embedding generation time
   - Total pipeline throughput assessment

4. Comparison to requirements:
   - Target: 1-2 CVs per minute acceptable for POC
   - Assessment: "Meets/Exceeds/Below expectations"

5. If performance below expectations, document mitigation strategies for Phase 2 (batch processing, queue system, model optimization)

6. Recommendations for production optimization noted (e.g., "GPU acceleration provides 3x improvement, recommended for scale")

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 4-6 hours
- **Dependencies**: Story 2.6 (LightRAG Knowledge Base Ingestion - CVs)
- **Blocks**: None

## QA

- **QA Assessment**: [Story 2.7 Assessment](../qa/assessments/story-2.7-assessment.md)
- **QA Gate**: [Story 2.7 Gate](../qa/gates/story-2.7-gate.md)

---

**Navigation:**
- ← Previous: [Story 2.6](story-2.6.md)
- → Next: [Story 3.1](story-3.1.md)
- ↑ Epic: [Epic 2](../epics/epic-2.md)
