# Story 4.1: LightRAG Retrieval Mode Strategy Implementation

> 📋 **Epic**: [Epic 4: Hybrid Retrieval & Match Explanation](../epics/epic-4.md)
> 📋 **Architecture**: [Core Workflows - Hybrid Retrieval Query](../architecture/core-workflows.md#workflow-3-hybrid-retrieval-query), [Components - LightRAG Service](../architecture/components.md#component-2-lightrag-service)

## User Story

**As a** developer,
**I want** the MCP server to intelligently select LightRAG retrieval modes based on query characteristics,
**so that** simple queries run fast (naive/local) while complex multi-criteria queries leverage full hybrid capabilities.

## Acceptance Criteria

1. MCP server implements retrieval mode selection logic:
   - **Naive mode**: Single-entity queries (e.g., "Who has Python experience?") → fast vector-only search
   - **Local mode**: Profile or specific competency queries (e.g., "Cloud Architects") → entity-focused with immediate graph neighborhood
   - **Global mode**: Broad domain queries (e.g., "All infrastructure specialists") → graph traversal across domains
   - **Hybrid mode**: Complex multi-criteria queries (e.g., "Senior DevOps with AWS, Terraform, and leadership") → combines vector similarity + graph relationships

2. Mode selection algorithm considers:
   - Number of criteria in query (1 criterion → naive/local, 3+ criteria → hybrid)
   - Query scope (specific entity vs. broad domain)
   - User-specified mode override if exposed as optional parameter

3. MCP tool implementations updated to pass selected mode to LightRAG API

4. Test suite validates mode selection:
   - 5 test queries per mode type (20 total)
   - Verify correct mode selected based on query characteristics
   - Document rationale for each selection

5. Performance comparison documented:
   - Response time for same query across all 4 modes
   - Quality comparison (are results different? which mode gives best results?)
   - Findings in `/docs/retrieval-modes-analysis.md`

6. Configuration option added to `.env` for default mode or mode selection strategy (allow tuning)

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 8-12 hours
- **Dependencies**: Story 3.8 (Basic Candidate Detail View)
- **Blocks**: Story 4.2, Story 4.3

## QA

- **QA Assessment**: [Story 4.1 Assessment](../qa/assessments/story-4.1-assessment.md)
- **QA Gate**: [Story 4.1 Gate](../qa/gates/story-4.1-gate.md)

---

**Navigation:**
- ← Previous: [Story 3.8](story-3.8.md)
- → Next: [Story 4.2](story-4.2.md)
- ↑ Epic: [Epic 4](../epics/epic-4.md)
