# Story 3.3: Core Search Tool - Multi-Criteria Skill Search

> 📋 **Epic**: [Epic 3: MCP Server & OpenWebUI Integration](../epics/epic-3.md)
> 📋 **Architecture**: [Components - MCP Server](../architecture/components.md#component-3-mcp-server), [Core Workflows](../architecture/core-workflows.md#workflow-3-hybrid-retrieval-query)

## User Story

**As a** recruiter,
**I want** to query for candidates by specific skills and technologies,
**so that** I can find candidates with precise technical expertise regardless of profile classification.

## Acceptance Criteria

1. MCP tool implemented: `search_by_skills`
   - Parameters:
     - `required_skills` (array of strings): Must-have skills (e.g., ["Kubernetes", "AWS"])
     - `preferred_skills` (optional array of strings): Nice-to-have skills
     - `experience_level` (optional enum: "junior", "mid", "senior")
     - `top_k` (optional number, default 5): Number of results
   - Returns: List of candidate matches with skill overlap details

2. Tool implementation:
   - Constructs natural language query from structured parameters (e.g., "Find candidates with Kubernetes and AWS experience at senior level")
   - Calls LightRAG API with appropriate retrieval mode (likely "hybrid" for multi-criteria)
   - Post-processes results to highlight skill matches
   - Ranks candidates by skill coverage

3. Tool handles semantic similarity:
   - Query for "Kubernetes" should surface candidates mentioning "K8s" or "container orchestration"
   - Relies on LightRAG's embedding-based semantic search

4. Manual test validates:
   - Query: required_skills=["Python", "Machine Learning"], experience_level="senior"
   - Returns candidates with relevant skills
   - Results show which required/preferred skills each candidate possesses

5. Empty results handled gracefully (e.g., "No candidates found with required skill combination. Try broadening criteria.")

6. Tool registered in MCP protocol and documented with usage examples

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 6-8 hours
- **Dependencies**: Story 3.1 (MCP Server Scaffold and Protocol Implementation)
- **Blocks**: Story 3.4, Story 3.5

## QA

- **QA Assessment**: [Story 3.3 Assessment](../qa/assessments/story-3.3-assessment.md)
- **QA Gate**: [Story 3.3 Gate](../qa/gates/story-3.3-gate.md)

---

**Navigation:**
- ← Previous: [Story 3.2](story-3.2.md)
- → Next: [Story 3.4](story-3.4.md)
- ↑ Epic: [Epic 3](../epics/epic-3.md)
