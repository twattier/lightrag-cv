# Story 4.2: Graph-Based Relationship Extraction for Match Ranking

> 📋 **Epic**: [Epic 4: Hybrid Retrieval & Match Explanation](../epics/epic-4.md)
> 📋 **Architecture**: [Data Models](../architecture/data-models.md), [Core Workflows - Hybrid Retrieval Query](../architecture/core-workflows.md#workflow-3-hybrid-retrieval-query), [Database Schema](../architecture/database-schema.md)

## User Story

**As a** developer,
**I want** candidate ranking enhanced with graph relationship insights,
**so that** matches reflect not just keyword overlap but semantic and structural relationships between candidate experience and profile requirements.

## Acceptance Criteria

1. When retrieving candidates, MCP server queries LightRAG for graph relationships:
   - Candidate skill nodes → competency nodes → CIGREF mission nodes
   - Candidate experience → domain entities → profile requirement entities
   - Example: Candidate mentions "Kubernetes" → graph shows "Kubernetes" relates to "container orchestration" → relates to "Cloud Infrastructure" competency → relates to "Cloud Architect" missions

2. Graph relationship scoring incorporated into ranking:
   - Direct relationships (1-hop) score higher than indirect (2-3 hops)
   - Multiple relationship paths increase confidence
   - Rare/specialized relationships weighted appropriately (domain-specific)

3. LightRAG's graph storage (PGGraphStorage via Apache AGE) queried using Cypher-like queries or LightRAG's graph API

4. Test validates graph-enhanced ranking:
   - Compare ranking with pure vector similarity vs. graph-enhanced hybrid
   - Identify cases where graph relationships surface better candidates (e.g., semantic similarity finds "SRE" when query is "DevOps Engineer")
   - Document 3-5 examples showing graph value

5. Graph queries optimized for performance:
   - Response time remains <10s for POC (graph traversal doesn't bottleneck)
   - If slow, limit graph depth (e.g., max 3 hops) or cache common paths

6. Graph relationship data included in tool responses for use in match explanations (Story 4.3)

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 10-14 hours
- **Dependencies**: Story 4.1 (LightRAG Retrieval Mode Strategy Implementation)
- **Blocks**: Story 4.3, Story 4.5

## QA

- **QA Assessment**: [Story 4.2 Assessment](../qa/assessments/story-4.2-assessment.md)
- **QA Gate**: [Story 4.2 Gate](../qa/gates/story-4.2-gate.md)

---

**Navigation:**
- ← Previous: [Story 4.1](story-4.1.md)
- → Next: [Story 4.3](story-4.3.md)
- ↑ Epic: [Epic 4](../epics/epic-4.md)
