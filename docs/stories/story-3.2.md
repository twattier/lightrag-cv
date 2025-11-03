# Story 3.2: Core Search Tool - Profile Match Query

> 📋 **Epic**: [Epic 3: MCP Server & OpenWebUI Integration](../epics/epic-3.md)
> 📋 **Architecture**: [Components - MCP Server](../architecture/components.md#component-3-mcp-server), [Core Workflows](../architecture/core-workflows.md#workflow-3-hybrid-retrieval-query)

## User Story

**As a** recruiter,
**I want** to query for candidates matching a specific CIGREF profile,
**so that** I can find candidates aligned to standardized job requirements.

## Acceptance Criteria

1. MCP tool implemented: `search_by_profile`
   - Parameters:
     - `profile_name` (string): CIGREF profile name (e.g., "Cloud Architect")
     - `experience_years` (optional number): Minimum years of experience
     - `top_k` (optional number, default 5): Number of results to return
   - Returns: List of candidate matches with IDs and brief summaries

2. Tool implementation:
   - Translates parameters to LightRAG API query
   - Uses LightRAG's "local" or "hybrid" retrieval mode (targets entities directly related to profile)
   - Calls LightRAG REST API with constructed query
   - Parses response and formats as structured JSON for MCP client

3. Tool exposed via MCP protocol (appears in tool discovery list)

4. Manual test validates functionality:
   - Invoke `search_by_profile` with profile_name="Cloud Architect"
   - Returns 5 relevant candidates from knowledge base
   - Response includes candidate IDs and summary text

5. Error handling for edge cases:
   - Profile name not found → returns helpful error message
   - No candidates match criteria → returns empty list with explanation
   - LightRAG API timeout → returns error with retry guidance

6. Tool schema documented with parameter descriptions and example invocations

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 6-8 hours
- **Dependencies**: Story 3.1 (MCP Server Scaffold and Protocol Implementation)
- **Blocks**: Story 3.4, Story 3.5

## QA

- **QA Assessment**: [Story 3.2 Assessment](../qa/assessments/story-3.2-assessment.md)
- **QA Gate**: [Story 3.2 Gate](../qa/gates/story-3.2-gate.md)

---

**Navigation:**
- ← Previous: [Story 3.1](story-3.1.md)
- → Next: [Story 3.3](story-3.3.md)
- ↑ Epic: [Epic 3](../epics/epic-3.md)
