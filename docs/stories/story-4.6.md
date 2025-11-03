# Story 4.6: Query Performance Optimization and Testing

> 📋 **Epic**: [Epic 4: Hybrid Retrieval & Match Explanation](../epics/epic-4.md)
> 📋 **Architecture**: [Core Workflows - Hybrid Retrieval Query](../architecture/core-workflows.md#workflow-3-hybrid-retrieval-query), [Database Schema](../architecture/database-schema.md)

## User Story

**As a** developer,
**I want** to optimize query performance across all retrieval modes,
**so that** response times meet the <10 second POC target for typical queries.

## Acceptance Criteria

1. Performance test suite created with 20 representative queries:
   - 5 simple (single skill, naive mode)
   - 5 moderate (profile match, local mode)
   - 5 complex (multi-criteria, hybrid mode)
   - 5 very complex (broad domain + filters, global mode)

2. Each query executed 3 times, response time measured end-to-end:
   - OpenWebUI input → MCP tool invocation → LightRAG retrieval → PostgreSQL queries → Result return
   - Record: p50, p95, p99 response times

3. Performance results documented in `/docs/performance-results.md`:
   - All queries: Comparison to <10s POC target
   - Slowest queries identified with bottleneck analysis (LightRAG retrieval? PostgreSQL query? Embedding generation? Graph traversal?)

4. If queries exceed 10s target:
   - Optimization attempts: Reduce context size, limit graph depth, tune PostgreSQL indices, adjust LightRAG parameters
   - Document optimizations applied and impact
   - If still slow, acceptable for POC with Phase 2 optimization plan

5. GPU acceleration impact measured (if available):
   - Compare query times with/without GPU for Docling processing
   - Embeddings generation time (likely not GPU-accelerated via Ollama unless configured)

6. Performance recommendations for Phase 2:
   - Caching strategies
   - Index optimization
   - Parallel query execution
   - Model optimization or quantization

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 8-12 hours
- **Dependencies**: Story 4.5 (Confidence Scoring and Ranking Refinement)
- **Blocks**: Story 4.7

## QA

- **QA Assessment**: [Story 4.6 Assessment](../qa/assessments/story-4.6-assessment.md)
- **QA Gate**: [Story 4.6 Gate](../qa/gates/story-4.6-gate.md)

---

**Navigation:**
- ← Previous: [Story 4.5](story-4.5.md)
- → Next: [Story 4.7](story-4.7.md)
- ↑ Epic: [Epic 4](../epics/epic-4.md)
